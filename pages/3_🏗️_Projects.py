"""
Project Management Page
Displays and manages development projects (under construction and completed)

Developer: Gilbert - Brisbane, QLD
"""

import streamlit as st
import plotly.graph_objects as go
from models.database import DatabaseManager
from datetime import datetime, timedelta
import pandas as pd
import json
import re
from config.theme import generate_css
from config.i18n import t, get_current_language

# Page configuration
st.set_page_config(
    page_title="Projects",
    page_icon="🏗️",
    layout="wide"
)

# 应用专业主题
st.markdown(generate_css('light'), unsafe_allow_html=True)


@st.cache_resource
def get_database():
    """Get cached database connection"""
    try:
        return DatabaseManager('industrial_real_estate.db')
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None


def get_completion_percentage(project):
    """Get completion percentage from project (from notes or calculated from budget)"""
    # First, try to get from notes field (stored as "COMPLETION_PERCENTAGE:XX")
    if project.notes:
        # Look for pattern like "COMPLETION_PERCENTAGE:75" in notes
        match = re.search(r'COMPLETION_PERCENTAGE:(\d+)', project.notes)
        if match:
            try:
                return int(match.group(1))
            except (ValueError, AttributeError):
                pass
    
    # If not found in notes, calculate from budget
    if project.total_budget and project.total_budget > 0:
        actual_cost = float(project.actual_cost) if project.actual_cost else 0.0
        total_budget = float(project.total_budget) if project.total_budget else 0.0
        if total_budget > 0:
            return min(100, int((actual_cost / total_budget) * 100))
    return 0


def set_completion_percentage_in_notes(notes, completion_percentage):
    """Set completion percentage in notes field"""
    if notes is None:
        notes = ""
    
    # Remove existing COMPLETION_PERCENTAGE if exists
    notes = re.sub(r'COMPLETION_PERCENTAGE:\d+\s*', '', notes).strip()
    
    # Add new completion percentage
    if notes:
        notes = f"{notes}\nCOMPLETION_PERCENTAGE:{completion_percentage}"
    else:
        notes = f"COMPLETION_PERCENTAGE:{completion_percentage}"
    
    return notes


