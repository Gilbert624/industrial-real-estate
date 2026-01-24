-- 项目任务表 (详细的甘特图数据)
CREATE TABLE IF NOT EXISTS project_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    
    -- 任务基本信息
    task_name TEXT NOT NULL,
    task_code TEXT,  -- 例如: "3.2.1" 或 "MAIN-001"
    description TEXT,
    
    -- 层级结构
    parent_task_id INTEGER,  -- 父任务ID，实现树形结构
    wbs_level INTEGER DEFAULT 1,  -- 1=项目, 2=阶段, 3=任务
    sort_order INTEGER,  -- 显示顺序
    
    -- 时间管理
    duration_days INTEGER NOT NULL,
    start_date DATE NOT NULL,
    finish_date DATE NOT NULL,
    actual_start_date DATE,
    actual_finish_date DATE,
    
    -- 依赖关系
    predecessor_ids TEXT,  -- 存储JSON: ["task_5", "task_12"]
    dependency_type TEXT DEFAULT 'FS',  -- FS, SS, FF, SF
    lag_days INTEGER DEFAULT 0,
    
    -- 进度追踪
    completion_percentage REAL DEFAULT 0,
    status TEXT DEFAULT 'Not Started',  -- Not Started, In Progress, Completed, Delayed
    
    -- 资源分配
    assigned_contractor TEXT,
    estimated_cost REAL,
    actual_cost REAL,
    
    -- 关键路径
    is_critical BOOLEAN DEFAULT 0,
    total_float_days INTEGER,
    
    -- 元数据
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (parent_task_id) REFERENCES project_tasks(id)
);

-- 索引优化
CREATE INDEX idx_tasks_project ON project_tasks(project_id);
CREATE INDEX idx_tasks_parent ON project_tasks(parent_task_id);
CREATE INDEX idx_tasks_status ON project_tasks(status);
CREATE INDEX idx_tasks_critical ON project_tasks(is_critical);

-- 示例数据: Heathwood Hub项目
INSERT INTO project_tasks (project_id, task_name, task_code, wbs_level, duration_days, start_date, finish_date, completion_percentage, status, is_critical) VALUES
-- Level 1: 主项目
(1, 'HEATHWOOD HUB', 'HH-000', 1, 1, '2025-01-10', '2025-01-10', 0, 'In Progress', 0),

-- Level 2: 主要阶段
(1, 'DESIGN & APPROVALS', 'HH-100', 2, 51, '2025-01-10', '2025-12-10', 60, 'In Progress', 1),
(1, 'MOBILISATION & EARLY WORKS', 'HH-200', 2, 53, '2025-11-24', '2026-02-25', 0, 'Not Started', 0),
(1, 'EXTERNAL SERVICES', 'HH-300', 2, 175, '2026-02-26', '2026-10-28', 0, 'Not Started', 1),
(1, 'MAIN BUILDING', 'HH-400', 2, 117, '2026-04-30', '2026-10-09', 0, 'Not Started', 1),
(1, 'OFFICE BUILDINGS', 'HH-500', 2, 133, '2026-05-21', '2026-11-23', 0, 'Not Started', 0),
(1, 'EXTERNAL WORKS', 'HH-600', 2, 60, '2026-09-07', '2026-11-27', 0, 'Not Started', 0),
(1, 'CLOSE OUT', 'HH-700', 2, 17, '2026-11-24', '2026-12-16', 0, 'Not Started', 0);

-- Level 3: 详细任务 (示例部分)
-- DESIGN & APPROVALS 下的任务
INSERT INTO project_tasks (project_id, parent_task_id, task_name, task_code, wbs_level, duration_days, start_date, finish_date, completion_percentage, status, assigned_contractor, is_critical) VALUES
(1, (SELECT id FROM project_tasks WHERE task_code='HH-100'), 'Building Approval', 'HH-106', 3, 50, '2025-01-10', '2025-12-09', 80, 'In Progress', 'Logan City Council', 1),
(1, (SELECT id FROM project_tasks WHERE task_code='HH-100'), 'Plumbing & Drainage Approval', 'HH-104', 3, 50, '2025-01-10', '2025-12-09', 60, 'In Progress', 'Council', 1),
(1, (SELECT id FROM project_tasks WHERE task_code='HH-100'), 'QFES Approval', 'HH-105', 3, 50, '2025-01-10', '2025-12-09', 40, 'In Progress', 'QFES', 1),
(1, (SELECT id FROM project_tasks WHERE task_code='HH-100'), 'QUU Approval', 'HH-107', 3, 50, '2025-01-10', '2025-12-09', 50, 'In Progress', 'QUU', 0);

-- MAIN BUILDING 下的任务
INSERT INTO project_tasks (project_id, parent_task_id, task_name, task_code, wbs_level, duration_days, start_date, finish_date, completion_percentage, status, assigned_contractor, estimated_cost, is_critical, predecessor_ids) VALUES
(1, (SELECT id FROM project_tasks WHERE task_code='HH-400'), 'FRPC Footings', 'HH-432', 3, 15, '2026-04-30', '2026-05-20', 0, 'Not Started', 'Concrete Contractor', 85000, 1, '["HH-300"]'),
(1, (SELECT id FROM project_tasks WHERE task_code='HH-400'), 'Cast & Cure Tilt Panels', 'HH-433', 3, 25, '2026-04-30', '2026-06-03', 0, 'Not Started', 'Precast Supplier', 250000, 1, '["HH-432"]'),
(1, (SELECT id FROM project_tasks WHERE task_code='HH-400'), 'Stand Tilt Panels', 'HH-434', 3, 7, '2026-06-04', '2026-06-12', 0, 'Not Started', 'Crane Operator', 45000, 1, '["HH-433"]'),
(1, (SELECT id FROM project_tasks WHERE task_code='HH-400'), 'Structural Steel Install', 'HH-435', 3, 20, '2026-06-15', '2026-07-10', 0, 'Not Started', 'Steel Erector', 320000, 1, '["HH-434"]'),
(1, (SELECT id FROM project_tasks WHERE task_code='HH-400'), 'Roofing & Cladding', 'HH-436', 3, 25, '2026-07-13', '2026-08-14', 0, 'Not Started', 'Roofing Contractor', 180000, 1, '["HH-435"]');

-- EXTERNAL SERVICES 关键任务
INSERT INTO project_tasks (project_id, parent_task_id, task_name, task_code, wbs_level, duration_days, start_date, finish_date, completion_percentage, status, assigned_contractor, estimated_cost, is_critical, notes) VALUES
(1, (SELECT id FROM project_tasks WHERE task_code='HH-300'), 'Energex PMT Lead-Time', 'HH-322', 3, 150, '2026-03-26', '2026-10-21', 0, 'Not Started', 'Energex', 0, 1, 'Critical long-lead item - order ASAP'),
(1, (SELECT id FROM project_tasks WHERE task_code='HH-300'), 'Energex PMT Install', 'HH-323', 3, 5, '2026-10-22', '2026-10-28', 0, 'Not Started', 'Energex', 85000, 1, 'Depends on PMT delivery');
