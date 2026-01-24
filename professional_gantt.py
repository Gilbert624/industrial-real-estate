"""
专业级项目任务甘特图系统
支持多层级WBS、依赖关系、关键路径等功能
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import json

st.set_page_config(page_title="Project Gantt Chart", page_icon="📊", layout="wide")

# ========== 数据库函数 ==========

def get_db_connection():
    conn = sqlite3.connect('industrial_property.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_projects():
    """获取所有项目"""
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM projects WHERE status IN ('Planning', 'DA', 'Construction')", conn)
    conn.close()
    return df

def get_project_tasks(project_id, wbs_level=None):
    """
    获取项目的所有任务
    wbs_level: None=全部, 1=项目级, 2=阶段级, 3=任务级
    """
    conn = get_db_connection()
    
    if wbs_level:
        query = """
            SELECT * FROM project_tasks 
            WHERE project_id = ? AND wbs_level = ?
            ORDER BY sort_order, start_date
        """
        df = pd.read_sql(query, conn, params=(project_id, wbs_level))
    else:
        query = """
            SELECT * FROM project_tasks 
            WHERE project_id = ?
            ORDER BY wbs_level, sort_order, start_date
        """
        df = pd.read_sql(query, conn, params=(project_id,))
    
    conn.close()
    return df

def get_task_hierarchy(project_id):
    """获取任务的层级结构"""
    conn = get_db_connection()
    
    # 获取所有任务
    all_tasks = pd.read_sql(
        "SELECT * FROM project_tasks WHERE project_id = ? ORDER BY sort_order",
        conn, params=(project_id,)
    )
    
    # 构建树形结构
    task_tree = []
    
    for _, task in all_tasks.iterrows():
        if task['wbs_level'] == 1:
            # 顶级项目
            task_tree.append({
                'task': task,
                'children': get_children(all_tasks, task['id'])
            })
    
    conn.close()
    return task_tree

def get_children(all_tasks, parent_id):
    """递归获取子任务"""
    children = []
    for _, task in all_tasks.iterrows():
        if task['parent_task_id'] == parent_id:
            children.append({
                'task': task,
                'children': get_children(all_tasks, task['id'])
            })
    return children

def calculate_critical_path(tasks_df):
    """简化版关键路径计算"""
    # 这里是简化版，实际应该用CPM算法
    critical_tasks = tasks_df[tasks_df['is_critical'] == 1]
    return critical_tasks

# ========== 甘特图生成 ==========

def create_hierarchical_gantt(tasks_df, show_level='all'):
    """
    创建层级化的甘特图
    show_level: 'all', 'phases', 'tasks'
    """
    
    if tasks_df.empty:
        return None
    
    # 根据显示级别过滤
    if show_level == 'phases':
        tasks_df = tasks_df[tasks_df['wbs_level'] <= 2]
    elif show_level == 'tasks':
        tasks_df = tasks_df[tasks_df['wbs_level'] == 3]
    
    # 准备数据
    fig_data = []
    
    for _, task in tasks_df.iterrows():
        # 根据WBS级别设置缩进和颜色
        indent = "  " * (task['wbs_level'] - 1)
        task_label = f"{indent}{task['task_name']}"
        
        # 颜色方案
        color_map = {
            1: '#1f77b4',  # 项目级 - 蓝色
            2: '#ff7f0e',  # 阶段级 - 橙色
            3: '#2ca02c'   # 任务级 - 绿色
        }
        
        if task['is_critical']:
            color = '#d62728'  # 关键路径 - 红色
        else:
            color = color_map.get(task['wbs_level'], '#7f7f7f')
        
        # 添加任务条
        fig_data.append({
            'Task': task_label,
            'Start': task['start_date'],
            'Finish': task['finish_date'],
            'Resource': task.get('assigned_contractor', 'Unassigned'),
            'Completion': task['completion_percentage'],
            'Status': task['status'],
            'Color': color,
            'IsCritical': task['is_critical'],
            'TaskCode': task.get('task_code', ''),
            'Duration': task['duration_days']
        })
    
    df_gantt = pd.DataFrame(fig_data)
    
    # 创建甘特图
    fig = go.Figure()
    
    for i, row in df_gantt.iterrows():
        # 已完成部分
        if row['Completion'] > 0:
            completed_duration = pd.Timedelta(days=row['Duration'] * row['Completion'] / 100)
            completed_end = pd.to_datetime(row['Start']) + completed_duration
            
            fig.add_trace(go.Bar(
                x=[completed_duration.days],
                y=[row['Task']],
                name='',
                orientation='h',
                marker=dict(color='darkgreen'),
                showlegend=False,
                base=pd.to_datetime(row['Start']),
                hovertemplate=f"<b>{row['Task']}</b><br>" +
                             f"Complete: {row['Completion']:.0f}%<br>" +
                             f"Status: {row['Status']}<extra></extra>"
            ))
        
        # 总进度条
        fig.add_trace(go.Bar(
            x=[(pd.to_datetime(row['Finish']) - pd.to_datetime(row['Start'])).days],
            y=[row['Task']],
            name='',
            orientation='h',
            marker=dict(
                color=row['Color'],
                opacity=0.6 if row['Completion'] > 0 else 0.8,
                line=dict(color='red', width=2) if row['IsCritical'] else None
            ),
            showlegend=False,
            base=pd.to_datetime(row['Start']),
            hovertemplate=f"<b>{row['Task']}</b><br>" +
                         f"Code: {row['TaskCode']}<br>" +
                         f"Start: {row['Start']}<br>" +
                         f"Finish: {row['Finish']}<br>" +
                         f"Duration: {row['Duration']} days<br>" +
                         f"Resource: {row['Resource']}<br>" +
                         f"Status: {row['Status']}<br>" +
                         f"Progress: {row['Completion']:.0f}%<br>" +
                         f"<b>Critical: {row['IsCritical']}</b><extra></extra>"
        ))
    
    # 更新布局
    fig.update_layout(
        title="Project Task Timeline",
        xaxis_title="Date",
        yaxis_title="Tasks",
        height=max(600, len(df_gantt) * 30),
        barmode='overlay',
        hovermode='closest',
        showlegend=False,
        xaxis=dict(
            type='date',
            tickformat='%b %Y'
        ),
        yaxis=dict(
            autorange='reversed',
            tickfont=dict(size=10)
        )
    )
    
    return fig

# ========== 主界面 ==========

st.title("📊 Professional Project Gantt Chart")

# 项目选择
projects = get_projects()

if not projects.empty:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_project_name = st.selectbox(
            "Select Project:",
            projects['project_name'].tolist()
        )
    
    with col2:
        view_mode = st.selectbox(
            "View Mode:",
            ["All Levels", "Phases Only", "Tasks Only"]
        )
    
    # 获取选中项目的ID
    project_row = projects[projects['project_name'] == selected_project_name].iloc[0]
    project_id = project_row['id']
    
    # 显示项目摘要
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Project Status", project_row['status'])
    with col2:
        st.metric("Overall Progress", f"{project_row['completion_percentage']:.0f}%")
    with col3:
        st.metric("Start Date", project_row['start_date'])
    with col4:
        st.metric("Target Completion", project_row['expected_completion'])
    
    # 获取任务数据
    tasks_df = get_project_tasks(project_id)
    
    if not tasks_df.empty:
        
        # 视图选择标签
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Gantt Chart", 
            "📋 Task List", 
            "🎯 Critical Path",
            "➕ Add Tasks"
        ])
        
        # Tab 1: 甘特图
        with tab1:
            # 视图级别映射
            level_map = {
                "All Levels": "all",
                "Phases Only": "phases",
                "Tasks Only": "tasks"
            }
            
            show_level = level_map[view_mode]
            
            # 生成甘特图
            with st.spinner("Generating Gantt Chart..."):
                fig = create_hierarchical_gantt(tasks_df, show_level)
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 图例说明
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown("🟦 **Project Level**")
                    with col2:
                        st.markdown("🟧 **Phase Level**")
                    with col3:
                        st.markdown("🟩 **Task Level**")
                    
                    st.markdown("🟥 **Red Border = Critical Path**")
        
        # Tab 2: 任务列表
        with tab2:
            st.subheader("📋 Task Breakdown")
            
            # 过滤器
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.multiselect(
                    "Status:",
                    options=tasks_df['status'].unique(),
                    default=tasks_df['status'].unique()
                )
            
            with col2:
                level_filter = st.multiselect(
                    "WBS Level:",
                    options=[1, 2, 3],
                    default=[1, 2, 3]
                )
            
            with col3:
                show_critical_only = st.checkbox("Show Critical Path Only")
            
            # 应用过滤
            filtered_df = tasks_df[
                (tasks_df['status'].isin(status_filter)) &
                (tasks_df['wbs_level'].isin(level_filter))
            ]
            
            if show_critical_only:
                filtered_df = filtered_df[filtered_df['is_critical'] == 1]
            
            # 显示表格
            display_columns = [
                'task_code', 'task_name', 'duration_days', 
                'start_date', 'finish_date', 'completion_percentage',
                'status', 'assigned_contractor', 'is_critical'
            ]
            
            st.dataframe(
                filtered_df[display_columns],
                use_container_width=True,
                hide_index=True
            )
            
            # 统计信息
            st.divider()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Tasks", len(filtered_df))
            with col2:
                completed = len(filtered_df[filtered_df['status'] == 'Completed'])
                st.metric("Completed", completed)
            with col3:
                in_progress = len(filtered_df[filtered_df['status'] == 'In Progress'])
                st.metric("In Progress", in_progress)
            with col4:
                critical = len(filtered_df[filtered_df['is_critical'] == 1])
                st.metric("Critical Tasks", critical)
        
        # Tab 3: 关键路径
        with tab3:
            st.subheader("🎯 Critical Path Analysis")
            
            critical_tasks = tasks_df[tasks_df['is_critical'] == 1]
            
            if not critical_tasks.empty:
                st.info(f"Found {len(critical_tasks)} tasks on the critical path")
                
                # 显示关键路径任务
                for _, task in critical_tasks.iterrows():
                    with st.expander(f"🔴 {task['task_name']} ({task['task_code']})"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Duration:** {task['duration_days']} days")
                            st.write(f"**Start:** {task['start_date']}")
                            st.write(f"**Finish:** {task['finish_date']}")
                        
                        with col2:
                            st.write(f"**Status:** {task['status']}")
                            st.write(f"**Progress:** {task['completion_percentage']:.0f}%")
                            st.write(f"**Contractor:** {task.get('assigned_contractor', 'TBD')}")
                        
                        if task['notes']:
                            st.warning(f"⚠️ Note: {task['notes']}")
                
                # 时间分析
                st.divider()
                st.subheader("⏱️ Timeline Analysis")
                
                earliest_start = critical_tasks['start_date'].min()
                latest_finish = critical_tasks['finish_date'].max()
                total_duration = (pd.to_datetime(latest_finish) - pd.to_datetime(earliest_start)).days
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Critical Path Start", earliest_start)
                with col2:
                    st.metric("Critical Path End", latest_finish)
                with col3:
                    st.metric("Total Duration", f"{total_duration} days")
                
            else:
                st.info("No tasks marked as critical path yet")
        
        # Tab 4: 添加任务
        with tab4:
            st.subheader("➕ Add New Task")
            
            st.info("Task management interface - Coming soon")
            
            st.markdown("""
            **Planned Features:**
            - Add new tasks with dependencies
            - Import from MS Project XML
            - Bulk import from Excel template
            - Visual task editor
            """)
    
    else:
        st.warning("📝 No detailed tasks found for this project")
        
        st.markdown("""
        ### How to add tasks?
        
        **Option 1: Import from MS Project**
        - Export your MS Project as XML
        - Use the import tool (coming soon)
        
        **Option 2: Manual Entry**
        - Use the "Add Tasks" tab
        - Enter task details
        
        **Option 3: Excel Template**
        - Download task template
        - Fill in Excel
        - Upload for batch import
        """)

else:
    st.info("📝 No projects found. Please add projects first in Data Input Center.")

# 侧边栏
with st.sidebar:
    st.header("🛠️ Tools")
    
    if st.button("📥 Import from MS Project"):
        st.info("MS Project import feature coming soon")
    
    if st.button("📊 Export to Excel"):
        st.info("Excel export feature coming soon")
    
    st.divider()
    
    st.header("📚 Help")
    
    with st.expander("WBS Levels"):
        st.markdown("""
        - **Level 1**: Project (e.g., "Heathwood Hub")
        - **Level 2**: Phase (e.g., "Design & Approvals")
        - **Level 3**: Task (e.g., "Building Approval")
        """)
    
    with st.expander("Critical Path"):
        st.markdown("""
        Tasks marked as critical determine the project completion date.
        Any delay in critical tasks delays the entire project.
        """)
