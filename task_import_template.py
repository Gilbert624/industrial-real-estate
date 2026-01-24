"""
Excel任务批量导入功能
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import io

def create_task_template():
    """生成Excel任务导入模板"""
    
    # 示例数据
    template_data = {
        'Task Name': [
            'DESIGN & APPROVALS',
            'Building Approval',
            'Plumbing & Drainage Approval',
            'QFES Approval',
            'MOBILISATION & EARLY WORKS',
            'Site Setup',
            'Bulk Earthworks',
            'MAIN BUILDING',
            'FRPC Footings',
            'Tilt Panel Casting',
        ],
        'Task Code': [
            'HH-100',
            'HH-101',
            'HH-102',
            'HH-103',
            'HH-200',
            'HH-201',
            'HH-202',
            'HH-300',
            'HH-301',
            'HH-302',
        ],
        'WBS Level': [2, 3, 3, 3, 2, 3, 3, 2, 3, 3],
        'Parent Task Code': [
            '', 'HH-100', 'HH-100', 'HH-100',
            '', 'HH-200', 'HH-200',
            '', 'HH-300', 'HH-300'
        ],
        'Duration (days)': [51, 50, 50, 50, 53, 5, 10, 117, 15, 25],
        'Start Date': [
            '2025-01-10', '2025-01-10', '2025-01-10', '2025-01-10',
            '2025-11-24', '2025-11-24', '2025-12-01',
            '2026-04-30', '2026-04-30', '2026-05-20'
        ],
        'Assigned Contractor': [
            '', 'Logan City Council', 'Council', 'QFES',
            '', 'Site Contractor', 'Earthworks Co',
            '', 'Concrete Contractor', 'Precast Supplier'
        ],
        'Status': [
            'In Progress', 'In Progress', 'In Progress', 'In Progress',
            'Not Started', 'Not Started', 'Not Started',
            'Not Started', 'Not Started', 'Not Started'
        ],
        'Completion %': [60, 80, 60, 40, 0, 0, 0, 0, 0, 0],
        'Is Critical': [1, 1, 1, 1, 0, 0, 0, 1, 1, 1],
        'Estimated Cost': [0, 15000, 8000, 5000, 0, 12000, 35000, 0, 85000, 250000],
        'Notes': [
            'Critical approvals phase',
            'Required for construction',
            '',
            '',
            'Early works preparation',
            'Fencing and signage',
            '10 days of excavation',
            'Main building structure',
            'Foundation work',
            'Precast panels - 25 days cure time'
        ]
    }
    
    df = pd.DataFrame(template_data)
    
    return df

def import_tasks_from_excel(uploaded_file, project_id):
    """从Excel导入任务"""
    
    try:
        # 读取Excel
        df = pd.read_excel(uploaded_file)
        
        # 验证必需的列
        required_columns = ['Task Name', 'WBS Level', 'Duration (days)', 'Start Date']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, f"Missing required columns: {', '.join(missing_columns)}"
        
        conn = sqlite3.connect('industrial_property.db')
        cursor = conn.cursor()
        
        # 存储task_code到id的映射 (用于处理parent关系)
        task_code_map = {}
        
        imported_count = 0
        
        for idx, row in df.iterrows():
            # 跳过空行
            if pd.isna(row['Task Name']):
                continue
            
            # 计算finish date
            start_date = pd.to_datetime(row['Start Date']).date()
            duration = int(row['Duration (days)'])
            finish_date = start_date + timedelta(days=duration)
            
            # 处理parent task
            parent_task_id = None
            if 'Parent Task Code' in df.columns and pd.notna(row['Parent Task Code']):
                parent_code = str(row['Parent Task Code']).strip()
                if parent_code and parent_code in task_code_map:
                    parent_task_id = task_code_map[parent_code]
            
            # 插入任务
            cursor.execute("""
                INSERT INTO project_tasks 
                (project_id, task_name, task_code, wbs_level, parent_task_id,
                 duration_days, start_date, finish_date, assigned_contractor,
                 status, completion_percentage, is_critical, estimated_cost, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                row['Task Name'],
                row.get('Task Code', f'T-{idx}'),
                int(row['WBS Level']),
                parent_task_id,
                duration,
                start_date,
                finish_date,
                row.get('Assigned Contractor', ''),
                row.get('Status', 'Not Started'),
                float(row.get('Completion %', 0)),
                int(row.get('Is Critical', 0)),
                float(row.get('Estimated Cost', 0)),
                row.get('Notes', '')
            ))
            
            # 记录task_code到id的映射
            task_id = cursor.lastrowid
            if pd.notna(row.get('Task Code')):
                task_code_map[str(row['Task Code'])] = task_id
            
            imported_count += 1
        
        conn.commit()
        conn.close()
        
        return True, f"Successfully imported {imported_count} tasks"
        
    except Exception as e:
        return False, str(e)

# ========== 在Gantt Chart的Add Tasks tab中添加 ==========

