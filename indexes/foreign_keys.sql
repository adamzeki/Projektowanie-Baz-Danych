CREATE INDEX absence_fk_employee ON absence (fk_employee);
CREATE INDEX absence_fk_absence_type ON absence (fk_absence_type);
CREATE INDEX competence_fk_employee ON competence (fk_employee);
CREATE INDEX competence_fk_skill_type ON competence (fk_skill_type);
CREATE INDEX employee_fk_department ON employee (fk_department);
CREATE INDEX monthly_score_fk_project_assignment ON monthly_score (fk_project_assignment);
CREATE INDEX project_fk_overseer_employee ON project (fk_overseer_employee);
CREATE INDEX project_fk_location ON project (fk_location);
CREATE INDEX project_assignment_fk_employee ON project_assignment (fk_employee);
CREATE INDEX project_assignment_fk_project ON project_assignment (fk_project);
CREATE INDEX project_assignment_fk_project_role ON project_assignment (fk_project_role);
CREATE INDEX work_schedule_fk_project_assignment ON work_schedule (fk_project_assignment);
CREATE INDEX work_session_fk_employee ON work_session (fk_employee);
CREATE INDEX work_session_fk_start_terminal ON work_session (fk_start_terminal);
CREATE INDEX work_session_fk_end_terminal ON work_session (fk_end_terminal);
CREATE INDEX work_session_fk_project ON work_session (fk_project);

-- the indexes below may not be useful - the tables have few records
CREATE INDEX terminal_fk_location ON terminal (fk_location);
CREATE INDEX department_fk_head_employee ON department (fk_head_employee);