def main():
    """Main application function"""
    
    # Title
    st.title(f"🏗️ {t('projects.title')}")
    
    # Initialize database
    db = get_database()
    if not db:
        st.error("⚠️ Could not connect to database.")
        return
    
    # Session state management
    if 'edit_project_id' not in st.session_state:
        st.session_state.edit_project_id = None
    
    # ==================== Top Key Metrics ====================
    st.markdown('<div style="margin-bottom: 2rem;">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        active_count = db.get_active_projects_count()
        total_budget = float(db.get_total_projects_budget())
        total_cost = float(db.get_total_projects_cost())
        avg_completion = float(db.get_average_completion())
        
        with col1:
            st.metric(
                t('home.active_projects'),
                active_count,
                help="Projects not yet completed"
            )
        
        with col2:
            st.metric(
                t('projects.total_budget'),
                f"${total_budget/1e6:.1f}M",
                help="Sum of all project budgets"
            )
        
        with col3:
            st.metric(
                t('projects.total_cost'),
                f"${total_cost/1e6:.1f}M",
                delta=f"${(total_budget - total_cost)/1e6:+.1f}M",
                delta_color="normal",
                help="Total actual costs incurred"
            )
        
        with col4:
            st.metric(
                t('projects.avg_completion'),
                f"{avg_completion:.0f}%",
                help="Average progress across all projects"
            )
    except Exception as e:
        st.error(f"Error loading metrics: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # ==================== Sidebar - Project Form ====================
    with st.sidebar:
        st.header(t('projects.project_management'))
        
        # Determine mode (add or edit)
        mode = t('projects.edit_project') if st.session_state.edit_project_id else t('projects.add_new_project')
        st.subheader(mode)
        
        # Load existing data if in edit mode
        project = None
        if st.session_state.edit_project_id:
            try:
                project = db.get_project_by_id(st.session_state.edit_project_id)
                if not project:
                    st.error("Project not found!")
                    st.session_state.edit_project_id = None
            except Exception as e:
                st.error(f"Error loading project: {e}")
                st.session_state.edit_project_id = None
        
        # Get assets for dropdown
        try:
            assets = db.get_all_assets_for_dropdown()
            asset_options = ["None"] + [f"{a['name']}" for a in assets]
            asset_dict = {a['name']: a['id'] for a in assets}
        except Exception as e:
            st.error(f"Error loading assets: {e}")
            assets = []
            asset_options = ["None"]
            asset_dict = {}
        
        # Form
        with st.form("project_form"):
            # Project name
            name = st.text_input(
                f"{t('projects.project_name')}*",
                value=project.project_name if project else "",
                help="Full name of the development project"
            )
            
            # Status and Type
            col1, col2 = st.columns(2)
            with col1:
                status_options = [
                    t('projects.project_status.planning'),
                    t('projects.project_status.approved'),
                    t('projects.project_status.construction'),
                    t('projects.project_status.completed'),
                    t('projects.project_status.on_hold')
                ]
                if project:
                    # Use status directly as string
                    current_status_display = str(project.status)
                    # Map status string to translation
                    status_map = {
                        "Planning": t('projects.project_status.planning'),
                        "Approved": t('projects.project_status.approved'),
                        "Construction": t('projects.project_status.construction'),
                        "Completed": t('projects.project_status.completed'),
                        "On Hold": t('projects.project_status.on_hold')
                    }
                    current_status_translated = status_map.get(current_status_display, status_options[0])
                    status_index = status_options.index(current_status_translated) if current_status_translated in status_options else 0
                else:
                    status_index = 2  # Default to Construction
                
                status = st.selectbox(
                    f"{t('common.status')}*",
                    status_options,
                    index=status_index
                )
            
            with col2:
                # Asset selection (required for database)
                if project and project.asset:
                    current_asset_name = project.asset.name
                    asset_index = asset_options.index(current_asset_name) if current_asset_name in asset_options else 0
                else:
                    asset_index = 0
                
                selected_asset = st.selectbox(
                    f"{t('finance.related_asset')}*",
                    asset_options,
                    index=asset_index,
                    help="Select the asset this project is associated with"
                )
            
            # Location (from asset if available, or free text)
            location_value = ""
            if project and project.asset:
                location_value = project.asset.region or project.asset.suburb or ""
            
            location = st.text_input(
                t('projects.location'),
                value=location_value,
                placeholder="Brisbane, Sunshine Coast, etc.",
                help="Project location (usually from asset)"
            )
            
            # Completion percentage (calculated from budget usage)
            if project:
                completion = get_completion_percentage(project)
            else:
                completion = 0
            
            completion = st.slider(
                f"{t('projects.completion')} %",
                0, 100,
                completion,
                help="Current progress percentage"
            )
            
            # Financial information
            col3, col4 = st.columns(2)
            with col3:
                budget = st.number_input(
                    f"{t('projects.budget')} (AUD)*",
                    min_value=0.0,
                    step=100000.0,
                    value=float(project.total_budget) if project and project.total_budget else 0.0,
                    format="%.0f",
                    help="Total project budget"
                )
                
                land_area_val = 0.0
                if project and project.asset and project.asset.land_area_sqm:
                    land_area_val = float(project.asset.land_area_sqm)
                
                land_area = st.number_input(
                    t('assets.land_area'),
                    min_value=0.0,
                    value=land_area_val,
                    help="Land area (from associated asset)"
                )
            
            with col4:
                actual_cost = st.number_input(
                    f"{t('projects.actual_cost')} (AUD)",
                    min_value=0.0,
                    step=100000.0,
                    value=float(project.actual_cost) if project and project.actual_cost else 0.0,
                    format="%.0f",
                    help="Current actual costs (can be updated via transactions)"
                )
                
                building_area_val = 0.0
                if project and project.asset and project.asset.building_area_sqm:
                    building_area_val = float(project.asset.building_area_sqm)
                
                building_area = st.number_input(
                    t('assets.building_area'),
                    min_value=0.0,
                    value=building_area_val,
                    help="Building area (from associated asset)"
                )
            
            # Dates
            col5, col6 = st.columns(2)
            with col5:
                start_date = st.date_input(
                    t('projects.start_date'),
                    value=project.planned_start_date if project and project.planned_start_date else datetime.now().date()
                )
            
            with col6:
                expected_completion = st.date_input(
                    t('projects.expected_completion'),
                    value=project.planned_completion_date if project and project.planned_completion_date else (datetime.now() + timedelta(days=180)).date()
                )
            
            # Estimated value (from asset valuation if available)
            estimated_value = 0.0
            if project and project.asset and project.asset.current_valuation:
                estimated_value = float(project.asset.current_valuation)
            
            estimated_value = st.number_input(
                "Estimated Value (AUD)",
                min_value=0.0,
                step=100000.0,
                value=estimated_value,
                format="%.0f",
                help="Estimated completed value"
            )
            
            # Description
            description = st.text_area(
                t('common.description'),
                value=project.description if project and project.description else "",
                placeholder="Project details, key features, etc.",
                height=100
            )
            
            # Buttons
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submitted = st.form_submit_button(f"💾 {t('common.save')}", use_container_width=True)
            with col_btn2:
                cancelled = st.form_submit_button(f"❌ {t('common.cancel')}", use_container_width=True)
            
            # Handle submission
            if submitted:
                # Validation
                if not name:
                    st.error(f"❌ {t('projects.project_name')} {t('validation.required')}")
                elif budget <= 0:
                    st.error(f"❌ {t('projects.budget')} {t('validation.positive_number')}")
                elif start_date > expected_completion:
                    st.error(f"❌ {t('validation.start_before_end')}")
                elif selected_asset == "None":
                    st.error(f"❌ {t('finance.related_asset')} {t('validation.required')}")
                else:
                    # Prepare data
                    # Store completion_percentage in notes field
                    # Get existing notes or use empty string
                    existing_notes = project.notes if project and project.notes else ""
                    notes_with_completion = set_completion_percentage_in_notes(
                        existing_notes,
                        completion
                    )
                    
                    project_data = {
                        "name": name,
                        "status": status,
                        "budget": budget,
                        "actual_cost": actual_cost,
                        "start_date": start_date,
                        "expected_completion": expected_completion,
                        "description": description,
                        "notes": notes_with_completion
                    }
                    
                    # Get asset_id
                    if selected_asset != "None":
                        project_data["asset_id"] = asset_dict[selected_asset]
                    
                    try:
                        if st.session_state.edit_project_id:
                            # Update
                            db.update_project(st.session_state.edit_project_id, project_data)
                            st.success(f"✅ {t('projects.project_saved')}")
                        else:
                            # Add
                            db.add_project(project_data)
                            st.success(f"✅ {t('projects.project_saved')}")
                        
                        st.session_state.edit_project_id = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {t('messages.error_occurred')}: {e}")
            
            # Handle cancel
            if cancelled:
                st.session_state.edit_project_id = None
                st.rerun()
    
    # ==================== Main Area - Project List ====================
    st.subheader(f"📋 {t('projects.title')}")
    
    # Status filter
    status_filter = st.selectbox(
        f"{t('common.filter')} {t('common.by')} {t('common.status')}",
        [t('assets.all'), t('projects.project_status.planning'), t('projects.project_status.approved'), t('projects.project_status.construction'), t('projects.project_status.completed'), t('projects.project_status.on_hold')],
        help="Filter projects by their current status"
    )
    
    # Get projects
    try:
        if status_filter == "All":
            projects = db.get_all_projects()
        else:
            projects = db.get_projects_by_status(status_filter)
        
        if projects:
            # Status color and emoji mapping
            status_display_map = {
                "Planning": ("🔵", "blue"),
                "Approved": ("🟢", "green"),
                "Construction": ("🟠", "orange"),
                "Completed": ("⚪", "gray"),
                "On Hold": ("🔴", "red"),
                "Approval Pending": ("🟡", "yellow"),
                "Cancelled": ("⚫", "black")
            }
            
            # Table header
            header_cols = st.columns([3, 1.5, 1.5, 1.5, 1.5, 1.5, 1.2, 0.8, 0.8])
            headers = ["Project Name", "Status", "Type", "Budget", "Actual Cost", "Variance", "Progress", "", ""]
            for col, header in zip(header_cols, headers):
                if header:
                    col.write(f"**{header}**")
            
            st.write("---")
            
            # Each project row
            for proj in projects:
                cols = st.columns([3, 1.5, 1.5, 1.5, 1.5, 1.5, 1.2, 0.8, 0.8])
                
                # Project name
                cols[0].write(proj.project_name)
                
                # Status (with color emoji)
                status_display = str(proj.status)
                emoji, color = status_display_map.get(status_display, ("⚪", "gray"))
                cols[1].write(f"{emoji} {status_display}")
                
                # Type (from asset type if available)
                if proj.asset and proj.asset.asset_type:
                    asset_type_display = proj.asset.asset_type.value.replace('_', ' ').title()
                else:
                    asset_type_display = "N/A"
                cols[2].write(asset_type_display)
                
                # Budget
                budget_val = float(proj.total_budget) if proj.total_budget else 0.0
                cols[3].write(f"${budget_val/1e6:.1f}M")
                
                # Actual cost
                actual_cost_val = float(proj.actual_cost) if proj.actual_cost else 0.0
                cols[4].write(f"${actual_cost_val/1e6:.1f}M")
                
                # Cost variance
                variance = budget_val - actual_cost_val
                if variance >= 0:
                    variance_color = "green"
                    variance_text = f"+${variance/1e6:.1f}M"
                else:
                    variance_color = "red"
                    variance_text = f"-${abs(variance)/1e6:.1f}M"
                
                cols[5].markdown(
                    f"<span style='color:{variance_color}'>{variance_text}</span>",
                    unsafe_allow_html=True
                )
                
                # Progress bar
                completion_pct = get_completion_percentage(proj)
                progress_color = "#4CAF50" if completion_pct >= 50 else "#FF9800"
                progress_html = f"""
                <div style="background-color: #e0e0e0; border-radius: 5px; height: 20px; width: 100%;">
                    <div style="background-color: {progress_color}; height: 100%; width: {completion_pct}%; 
                         border-radius: 5px; text-align: center; line-height: 20px; color: white; font-size: 11px;">
                        {completion_pct}%
                    </div>
                </div>
                """
                cols[6].markdown(progress_html, unsafe_allow_html=True)
                
                # Edit button
                if cols[7].button("✏️", key=f"edit_proj_{proj.id}", help="Edit project"):
                    st.session_state.edit_project_id = proj.id
                    st.rerun()
                
                # Delete button
                if cols[8].button("🗑️", key=f"del_proj_{proj.id}", help="Delete project"):
                    st.session_state[f'confirm_delete_proj_{proj.id}'] = True
                
                # Delete confirmation
                if st.session_state.get(f'confirm_delete_proj_{proj.id}'):
                    st.warning(f"⚠️ Are you sure you want to delete project: **{proj.project_name}**?")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Yes, Delete", key=f"yes_proj_{proj.id}"):
                            try:
                                db.delete_project(proj.id)
                                st.success("✅ Project deleted successfully!")
                                del st.session_state[f'confirm_delete_proj_{proj.id}']
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error deleting project: {e}")
                    with col2:
                        if st.button("❌ Cancel", key=f"no_proj_{proj.id}"):
                            del st.session_state[f'confirm_delete_proj_{proj.id}']
                            st.rerun()
                
                # Project details (expandable)
                with st.expander(f"📄 View Details - {proj.project_name}"):
                    detail_col1, detail_col2, detail_col3 = st.columns(3)
                    
                    with detail_col1:
                        st.write("**Basic Information**")
                        asset_location = proj.asset.region if proj.asset and proj.asset.region else "N/A"
                        st.write(f"Location: {asset_location}")
                        st.write(f"Start Date: {proj.planned_start_date.strftime('%Y-%m-%d') if proj.planned_start_date else 'N/A'}")
                        st.write(f"Expected Completion: {proj.planned_completion_date.strftime('%Y-%m-%d') if proj.planned_completion_date else 'N/A'}")
                        if proj.asset:
                            st.write(f"Related Asset: {proj.asset.name}")
                    
                    with detail_col2:
                        st.write("**Area & Value**")
                        if proj.asset:
                            land_area = float(proj.asset.land_area_sqm) if proj.asset.land_area_sqm else None
                            building_area = float(proj.asset.building_area_sqm) if proj.asset.building_area_sqm else None
                            estimated_value = float(proj.asset.current_valuation) if proj.asset.current_valuation else None
                            st.write(f"Land Area: {land_area:,.0f} sqm" if land_area else "Land Area: N/A")
                            st.write(f"Building Area: {building_area:,.0f} sqm" if building_area else "Building Area: N/A")
                            st.write(f"Estimated Value: ${estimated_value/1e6:.1f}M" if estimated_value else "Estimated Value: N/A")
                        else:
                            st.write("Land Area: N/A")
                            st.write("Building Area: N/A")
                            st.write("Estimated Value: N/A")
                    
                    with detail_col3:
                        st.write("**Financial Summary**")
                        budget_val = float(proj.total_budget) if proj.total_budget else 0.0
                        actual_cost_val = float(proj.actual_cost) if proj.actual_cost else 0.0
                        st.write(f"Budget: ${budget_val/1e6:.2f}M")
                        st.write(f"Spent: ${actual_cost_val/1e6:.2f}M")
                        remaining = budget_val - actual_cost_val
                        st.write(f"Remaining: ${remaining/1e6:.2f}M")
                    
                    if proj.description:
                        st.write("**Description**")
                        st.write(proj.description)
                    
                    # Related transactions (if any)
                    try:
                        transactions = db.get_project_transactions(proj.id)
                        if transactions:
                            st.write(f"**Related Transactions ({len(transactions)})**")
                            for tx in transactions[:5]:  # Show only recent 5
                                tx_amount = abs(float(tx.amount))
                                tx_category = tx.category or "N/A"
                                st.write(f"- {tx.transaction_date.strftime('%Y-%m-%d')}: {tx_category} - ${tx_amount:,.0f}")
                            if len(transactions) > 5:
                                st.write(f"_...and {len(transactions) - 5} more transactions_")
                    except Exception as e:
                        st.write(f"_Could not load transactions: {e}_")
                
                st.write("---")
        
        else:
            st.info(f"📭 {t('messages.no_results')}")
    
    except Exception as e:
        st.error(f"❌ Error loading projects: {e}")
        import traceback
        with st.expander("Show Error Details"):
            st.code(traceback.format_exc())
    
    st.markdown("---")
    st.markdown("*© 2025 Gilbert Industrial Real Estate Development | Brisbane, Queensland, Australia*")


if __name__ == "__main__":
    main()
