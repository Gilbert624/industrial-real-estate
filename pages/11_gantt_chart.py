"""
专业级项目任务甘特图系统
支持多层级WBS、依赖关系、关键路径等功能
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sqlite3
import io
from datetime import datetime, timedelta

DB_PATH = "industrial_property.db"

st.set_page_config(page_title="Project Gantt Chart", page_icon="📊", layout="wide")

# ========== 数据库函数 ==========

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def table_exists(conn, table_name):
    return conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    ).fetchone() is not None

def column_exists(conn, table_name, column_name):
    return conn.execute(
        "SELECT 1 FROM pragma_table_info(?) WHERE name = ? LIMIT 1",
        (table_name, column_name)
    ).fetchone() is not None

def init_task_table():
    """确保project_tasks表存在"""
    conn = get_db_connection()
    if not table_exists(conn, "project_tasks"):
        conn.execute("""
            CREATE TABLE project_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                task_name TEXT NOT NULL,
                task_code TEXT,
                description TEXT,
                parent_task_id INTEGER,
                wbs_level INTEGER DEFAULT 1,
                sort_order INTEGER,
                duration_days INTEGER NOT NULL,
                start_date DATE NOT NULL,
                finish_date DATE NOT NULL,
                actual_start_date DATE,
                actual_finish_date DATE,
                predecessor_ids TEXT,
                dependency_type TEXT DEFAULT 'FS',
                lag_days INTEGER DEFAULT 0,
                completion_percentage REAL DEFAULT 0,
                status TEXT DEFAULT 'Not Started',
                assigned_contractor TEXT,
                estimated_cost REAL,
                actual_cost REAL,
                is_critical BOOLEAN DEFAULT 0,
                total_float_days INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id),
                FOREIGN KEY (parent_task_id) REFERENCES project_tasks(id)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_project ON project_tasks(project_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_parent ON project_tasks(parent_task_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON project_tasks(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_critical ON project_tasks(is_critical)")
        conn.commit()
    conn.close()

def ensure_example_project(conn):
    has_is_active = column_exists(conn, "projects", "is_active")
    conn.execute(
        f"""
        INSERT INTO projects (
            id, project_name, status,
            planned_start_date, planned_completion_date
            {" , is_active" if has_is_active else ""}
        ) VALUES (1, ?, 'Construction', ?, ? {", 1" if has_is_active else ""})
        ON CONFLICT(id) DO UPDATE SET
            project_name=excluded.project_name,
            status=excluded.status,
            planned_start_date=excluded.planned_start_date,
            planned_completion_date=excluded.planned_completion_date
            {", is_active=excluded.is_active" if has_is_active else ""}
        """,
        ("Heathwood Hub", "2025-01-10", "2026-12-16")
    )

def ensure_project_exists(conn, project_id, project_name="Heathwood Hub"):
    existing = conn.execute("SELECT id FROM projects WHERE id = ?", (project_id,)).fetchone()
    if existing:
        return existing[0]

    columns = ["id", "project_name"]
    values = [project_id, project_name]

    if column_exists(conn, "projects", "status"):
        columns.append("status")
        values.append("Construction")
    if column_exists(conn, "projects", "planned_start_date"):
        columns.append("planned_start_date")
        values.append("2025-01-10")
    if column_exists(conn, "projects", "planned_completion_date"):
        columns.append("planned_completion_date")
        values.append("2026-12-16")
    if column_exists(conn, "projects", "is_active"):
        columns.append("is_active")
        values.append(1)

    placeholders = ", ".join(["?"] * len(columns))
    try:
        conn.execute(
            f"INSERT INTO projects ({', '.join(columns)}) VALUES ({placeholders})",
            values
        )
        return project_id
    except sqlite3.IntegrityError as exc:
        if "datatype mismatch" not in str(exc):
            raise

    columns = [c for c in columns if c != "id"]
    values = values[1:]
    placeholders = ", ".join(["?"] * len(columns))
    cursor = conn.execute(
        f"INSERT INTO projects ({', '.join(columns)}) VALUES ({placeholders})",
        values
    )
    return cursor.lastrowid

def load_heathwood_example(project_id=None):
    conn = get_db_connection()
    conn.execute("PRAGMA foreign_keys = ON")

    init_task_table()

    if project_id is None:
        project_id = 1
        ensure_example_project(conn)
    else:
        project_id = ensure_project_exists(conn, project_id)

    conn.execute("DELETE FROM project_tasks WHERE project_id = ?", (project_id,))

    phase_tasks = [
        (project_id, None, 'DESIGN & APPROVALS', 'HH-100', 2, 1, 51, '2025-01-10', '2025-12-10', 60, 'In Progress', None, 1, 0, None),
        (project_id, None, 'MOBILISATION & EARLY WORKS', 'HH-200', 2, 2, 53, '2025-11-24', '2026-02-25', 0, 'Not Started', None, 0, 0, None),
        (project_id, None, 'EXTERNAL SERVICES', 'HH-300', 2, 3, 175, '2026-02-26', '2026-10-28', 0, 'Not Started', None, 1, 0, None),
        (project_id, None, 'MAIN BUILDING', 'HH-400', 2, 4, 117, '2026-04-30', '2026-10-09', 0, 'Not Started', None, 1, 0, None),
        (project_id, None, 'OFFICE BUILDINGS', 'HH-500', 2, 5, 133, '2026-05-21', '2026-11-23', 0, 'Not Started', None, 0, 0, None),
        (project_id, None, 'EXTERNAL WORKS', 'HH-600', 2, 6, 60, '2026-09-07', '2026-11-27', 0, 'Not Started', None, 0, 0, None),
        (project_id, None, 'CLOSE OUT', 'HH-700', 2, 7, 17, '2026-11-24', '2026-12-16', 0, 'Not Started', None, 0, 0, None),
    ]

    for task in phase_tasks:
        conn.execute("""
            INSERT INTO project_tasks 
            (project_id, parent_task_id, task_name, task_code, wbs_level, sort_order,
             duration_days, start_date, finish_date, completion_percentage, status,
             assigned_contractor, is_critical, estimated_cost, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, task)

    design_id = conn.execute("SELECT id FROM project_tasks WHERE task_code = 'HH-100'").fetchone()[0]
    detail_tasks = [
        (project_id, design_id, 'Building Approval', 'HH-106', 3, 1, 50, '2025-01-10', '2025-12-09', 80, 'In Progress', 'Logan City Council', 1, 15000, 'Critical approval'),
        (project_id, design_id, 'Plumbing & Drainage Approval', 'HH-104', 3, 2, 50, '2025-01-10', '2025-12-09', 60, 'In Progress', 'Council', 1, 8000, None),
        (project_id, design_id, 'QFES Approval', 'HH-105', 3, 3, 50, '2025-01-10', '2025-12-09', 40, 'In Progress', 'QFES', 1, 5000, None),
        (project_id, design_id, 'QUU Approval', 'HH-107', 3, 4, 50, '2025-01-10', '2025-12-09', 50, 'In Progress', 'QUU', 0, 6000, None),
    ]

    for task in detail_tasks:
        conn.execute("""
            INSERT INTO project_tasks 
            (project_id, parent_task_id, task_name, task_code, wbs_level, sort_order,
             duration_days, start_date, finish_date, completion_percentage, status,
             assigned_contractor, is_critical, estimated_cost, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, task)

    main_building_id = conn.execute("SELECT id FROM project_tasks WHERE task_code = 'HH-400'").fetchone()[0]
    building_tasks = [
        (project_id, main_building_id, 'FRPC Footings', 'HH-432', 3, 1, 15, '2026-04-30', '2026-05-20', 0, 'Not Started', 'Concrete Contractor', 1, 85000, None),
        (project_id, main_building_id, 'Cast & Cure Tilt Panels', 'HH-433', 3, 2, 25, '2026-04-30', '2026-06-03', 0, 'Not Started', 'Precast Supplier', 1, 250000, None),
        (project_id, main_building_id, 'Stand Tilt Panels', 'HH-434', 3, 3, 7, '2026-06-04', '2026-06-12', 0, 'Not Started', 'Crane Operator', 1, 45000, None),
        (project_id, main_building_id, 'Structural Steel Install', 'HH-435', 3, 4, 20, '2026-06-15', '2026-07-10', 0, 'Not Started', 'Steel Erector', 1, 320000, None),
        (project_id, main_building_id, 'Roofing & Cladding', 'HH-436', 3, 5, 25, '2026-07-13', '2026-08-14', 0, 'Not Started', 'Roofing Contractor', 1, 180000, None),
    ]

    for task in building_tasks:
        conn.execute("""
            INSERT INTO project_tasks 
            (project_id, parent_task_id, task_name, task_code, wbs_level, sort_order,
             duration_days, start_date, finish_date, completion_percentage, status,
             assigned_contractor, is_critical, estimated_cost, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, task)

    services_id = conn.execute("SELECT id FROM project_tasks WHERE task_code = 'HH-300'").fetchone()[0]
    energex_tasks = [
        (project_id, services_id, 'Energex PMT Lead-Time', 'HH-322', 3, 1, 150, '2026-03-26', '2026-10-21', 0, 'Not Started', 'Energex', 1, 0, 'Critical long-lead item - order ASAP!'),
        (project_id, services_id, 'Energex PMT Install', 'HH-323', 3, 2, 5, '2026-10-22', '2026-10-28', 0, 'Not Started', 'Energex', 1, 85000, 'Depends on PMT delivery'),
    ]

    for task in energex_tasks:
        conn.execute("""
            INSERT INTO project_tasks 
            (project_id, parent_task_id, task_name, task_code, wbs_level, sort_order,
             duration_days, start_date, finish_date, completion_percentage, status,
             assigned_contractor, is_critical, estimated_cost, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, task)

    conn.commit()
    conn.close()

def get_projects():
    """获取所有项目"""
    conn = get_db_connection()
    if not table_exists(conn, "projects"):
        conn.close()
        return pd.DataFrame()

    has_is_active = column_exists(conn, "projects", "is_active")
    df = pd.read_sql(
        f"""
        SELECT
            id,
            project_name,
            status,
            planned_start_date,
            actual_start_date,
            planned_completion_date,
            actual_completion_date
            {" , is_active" if has_is_active else ""}
        FROM projects
        {"WHERE COALESCE(is_active, 1) = 1" if has_is_active else ""}
        """,
        conn
    )
    conn.close()

    if df.empty:
        return df

    start_series = df["actual_start_date"].fillna(df["planned_start_date"])
    completion_series = df["actual_completion_date"].fillna(df["planned_completion_date"])
    df["start_date"] = pd.to_datetime(start_series, errors="coerce")
    df["expected_completion"] = pd.to_datetime(completion_series, errors="coerce")

    today = pd.Timestamp.now().normalize()
    def calc_completion(row):
        if pd.isna(row["start_date"]) or pd.isna(row["expected_completion"]):
            return 0.0
        if row["expected_completion"] <= today:
            return 100.0
        total_days = (row["expected_completion"] - row["start_date"]).days
        if total_days <= 0:
            return 0.0
        elapsed_days = (today - row["start_date"]).days
        return max(0.0, min(100.0, (elapsed_days / total_days) * 100))

    df["completion_percentage"] = df.apply(calc_completion, axis=1)
    return df

def get_project_tasks(project_id, wbs_level=None):
    """
    获取项目的所有任务
    wbs_level: None=全部, 1=项目级, 2=阶段级, 3=任务级
    """
    conn = get_db_connection()
    if not table_exists(conn, "project_tasks"):
        conn.close()
        return pd.DataFrame()

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
    if not table_exists(conn, "project_tasks"):
        conn.close()
        return []
    
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

def create_task_template():
    """生成Excel任务导入模板（含示例数据）"""
    template_data = {
        "Task Name": [
            "DESIGN & APPROVALS",
            "Building Approval",
            "Plumbing & Drainage Approval",
            "QFES Approval",
            "MOBILISATION & EARLY WORKS",
            "Site Setup",
            "Bulk Earthworks",
            "MAIN BUILDING",
            "FRPC Footings",
            "Tilt Panel Casting",
        ],
        "Task Code": [
            "HH-100",
            "HH-101",
            "HH-102",
            "HH-103",
            "HH-200",
            "HH-201",
            "HH-202",
            "HH-300",
            "HH-301",
            "HH-302",
        ],
        "WBS Level": [2, 3, 3, 3, 2, 3, 3, 2, 3, 3],
        "Parent Task Code": [
            "", "HH-100", "HH-100", "HH-100",
            "", "HH-200", "HH-200",
            "", "HH-300", "HH-300",
        ],
        "Duration (days)": [51, 50, 50, 50, 53, 5, 10, 117, 15, 25],
        "Start Date": [
            "2025-01-10", "2025-01-10", "2025-01-10", "2025-01-10",
            "2025-11-24", "2025-11-24", "2025-12-01",
            "2026-04-30", "2026-04-30", "2026-05-20",
        ],
        "Assigned Contractor": [
            "", "Logan City Council", "Council", "QFES",
            "", "Site Contractor", "Earthworks Co",
            "", "Concrete Contractor", "Precast Supplier",
        ],
        "Status": [
            "In Progress", "In Progress", "In Progress", "In Progress",
            "Not Started", "Not Started", "Not Started",
            "Not Started", "Not Started", "Not Started",
        ],
        "Completion %": [60, 80, 60, 40, 0, 0, 0, 0, 0, 0],
        "Is Critical": [1, 1, 1, 1, 0, 0, 0, 1, 1, 1],
        "Estimated Cost": [0, 15000, 8000, 5000, 0, 12000, 35000, 0, 85000, 250000],
        "Notes": [
            "Critical approvals phase",
            "Required for construction",
            "",
            "",
            "Early works preparation",
            "Fencing and signage",
            "10 days of excavation",
            "Main building structure",
            "Foundation work",
            "Precast panels - 25 days cure time",
        ],
    }
    return pd.DataFrame(template_data)

def validate_excel_tasks(df):
    required_columns = ["Task Name", "WBS Level", "Duration (days)", "Start Date"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return [f"Missing required columns: {', '.join(missing_columns)}"], df

    cleaned_df = df.copy()
    cleaned_df["Task Name"] = cleaned_df["Task Name"].astype(str).str.strip()
    cleaned_df = cleaned_df[cleaned_df["Task Name"].str.len() > 0]

    errors = []

    cleaned_df["WBS Level"] = pd.to_numeric(cleaned_df["WBS Level"], errors="coerce")
    invalid_wbs = cleaned_df[~cleaned_df["WBS Level"].isin([1, 2, 3])]
    if not invalid_wbs.empty:
        errors.append("WBS Level must be 1, 2, or 3.")

    cleaned_df["Duration (days)"] = pd.to_numeric(cleaned_df["Duration (days)"], errors="coerce")
    invalid_duration = cleaned_df[cleaned_df["Duration (days)"].isna() | (cleaned_df["Duration (days)"] <= 0)]
    if not invalid_duration.empty:
        errors.append("Duration (days) must be a positive number.")

    cleaned_df["Start Date"] = pd.to_datetime(cleaned_df["Start Date"], errors="coerce")
    invalid_dates = cleaned_df[cleaned_df["Start Date"].isna()]
    if not invalid_dates.empty:
        errors.append("Start Date must be a valid date (YYYY-MM-DD).")

    return errors, cleaned_df

def import_tasks_from_excel(df, project_id):
    init_task_table()
    conn = get_db_connection()

    task_code_map = {}
    parent_links = []
    imported_count = 0

    for idx, row in df.iterrows():
        task_name = str(row["Task Name"]).strip()
        if not task_name:
            continue

        start_date = pd.to_datetime(row["Start Date"]).date()
        duration = int(row["Duration (days)"])
        finish_date = start_date + timedelta(days=duration)

        task_code = str(row.get("Task Code", f"T-{idx}")).strip() if pd.notna(row.get("Task Code")) else f"T-{idx}"
        wbs_level = int(row["WBS Level"])
        parent_code = ""
        if "Parent Task Code" in df.columns and pd.notna(row.get("Parent Task Code")):
            parent_code = str(row["Parent Task Code"]).strip()

        assigned_contractor = row.get("Assigned Contractor", "")
        status = row.get("Status", "Not Started")
        completion = float(row.get("Completion %", 0) or 0)
        is_critical = row.get("Is Critical", 0)
        try:
            is_critical = int(is_critical)
        except Exception:
            is_critical = 1 if str(is_critical).strip().upper() in ["Y", "YES", "TRUE", "1"] else 0
        estimated_cost = float(row.get("Estimated Cost", 0) or 0)
        notes = row.get("Notes", "")

        conn.execute("""
            INSERT INTO project_tasks 
            (project_id, task_name, task_code, wbs_level, parent_task_id,
             duration_days, start_date, finish_date, assigned_contractor,
             status, completion_percentage, is_critical, estimated_cost, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id,
            task_name,
            task_code,
            wbs_level,
            None,
            duration,
            start_date,
            finish_date,
            assigned_contractor,
            status,
            completion,
            is_critical,
            estimated_cost,
            notes,
        ))

        task_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        if task_code:
            task_code_map[task_code] = task_id
        if parent_code:
            parent_links.append((task_id, parent_code))

        imported_count += 1

    for task_id, parent_code in parent_links:
        parent_id = task_code_map.get(parent_code)
        if parent_id:
            conn.execute(
                "UPDATE project_tasks SET parent_task_id = ? WHERE id = ?",
                (parent_id, task_id)
            )

    conn.commit()
    conn.close()
    return imported_count

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
    
    for _, row in df_gantt.iterrows():
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

init_task_table()

st.title("📊 Professional Project Gantt Chart")

projects = get_projects()

with st.sidebar:
    st.header("🛠️ Quick Start")
    
    if projects.empty:
        if st.button("➕ Create Heathwood Hub Example", type="primary"):
            load_heathwood_example()
            st.success("✅ Example data loaded!")
            st.rerun()
    else:
        project_labels = {
            row["id"]: f"{row['project_name']} (ID {row['id']})"
            for _, row in projects.iterrows()
        }
        quick_project = st.selectbox(
            "Select project for example data:",
            projects["id"].tolist(),
            format_func=lambda pid: project_labels.get(pid, str(pid)),
            key="quick_project"
        )
        if st.button("➕ Load Heathwood Hub Example", type="primary"):
            load_heathwood_example(quick_project)
            st.success("✅ Example data loaded!")
            st.rerun()
    
    st.divider()
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

if projects.empty:
    st.info("📝 No projects found. Please add projects first in Data Input Center.")
    st.stop()

# 项目选择
col1, col2 = st.columns([3, 1])

with col1:
    project_labels = {
        row["id"]: f"{row['project_name']} (ID {row['id']})"
        for _, row in projects.iterrows()
    }
    selected_project_id = st.selectbox(
        "Select Project:",
        projects["id"].tolist(),
        format_func=lambda pid: project_labels.get(pid, str(pid))
    )

with col2:
    view_mode = st.selectbox(
        "View Mode:",
        ["All Levels", "Phases Only", "Tasks Only"]
    )

# 获取选中项目的ID
project_row = projects[projects["id"] == selected_project_id].iloc[0]
project_id = selected_project_id

# 显示项目摘要
st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Project Status", project_row['status'] or "Unknown")
with col2:
    st.metric("Overall Progress", f"{project_row['completion_percentage']:.0f}%")
with col3:
    start_value = project_row["start_date"]
    st.metric("Start Date", start_value.strftime("%Y-%m-%d") if pd.notna(start_value) else "N/A")
with col4:
    completion_value = project_row["expected_completion"]
    st.metric("Target Completion", completion_value.strftime("%Y-%m-%d") if pd.notna(completion_value) else "N/A")

# 获取任务数据
tasks_df = get_project_tasks(project_id)

# 视图选择标签
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Gantt Chart", 
    "📋 Task List", 
    "🎯 Critical Path",
    "➕ Add Tasks"
])

# Tab 1: 甘特图
with tab1:
    if not tasks_df.empty:
        level_map = {
            "All Levels": "all",
            "Phases Only": "phases",
            "Tasks Only": "tasks"
        }
        
        show_level = level_map[view_mode]
        
        with st.spinner("Generating Gantt Chart..."):
            fig = create_hierarchical_gantt(tasks_df, show_level)
            
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("🟦 **Project Level**")
                with col2:
                    st.markdown("🟧 **Phase Level**")
                with col3:
                    st.markdown("🟩 **Task Level**")
                
                st.markdown("🟥 **Red Border = Critical Path**")
    else:
        st.warning("📝 No detailed tasks found for this project")
        st.markdown("""
        ### How to add tasks?
        
        1. Click **"Load Heathwood Hub Example"** in the sidebar to see a sample
        2. Or use the **"Add Tasks"** tab to create your own
        3. Or import from MS Project (coming soon)
        """)

# Tab 2: 任务列表
with tab2:
    if not tasks_df.empty:
        st.subheader("📋 Task Breakdown")
        
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
        
        filtered_df = tasks_df[
            (tasks_df['status'].isin(status_filter)) &
            (tasks_df['wbs_level'].isin(level_filter))
        ]
        
        if show_critical_only:
            filtered_df = filtered_df[filtered_df['is_critical'] == 1]
        
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
    else:
        st.info("No tasks to display. Load example data or add tasks manually.")

# Tab 3: 关键路径
with tab3:
    critical_tasks = tasks_df[tasks_df['is_critical'] == 1] if not tasks_df.empty else pd.DataFrame()
    
    if not critical_tasks.empty:
        st.subheader("🎯 Critical Path Analysis")
        st.info(f"Found {len(critical_tasks)} tasks on the critical path")
        
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
        st.info("No critical path tasks defined yet")

# Tab 4: 添加任务
with tab4:
    st.subheader("➕ Add Tasks")

    input_method = st.radio(
        "Choose input method:",
        ["📝 Single Task", "📊 Excel Batch Import", "📋 Quick List"],
        horizontal=True
    )

    if input_method == "📝 Single Task":
        with st.form("add_task_form"):
            col1, col2 = st.columns(2)

            with col1:
                task_name = st.text_input("Task Name *")
                task_code = st.text_input("Task Code (e.g., HH-101)")
                wbs_level = st.selectbox("WBS Level", [2, 3], format_func=lambda x: "Phase" if x == 2 else "Task")

            with col2:
                duration = st.number_input("Duration (days) *", min_value=1, value=10)
                start_date = st.date_input("Start Date *")
                contractor = st.text_input("Assigned Contractor")

            col3, col4 = st.columns(2)

            with col3:
                is_critical = st.checkbox("On Critical Path?")

            with col4:
                estimated_cost = st.number_input("Estimated Cost (AUD)", min_value=0.0, step=1000.0)

            notes = st.text_area("Notes")

            submitted = st.form_submit_button("💾 Add Task", type="primary")

            if submitted:
                if not task_name:
                    st.error("Task name is required")
                else:
                    finish_date = start_date + timedelta(days=duration)

                    try:
                        conn = get_db_connection()
                        conn.execute("""
                            INSERT INTO project_tasks 
                            (project_id, task_name, task_code, wbs_level, duration_days,
                             start_date, finish_date, assigned_contractor, is_critical,
                             estimated_cost, notes, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Not Started')
                        """, (
                            project_id, task_name, task_code, wbs_level, duration,
                            start_date, finish_date, contractor, int(is_critical),
                            estimated_cost, notes
                        ))

                        conn.commit()
                        conn.close()

                        st.success(f"✅ Task '{task_name}' added successfully!")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"❌ Error adding task: {str(exc)}")

    elif input_method == "📊 Excel Batch Import":
        st.markdown("### 📥 Import Tasks from Excel")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.info(
                "**Steps:**\n"
                "1. Download the template\n"
                "2. Fill in your tasks\n"
                "3. Upload the file\n"
                "4. Review and import"
            )

            template_df = create_task_template()
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                template_df.to_excel(writer, sheet_name="Tasks", index=False)
                instructions = pd.DataFrame({
                    "Column": [
                        "Task Name", "Task Code", "WBS Level", "Parent Task Code",
                        "Duration (days)", "Start Date", "Status", "Is Critical"
                    ],
                    "Description": [
                        "Name of the task (required)",
                        "Unique code like HH-101 (optional but recommended)",
                        "1=Project, 2=Phase, 3=Task (required)",
                        "Parent task code for hierarchy (optional)",
                        "Number of days (required)",
                        "YYYY-MM-DD format (required)",
                        "Not Started, In Progress, Completed, Delayed",
                        "1=Yes, 0=No (also accepts Y/N)"
                    ]
                })
                instructions.to_excel(writer, sheet_name="Instructions", index=False)

            st.download_button(
                label="📥 Download Template",
                data=output.getvalue(),
                file_name=f"task_import_template_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )

        with col2:
            st.warning(
                "**Important:**\n"
                "- Do NOT change column names\n"
                "- Task Code should be unique\n"
                "- Parent Task Code must exist in the file\n"
                "- Date format: YYYY-MM-DD"
            )

        st.divider()

        uploaded_file = st.file_uploader(
            "Upload your completed Excel file",
            type=["xlsx", "xls"],
            help="Upload the template file with your task data"
        )

        if uploaded_file:
            try:
                uploaded_file.seek(0)
                preview_df = pd.read_excel(uploaded_file)
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                st.metric("Rows found", len(preview_df))

                with st.expander("📋 Preview Data", expanded=True):
                    st.dataframe(preview_df, use_container_width=True)

                validation_errors, cleaned_df = validate_excel_tasks(preview_df)
                st.subheader("🔍 Validation")
                if validation_errors:
                    for err in validation_errors:
                        st.error(err)
                else:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Phases (Level 2)", len(cleaned_df[cleaned_df["WBS Level"] == 2]))
                    with col2:
                        st.metric("Tasks (Level 3)", len(cleaned_df[cleaned_df["WBS Level"] == 3]))
                    with col3:
                        critical = cleaned_df["Is Critical"].sum() if "Is Critical" in cleaned_df.columns else 0
                        st.metric("Critical Tasks", int(critical))

                st.divider()

                if not validation_errors and st.button("🚀 Import All Tasks", type="primary", use_container_width=True):
                    with st.spinner("Importing tasks..."):
                        imported = import_tasks_from_excel(cleaned_df, project_id)
                        st.success(f"✅ Successfully imported {imported} tasks")
                        st.rerun()
            except Exception as exc:
                st.error(f"❌ Error reading file: {str(exc)}")

    else:  # Quick List
        st.markdown("### ⚡ Quick List Entry")
        st.info(
            "Enter tasks one per line in this format:\n"
            "`Task Name | Duration | Contractor | Critical (Y/N)`\n\n"
            "Example:\n"
            "Building Approval | 50 | Logan Council | Y\n"
            "Site Setup | 5 | ABC Contractors | N\n"
            "FRPC Footings | 15 | Concrete Co | Y"
        )

        task_list = st.text_area(
            "Enter your tasks:",
            height=260,
            placeholder="Building Approval | 50 | Logan Council | Y\nSite Setup | 5 | ABC Contractors | N"
        )

        col1, col2 = st.columns(2)
        with col1:
            default_start = st.date_input("Default Start Date", datetime.now())
        with col2:
            default_wbs = st.selectbox("Default WBS Level", [2, 3], format_func=lambda x: "Phase" if x == 2 else "Task")

        if st.button("🚀 Import Task List", type="primary"):
            lines = [line.strip() for line in task_list.split("\n")]
            parsed = []

            for line in lines:
                if not line:
                    continue
                if "|" in line:
                    parts = [p.strip() for p in line.split("|")]
                else:
                    parts = [line.strip()]

                task_name = parts[0] if len(parts) > 0 else ""
                if not task_name:
                    continue

                duration = 10
                if len(parts) > 1 and parts[1]:
                    try:
                        duration = int(float(parts[1]))
                    except Exception:
                        duration = 10

                contractor = parts[2] if len(parts) > 2 else ""

                critical_token = parts[3] if len(parts) > 3 else ""
                is_critical = 1 if str(critical_token).strip().upper() in ["Y", "YES", "TRUE", "1"] else 0

                parsed.append((task_name, duration, contractor, is_critical))

            if not parsed:
                st.warning("Please enter at least one task")
            else:
                conn = get_db_connection()
                current_date = pd.to_datetime(default_start).date()

                for task_name, duration, contractor, is_critical in parsed:
                    finish_date = current_date + timedelta(days=duration)
                    conn.execute("""
                        INSERT INTO project_tasks
                        (project_id, task_name, wbs_level, duration_days,
                         start_date, finish_date, assigned_contractor, is_critical, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Not Started')
                    """, (
                        project_id, task_name, default_wbs, duration,
                        current_date, finish_date, contractor, is_critical
                    ))
                    current_date = finish_date

                conn.commit()
                conn.close()

                st.success(f"✅ Imported {len(parsed)} tasks!")
                st.rerun()
