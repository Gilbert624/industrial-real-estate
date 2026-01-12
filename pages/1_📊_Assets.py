"""
Asset Portfolio Management Page
Displays and manages all industrial real estate assets

Developer: Gilbert - Brisbane, QLD
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from sqlalchemy import func, and_, or_
from config.theme import generate_css
from config.i18n import t, get_current_language

# Import database models
try:
    from models.database import (
        DatabaseManager, Asset, Project, RentalIncome,
        AssetType, AssetStatus
    )
    DB_AVAILABLE = True
except ImportError as e:
    st.error(f"⚠️ Database models not found: {e}")
    DB_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Asset Portfolio",
    page_icon="📊",
    layout="wide"
)

# 应用专业主题
st.markdown(generate_css('light'), unsafe_allow_html=True)


@st.cache_resource
def get_database():
    """Get cached database connection"""
    try:
        return DatabaseManager('sqlite:///industrial_real_estate.db')
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None


def get_filter_options(session):
    """
    Get unique values for filters from database
    
    Returns:
        dict: Filter options for region, type, and status
    """
    try:
        # Get unique regions
        regions = session.query(Asset.region).distinct().all()
        region_list = ['All'] + [r[0] for r in regions if r[0]]
        
        # Get all asset types from enum
        type_list = ['All'] + [t.value for t in AssetType]
        
        # Get all asset statuses from enum
        status_list = ['All'] + [s.value for s in AssetStatus]
        
        return {
            'regions': region_list,
            'types': type_list,
            'statuses': status_list
        }
    except Exception as e:
        st.error(f"Error loading filter options: {e}")
        return {
            'regions': ['All'],
            'types': ['All'],
            'statuses': ['All']
        }


def apply_filters(query, region, asset_type, status):
    """
    Apply filters to asset query
    
    Args:
        query: SQLAlchemy query object
        region: Selected region filter
        asset_type: Selected asset type filter
        status: Selected status filter
        
    Returns:
        Filtered query object
    """
    if region != 'All':
        query = query.filter(Asset.region == region)
    
    if asset_type != 'All':
        # Convert string back to enum
        for at in AssetType:
            if at.value == asset_type:
                query = query.filter(Asset.asset_type == at)
                break
    
    if status != 'All':
        # Convert string back to enum
        for s in AssetStatus:
            if s.value == status:
                query = query.filter(Asset.status == s)
                break
    
    return query


def calculate_metrics(assets):
    """
    Calculate key portfolio metrics
    
    Args:
        assets: List of Asset objects
        
    Returns:
        dict: Portfolio metrics
    """
    if not assets:
        return {
            'total_assets': 0,
            'total_valuation': 0,
            'avg_valuation': 0
        }
    
    total_assets = len(assets)
    total_valuation = sum(float(a.current_valuation or 0) for a in assets)
    avg_valuation = total_valuation / total_assets if total_assets > 0 else 0
    
    return {
        'total_assets': total_assets,
        'total_valuation': total_valuation,
        'avg_valuation': avg_valuation
    }


def format_asset_dataframe(assets):
    """
    Convert assets to formatted DataFrame for display
    
    Args:
        assets: List of Asset objects
        
    Returns:
        DataFrame: Formatted asset data
    """
    if not assets:
        return pd.DataFrame()
    
    data = []
    for asset in assets:
        data.append({
            'Asset ID': asset.id,
            'Project Name': asset.name,
            'Address': f"{asset.address_line1}, {asset.suburb}",
            'Region': asset.region,
            'Type': asset.asset_type.value.replace('_', ' ').title(),
            'Land Area (㎡)': f"{asset.land_area_sqm:,.0f}" if asset.land_area_sqm else 'N/A',
            'Building Area (㎡)': f"{asset.building_area_sqm:,.0f}" if asset.building_area_sqm else 'N/A',
            'Current Valuation': f"${asset.current_valuation:,.2f}" if asset.current_valuation else 'N/A',
            'Status': asset.status.value.replace('_', ' ').title(),
            'Purchase Date': asset.purchase_date.strftime('%d %b %Y') if asset.purchase_date else 'N/A'
        })
    
    return pd.DataFrame(data)


def display_asset_details(asset, session):
    """
    Display detailed information about an asset in an expander
    
    Args:
        asset: Asset object
        session: Database session
    """
    with st.expander(f"📋 View Details: {asset.name}"):
        # Create columns for layout
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📍 Location")
            st.write(f"**Address:** {asset.address_line1}")
            if asset.address_line2:
                st.write(f"{asset.address_line2}")
            st.write(f"**Suburb:** {asset.suburb}")
            st.write(f"**Postcode:** {asset.postcode}")
            st.write(f"**Region:** {asset.region}")
            st.write(f"**Council:** {asset.council or 'N/A'}")
        
        with col2:
            st.markdown("#### 📐 Physical Characteristics")
            st.write(f"**Type:** {asset.asset_type.value.replace('_', ' ').title()}")
            st.write(f"**Status:** {asset.status.value.replace('_', ' ').title()}")
            st.write(f"**Land Area:** {asset.land_area_sqm:,.0f} ㎡" if asset.land_area_sqm else "Land Area: N/A")
            st.write(f"**Building Area:** {asset.building_area_sqm:,.0f} ㎡" if asset.building_area_sqm else "Building Area: N/A")
            if asset.warehouse_area_sqm:
                st.write(f"**Warehouse:** {asset.warehouse_area_sqm:,.0f} ㎡")
            if asset.office_area_sqm:
                st.write(f"**Office:** {asset.office_area_sqm:,.0f} ㎡")
            if asset.clear_height_meters:
                st.write(f"**Clear Height:** {asset.clear_height_meters} m")
        
        with col3:
            st.markdown("#### 💰 Financial Information")
            if asset.purchase_price:
                st.write(f"**Purchase Price:** ${asset.purchase_price:,.2f}")
            if asset.purchase_date:
                st.write(f"**Purchase Date:** {asset.purchase_date.strftime('%d %b %Y')}")
            if asset.current_valuation:
                st.write(f"**Current Valuation:** ${asset.current_valuation:,.2f}")
            if asset.valuation_date:
                st.write(f"**Valuation Date:** {asset.valuation_date.strftime('%d %b %Y')}")
            
            # Calculate appreciation if both values exist
            if asset.purchase_price and asset.current_valuation:
                appreciation = asset.current_valuation - asset.purchase_price
                appreciation_pct = (appreciation / asset.purchase_price) * 100
                st.write(f"**Appreciation:** ${appreciation:,.2f} ({appreciation_pct:+.1f}%)")
        
        # Technical specifications
        if any([asset.power_capacity_kva, asset.loading_docks, asset.car_parking_spaces]):
            st.markdown("#### 🔧 Technical Specifications")
            specs_col1, specs_col2, specs_col3 = st.columns(3)
            
            with specs_col1:
                if asset.power_capacity_kva:
                    st.write(f"⚡ **Power:** {asset.power_capacity_kva} kVA")
            with specs_col2:
                if asset.loading_docks:
                    st.write(f"🚛 **Loading Docks:** {asset.loading_docks}")
            with specs_col3:
                if asset.car_parking_spaces:
                    st.write(f"🅿️ **Parking Spaces:** {asset.car_parking_spaces}")
        
        # Zoning information
        if asset.zoning:
            st.markdown("#### 📋 Zoning & Compliance")
            st.write(f"**Zoning:** {asset.zoning}")
        
        # Description
        if asset.description:
            st.markdown("#### 📝 Description")
            st.write(asset.description)
        
        # Related projects
        try:
            projects = session.query(Project).filter_by(asset_id=asset.id).all()
            if projects:
                st.markdown("#### 🏗️ Associated Projects")
                for proj in projects:
                    st.write(f"- **{proj.project_name}** ({proj.status.value})")
                    if proj.total_budget:
                        st.write(f"  Budget: ${proj.total_budget:,.2f}")
        except Exception as e:
            st.error(f"Error loading projects: {e}")
        
        # Rental information
        try:
            rentals = session.query(RentalIncome).filter_by(
                asset_id=asset.id, 
                is_active=True
            ).all()
            
            if rentals:
                st.markdown("#### 🏢 Active Leases")
                for rental in rentals:
                    st.write(f"- **Tenant:** {rental.tenant_name}")
                    st.write(f"  Monthly Rent: ${rental.monthly_rent:,.2f}")
                    st.write(f"  Lease End: {rental.lease_end_date.strftime('%d %b %Y')}")
        except Exception as e:
            st.error(f"Error loading rental info: {e}")
        
        # Notes
        if asset.notes:
            st.markdown("#### 📌 Notes")
            st.info(asset.notes)


def main():
    """Main application function"""
    
    st.title(f"📊 {t('assets.title')}")
    st.markdown(f"### {t('assets.subtitle')}")
    
    if not DB_AVAILABLE:
        st.error("⚠️ Database models are not available. Please check your installation.")
        return
    
    db = get_database()
    if not db:
        st.error("⚠️ Could not connect to database.")
        return
    
    session = db.get_session()
    
    try:
        # Sidebar filters
        st.sidebar.markdown(f"### 🔍 {t('assets.filters')}")
        
        # Get filter options
        filter_options = get_filter_options(session)
        
        # Region filter
        selected_region = st.sidebar.selectbox(
            t('assets.region'),
            options=filter_options['regions'],
            index=0
        )
        
        # Asset type filter
        selected_type = st.sidebar.selectbox(
            t('assets.asset_type'),
            options=filter_options['types'],
            index=0
        )
        
        # Status filter
        selected_status = st.sidebar.selectbox(
            t('common.status'),
            options=filter_options['statuses'],
            index=0
        )
        
        st.sidebar.markdown("---")
        
        # Add refresh button
        if st.sidebar.button(f"🔄 {t('assets.refresh_data')}"):
            st.cache_resource.clear()
            st.rerun()
        
        st.sidebar.markdown("---")
        
        # Asset Management Form
        st.sidebar.header(t('assets.asset_management'))
        
        # Initialize session state for edit mode
        if 'edit_asset_id' not in st.session_state:
            st.session_state.edit_asset_id = None
        
        # Determine mode
        mode = t('assets.edit_asset') if st.session_state.edit_asset_id else t('assets.add_new_asset')
        st.sidebar.subheader(mode)
        
        # Load asset data if in edit mode
        asset = None
        if st.session_state.edit_asset_id:
            asset = db.get_asset_by_id(st.session_state.edit_asset_id, session)
            if not asset:
                st.sidebar.warning("Asset not found!")
                st.session_state.edit_asset_id = None
        
        # Form
        with st.sidebar.form("asset_form"):
            # Basic information
            name = st.text_input(
                f"{t('assets.project_name')}*",
                value=asset.name if asset else "",
                help="Name of the asset/project"
            )
            
            address = st.text_area(
                f"{t('assets.address')}*",
                value=asset.address_line1 if asset else "",
                help="Street address"
            )
            
            # Region and Type
            col1, col2 = st.columns(2)
            with col1:
                region_options = ["Brisbane", "Sunshine Coast"]
                region_index = region_options.index(asset.region) if asset and asset.region in region_options else 0
                region = st.selectbox(f"{t('assets.region')}*", region_options, index=region_index)
                
                asset_type_options = [t('assets.asset_types.industrial_warehouse'), t('assets.asset_types.land'), t('assets.asset_types.mixed_use')]
                asset_type_map = {
                    t('assets.asset_types.industrial_warehouse'): "warehouse",
                    t('assets.asset_types.land'): "land",
                    t('assets.asset_types.mixed_use'): "mixed_use"
                }
                # Find current type index
                current_type_display = None
                if asset:
                    asset_type_value = asset.asset_type.value if asset.asset_type else None
                    for display, value in asset_type_map.items():
                        if value == asset_type_value:
                            current_type_display = display
                            break
                type_index = asset_type_options.index(current_type_display) if current_type_display in asset_type_options else 0
                asset_type = st.selectbox(f"{t('common.type')}*", asset_type_options, index=type_index)
            
            with col2:
                status_options = [t('assets.status_options.operating'), t('assets.status_options.under_development'), t('assets.status_options.planned')]
                status_map = {
                    t('assets.status_options.operating'): "active",
                    t('assets.status_options.under_development'): "under_development",
                    t('assets.status_options.planned'): "under_development"
                }
                # Find current status index
                current_status_display = None
                if asset:
                    status_value = asset.status.value if asset.status else None
                    for display, value in status_map.items():
                        if value == status_value:
                            current_status_display = display
                            break
                status_index = status_options.index(current_status_display) if current_status_display in status_options else 0
                status = st.selectbox(f"{t('common.status')}*", status_options, index=status_index)
                
                acquisition_date = st.date_input(
                    t('assets.acquisition_date'),
                    value=asset.purchase_date if asset and asset.purchase_date else date.today(),
                    help="Date of acquisition"
                )
            
            # Area and Valuation
            col3, col4 = st.columns(2)
            with col3:
                land_area = st.number_input(
                    f"{t('assets.land_area')}*",
                    min_value=0.0,
                    value=float(asset.land_area_sqm) if asset and asset.land_area_sqm else 0.0,
                    step=1.0,
                    format="%.0f"
                )
                building_area = st.number_input(
                    f"{t('assets.building_area')}*",
                    min_value=0.0,
                    value=float(asset.building_area_sqm) if asset and asset.building_area_sqm else 0.0,
                    step=1.0,
                    format="%.0f"
                )
            
            with col4:
                valuation = st.number_input(
                    f"{t('assets.current_valuation')} (AUD)*",
                    min_value=0.0,
                    value=float(asset.current_valuation) if asset and asset.current_valuation else 0.0,
                    step=1000.0,
                    format="%.2f"
                )
            
            description = st.text_area(
                t('common.description'),
                value=asset.description if asset and asset.description else "",
                help="Additional description or notes"
            )
            
            # Form buttons
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submitted = st.form_submit_button(f"💾 {t('common.save')}", use_container_width=True)
            with col_btn2:
                cancelled = st.form_submit_button(f"❌ {t('common.cancel')}", use_container_width=True)
            
            if submitted:
                # Validation
                errors = []
                if not name or not name.strip():
                    errors.append(f"{t('assets.project_name')} {t('validation.required')}")
                if not address or not address.strip():
                    errors.append(f"{t('assets.address')} {t('validation.required')}")
                if land_area <= 0:
                    errors.append(f"{t('assets.land_area')} {t('validation.positive_number')}")
                if valuation <= 0:
                    errors.append(f"{t('assets.current_valuation')} {t('validation.positive_number')}")
                
                if errors:
                    for error in errors:
                        st.sidebar.error(error)
                else:
                    # Prepare asset data
                    asset_data = {
                        "name": name.strip(),
                        "address": address.strip(),
                        "region": region,
                        "asset_type": asset_type,
                        "status": status,
                        "land_area_sqm": land_area,
                        "building_area_sqm": building_area if building_area > 0 else None,
                        "current_valuation": valuation,
                        "acquisition_date": acquisition_date,
                        "description": description.strip() if description else None,
                        # Set required fields for address
                        "suburb": region,  # Use region as suburb for now
                        "state": "Queensland",
                        "postcode": "0000"  # Default postcode
                    }
                    
                    try:
                        if st.session_state.edit_asset_id:
                            db.update_asset(st.session_state.edit_asset_id, asset_data, session)
                            st.sidebar.success(f"✅ {t('assets.asset_saved')}")
                        else:
                            db.add_asset(asset_data, session)
                            st.sidebar.success(f"✅ {t('assets.asset_saved')}")
                        
                        st.session_state.edit_asset_id = None
                        st.rerun()
                    except Exception as e:
                        st.sidebar.error(f"❌ {t('messages.error_occurred')}: {str(e)}")
            
            if cancelled:
                st.session_state.edit_asset_id = None
                st.rerun()
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Last Updated:**")
        st.sidebar.markdown(f"{datetime.now().strftime('%d %b %Y, %H:%M')}")
        
        # Query assets with filters
        query = session.query(Asset)
        query = apply_filters(query, selected_region, selected_type, selected_status)
        assets = query.all()
        
        # Calculate metrics
        metrics = calculate_metrics(assets)
        
        # Display key metrics
        st.markdown('<div style="margin-bottom: 2rem;">', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"### 📈 {t('home.portfolio_overview')}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label=t('home.total_assets'),
                value=f"{metrics['total_assets']}",
                help="Total number of assets matching current filters"
            )
        
        with col2:
            valuation_millions = metrics['total_valuation'] / 1_000_000
            st.metric(
                label=t('assets.total_portfolio_value'),
                value=f"${valuation_millions:.2f}M AUD",
                help="Sum of current valuations for filtered assets"
            )
        
        with col3:
            avg_millions = metrics['avg_valuation'] / 1_000_000
            st.metric(
                label=t('assets.average_asset_value'),
                value=f"${avg_millions:.2f}M AUD",
                help="Average valuation per asset"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Display assets table
        st.markdown(f"### 🏢 {t('assets.title')}")
        
        if not assets:
            st.info(t('messages.no_results'))
        else:
            # Create DataFrame
            df = format_asset_dataframe(assets)
            
            # Display info message
            st.info(f"📊 Showing {len(assets)} asset(s) | Click on any asset below to view detailed information")
            
            # Display main table (without Asset ID column for cleaner view)
            display_df = df.drop(columns=['Asset ID'])
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'Project Name': st.column_config.TextColumn(
                        'Project Name',
                        width='large',
                        help='Click expand below to view details'
                    ),
                    'Address': st.column_config.TextColumn(
                        'Address',
                        width='large'
                    ),
                    'Region': st.column_config.TextColumn(
                        'Region',
                        width='small'
                    ),
                    'Type': st.column_config.TextColumn(
                        'Type',
                        width='medium'
                    ),
                    'Land Area (㎡)': st.column_config.TextColumn(
                        'Land Area (㎡)',
                        width='small'
                    ),
                    'Building Area (㎡)': st.column_config.TextColumn(
                        'Building Area (㎡)',
                        width='small'
                    ),
                    'Current Valuation': st.column_config.TextColumn(
                        'Current Valuation',
                        width='medium'
                    ),
                    'Status': st.column_config.TextColumn(
                        'Status',
                        width='medium'
                    ),
                    'Purchase Date': st.column_config.TextColumn(
                        'Purchase Date',
                        width='small'
                    )
                }
            )
            
            st.markdown("---")
            
            # Asset Operations (Edit/Delete buttons)
            st.markdown("### ⚙️ Asset Operations")
            st.info(f"📊 Showing {len(assets)} asset(s) | Use buttons below to {t('common.edit')} or {t('common.delete')} assets")
            
            # Initialize delete confirmation state
            for asset in assets:
                if f'confirm_delete_{asset.id}' not in st.session_state:
                    st.session_state[f'confirm_delete_{asset.id}'] = False
            
            # Display operations for each asset
            for asset in assets:
                col1, col2, col3 = st.columns([6, 1, 1])
                
                with col1:
                    st.write(f"**{asset.name}** - {asset.region} | Valuation: ${asset.current_valuation:,.2f}" if asset.current_valuation else f"**{asset.name}** - {asset.region}")
                
                with col2:
                    if st.button(f"✏️ {t('common.edit')}", key=f"edit_{asset.id}", help="Edit this asset", use_container_width=True):
                        st.session_state.edit_asset_id = asset.id
                        st.rerun()
                
                with col3:
                    if st.button(f"🗑️ {t('common.delete')}", key=f"delete_{asset.id}", help="Delete this asset", use_container_width=True):
                        st.session_state[f'confirm_delete_{asset.id}'] = True
                        st.rerun()
            
            # Delete confirmation dialogs
            for asset in assets:
                if st.session_state.get(f'confirm_delete_{asset.id}', False):
                    st.warning(f"⚠️ {t('assets.delete_confirm')}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✅ {t('common.yes')}, {t('common.delete')}", key=f"confirm_yes_{asset.id}", type="primary", use_container_width=True):
                            try:
                                success = db.delete_asset(asset.id, session)
                                if success:
                                    st.success(f"✅ {t('assets.asset_deleted')}")
                                    del st.session_state[f'confirm_delete_{asset.id}']
                                    st.rerun()
                                else:
                                    st.error("Asset not found")
                            except Exception as e:
                                st.error(f"❌ {t('messages.error_occurred')}: {str(e)}")
                    
                    with col2:
                        if st.button(f"❌ {t('common.cancel')}", key=f"confirm_no_{asset.id}", use_container_width=True):
                            del st.session_state[f'confirm_delete_{asset.id}']
                            st.rerun()
            
            st.markdown("---")
            st.markdown("### 📋 Detailed Asset Information")
            st.markdown("*Expand any asset below to view comprehensive details*")
            
            # Display expandable details for each asset
            for asset in assets:
                display_asset_details(asset, session)
        
        # Portfolio insights
        if assets:
            st.markdown("---")
            st.markdown("### 💡 Portfolio Insights")
            
            insight_col1, insight_col2, insight_col3 = st.columns(3)
            
            with insight_col1:
                # Asset type breakdown
                type_counts = {}
                for asset in assets:
                    asset_type = asset.asset_type.value.replace('_', ' ').title()
                    type_counts[asset_type] = type_counts.get(asset_type, 0) + 1
                
                st.markdown("#### Asset Types")
                for asset_type, count in sorted(type_counts.items()):
                    st.write(f"**{asset_type}:** {count}")
            
            with insight_col2:
                # Region breakdown
                region_counts = {}
                for asset in assets:
                    region_counts[asset.region] = region_counts.get(asset.region, 0) + 1
                
                st.markdown("#### By Region")
                for region, count in sorted(region_counts.items()):
                    st.write(f"**{region}:** {count}")
            
            with insight_col3:
                # Status breakdown
                status_counts = {}
                for asset in assets:
                    status = asset.status.value.replace('_', ' ').title()
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                st.markdown("#### By Status")
                for status, count in sorted(status_counts.items()):
                    st.write(f"**{status}:** {count}")
    
    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
        import traceback
        with st.expander("Show Error Details"):
            st.code(traceback.format_exc())
    
    finally:
        if session:
            db.close_session(session)


if __name__ == "__main__":
    main()