with tab4:  # Add Tasks tab
    st.subheader("➕ Add Tasks")
    
    # 添加输入方式选择
    input_method = st.radio(
        "Choose input method:",
        ["📝 Single Task", "📊 Excel Batch Import", "📋 Quick List"],
        horizontal=True
    )
    
    # ===== 方法1: 单个任务 (原有功能) =====
    if input_method == "📝 Single Task":
        with st.form("add_task_form"):
            # ... 原有的单个任务表单
            pass
    
    # ===== 方法2: Excel批量导入 =====
    elif input_method == "📊 Excel Batch Import":
        st.markdown("### 📥 Import Tasks from Excel")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.info("""
            **Steps:**
            1. Download the template
            2. Fill in your tasks
            3. Upload the file
            4. Review and import
            """)
            
            # 下载模板按钮
            template_df = create_task_template()
            
            # 转换为Excel bytes
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                template_df.to_excel(writer, sheet_name='Tasks', index=False)
                
                # 添加说明sheet
                instructions = pd.DataFrame({
                    'Column': ['Task Name', 'Task Code', 'WBS Level', 'Parent Task Code', 
                              'Duration (days)', 'Start Date', 'Status', 'Is Critical'],
                    'Description': [
                        'Name of the task (required)',
                        'Unique code like HH-101 (optional but recommended)',
                        '2=Phase, 3=Task (required)',
                        'Parent task code for hierarchy (optional)',
                        'Number of days (required)',
                        'YYYY-MM-DD format (required)',
                        'Not Started, In Progress, Completed, Delayed',
                        '1=Yes, 0=No'
                    ]
                })
                instructions.to_excel(writer, sheet_name='Instructions', index=False)
            
            excel_data = output.getvalue()
            
            st.download_button(
                label="📥 Download Template",
                data=excel_data,
                file_name=f"task_import_template_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
        
        with col2:
            st.warning("""
            **Important:**
            - Do NOT change column names
            - Task Code must be unique
            - Parent Task Code must exist in the file
            - Date format: YYYY-MM-DD
            """)
        
        st.divider()
        
        # 上传文件
        uploaded_file = st.file_uploader(
            "Upload your completed Excel file",
            type=['xlsx', 'xls'],
            help="Upload the template file with your task data"
        )
        
        if uploaded_file:
            # 预览数据
            try:
                preview_df = pd.read_excel(uploaded_file)
                
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                st.metric("Tasks found", len(preview_df))
                
                with st.expander("📋 Preview Data", expanded=True):
                    st.dataframe(preview_df, use_container_width=True)
                
                # 数据验证
                st.subheader("🔍 Validation")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    phases = len(preview_df[preview_df['WBS Level'] == 2])
                    st.metric("Phases (Level 2)", phases)
                
                with col2:
                    tasks = len(preview_df[preview_df['WBS Level'] == 3])
                    st.metric("Tasks (Level 3)", tasks)
                
                with col3:
                    critical = preview_df['Is Critical'].sum() if 'Is Critical' in preview_df.columns else 0
                    st.metric("Critical Tasks", int(critical))
                
                # 导入按钮
                st.divider()
                
                if st.button("🚀 Import All Tasks", type="primary", use_container_width=True):
                    with st.spinner("Importing tasks..."):
                        success, message = import_tasks_from_excel(uploaded_file, project_id)
                        
                        if success:
                            st.success(f"✅ {message}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ Import failed: {message}")
                
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
    
    # ===== 方法3: 快速列表输入 =====
    elif input_method == "📋 Quick List":
        st.markdown("### ⚡ Quick List Entry")
        
        st.info("""
        Enter tasks one per line in this format:
        `Task Name | Duration | Contractor | Critical (Y/N)`
        
        **Example:**
        ```
        Building Approval | 50 | Logan Council | Y
        Site Setup | 5 | ABC Contractors | N
        FRPC Footings | 15 | Concrete Co | Y
        ```
        """)
        
        task_list = st.text_area(
            "Enter your tasks:",
            height=300,
            placeholder="Building Approval | 50 | Logan Council | Y\nSite Setup | 5 | ABC Contractors | N"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            default_start = st.date_input("Default Start Date", datetime.now())
        
        with col2:
            default_wbs = st.selectbox("Default WBS Level", [2, 3], format_func=lambda x: "Phase" if x==2 else "Task")
        
        if st.button("🚀 Import Task List", type="primary"):
            if task_list.strip():
                lines = [line.strip() for line in task_list.split('\n') if line.strip()]
                
                conn = sqlite3.connect('industrial_property.db')
                cursor = conn.cursor()
                
                imported = 0
                current_date = default_start
                
                for line in lines:
                    parts = [p.strip() for p in line.split('|')]
                    
                    if len(parts) >= 2:
                        task_name = parts[0]
                        try:
                            duration = int(parts[1])
                        except:
                            duration = 10
                        
                        contractor = parts[2] if len(parts) > 2 else ''
                        is_critical = 1 if len(parts) > 3 and parts[3].upper() == 'Y' else 0
                        
                        finish_date = current_date + timedelta(days=duration)
                        
                        cursor.execute("""
                            INSERT INTO project_tasks 
                            (project_id, task_name, wbs_level, duration_days,
                             start_date, finish_date, assigned_contractor, is_critical, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Not Started')
                        """, (project_id, task_name, default_wbs, duration,
                              current_date, finish_date, contractor, is_critical))
                        
                        imported += 1
                        current_date = finish_date  # 下一个任务接着开始
                
                conn.commit()
                conn.close()
                
                st.success(f"✅ Imported {imported} tasks!")
                st.rerun()
            else:
                st.warning("Please enter at least one task")
