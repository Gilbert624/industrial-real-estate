"""
Asset Portfolio Management Page
Displays and manages all industrial real estate assets

Developer: Gilbert - Brisbane, QLD
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import func, and_, or_

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

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1e3a5f;
        font-weight: 600;
    }
    h2, h3 {
        color: #2c5282;
        font-weight: 500;
    }
    .asset-card {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)


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
    
    st.title("📊 Asset Portfolio Management")
    st.markdown("### Industrial Real Estate Portfolio - Brisbane & Sunshine Coast")
    
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
        st.sidebar.markdown("### 🔍 Filters")
        
        # Get filter options
        filter_options = get_filter_options(session)
        
        # Region filter
        selected_region = st.sidebar.selectbox(
            "Region",
            options=filter_options['regions'],
            index=0
        )
        
        # Asset type filter
        selected_type = st.sidebar.selectbox(
            "Asset Type",
            options=filter_options['types'],
            index=0
        )
        
        # Status filter
        selected_status = st.sidebar.selectbox(
            "Status",
            options=filter_options['statuses'],
            index=0
        )
        
        st.sidebar.markdown("---")
        
        # Add refresh button
        if st.sidebar.button("🔄 Refresh Data"):
            st.cache_resource.clear()
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
        st.markdown("---")
        st.markdown("### 📈 Portfolio Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Assets",
                value=f"{metrics['total_assets']}",
                help="Total number of assets matching current filters"
            )
        
        with col2:
            valuation_millions = metrics['total_valuation'] / 1_000_000
            st.metric(
                label="Total Valuation",
                value=f"${valuation_millions:.2f}M AUD",
                help="Sum of current valuations for filtered assets"
            )
        
        with col3:
            avg_millions = metrics['avg_valuation'] / 1_000_000
            st.metric(
                label="Average Asset Value",
                value=f"${avg_millions:.2f}M AUD",
                help="Average valuation per asset"
            )
        
        st.markdown("---")
        
        # Display assets table
        st.markdown("### 🏢 Asset List")
        
        if not assets:
            st.info("No assets found matching the selected filters.")
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