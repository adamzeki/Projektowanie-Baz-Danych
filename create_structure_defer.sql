CREATE TABLE absence_type (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  paid BOOLEAN NOT NULL
);

CREATE TABLE absence (
  id SERIAL PRIMARY KEY,
  FK_employee INT NOT NULL,
  date_from DATE NOT NULL,
  date_to DATE,
  FK_absence_type INT NOT NULL REFERENCES absence_type ON DELETE RESTRICT,
  CHECK (date_to IS NULL OR date_to >= date_from)
);

CREATE TABLE skill_type (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE competence (
  id SERIAL PRIMARY KEY,
  FK_employee INT NOT NULL,
  FK_skill_type INT NOT NULL REFERENCES skill_type ON DELETE RESTRICT,
  level DECIMAL(1) NOT NULL CHECK (level >= 0 AND level <= 5)
);

CREATE TABLE project_role (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE project_assignment (
  id SERIAL PRIMARY KEY,
  FK_employee INT NOT NULL,
  FK_project INT NOT NULL,
  FK_project_role INT REFERENCES project_role ON DELETE RESTRICT,
  date_start DATE NOT NULL,
  date_end DATE,
  CHECK (date_end IS NULL OR date_end > date_start)
);

CREATE TABLE work_schedule (
  id SERIAL PRIMARY KEY,
  FK_project_assignment INT NOT NULL REFERENCES project_assignment ON DELETE CASCADE,
  weekday DECIMAL(1) NOT NULL,
  time_from TIME(0) NOT NULL,
  time_to TIME(0) NOT NULL,
  CHECK (weekday >= 0 AND weekday < 7),
  CHECK (time_from < time_to)
);

CREATE TABLE monthly_score (
  id SERIAL PRIMARY KEY,
  FK_project_assignment INT NOT NULL REFERENCES project_assignment ON DELETE CASCADE,
  score DECIMAL(1) NOT NULL CHECK (score >= 0 AND score <= 10),
  date_of DATE NOT NULL
);

CREATE TABLE employee (
  id serial PRIMARY KEY,
  login VARCHAR(100) NOT NULL,
  user_password VARCHAR(100) NOT NULL,
  permission_type SMALLINT NOT NULL CHECK (permission_type >= 0 AND permission_type <= 2),
  name varchar(100) NOT NULL,
  surname varchar(100) NOT NULL,
  telephone VARCHAR(15),
  fk_department INTEGER
);

CREATE TABLE department (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  address VARCHAR(100) NOT NULL,
  fk_head_employee INTEGER
);

CREATE TABLE work_session (
  id SERIAL PRIMARY KEY,
  time_from TIMESTAMP NOT NULL,
  time_to TIMESTAMP,
  fk_employee INTEGER NOT NULL,
  fk_start_terminal INTEGER NOT NULL,
  fk_end_terminal INTEGER,
  fk_project INTEGER NOT NULL,
  CHECK (time_to IS NULL OR time_from < time_to)
);

CREATE TABLE project (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  fk_overseer_employee INTEGER,
  fk_location INTEGER
);

CREATE TABLE location_table (
  id SERIAL PRIMARY KEY,
  address VARCHAR(100),
  name VARCHAR(100)
);

CREATE TABLE terminal (
  id SERIAL PRIMARY KEY,
  fk_location INTEGER NOT NULL
);

ALTER TABLE employee
  ADD CONSTRAINT fk_department
  FOREIGN KEY (fk_department)
  REFERENCES department (id)
  ON DELETE RESTRICT
  DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE department
  ADD CONSTRAINT fk_head_employee
  FOREIGN KEY (fk_head_employee)
  REFERENCES employee (id)
  ON DELETE SET NULL
  DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE work_session
  ADD CONSTRAINT fk_employee
  FOREIGN KEY (fk_employee)
  REFERENCES employee (id)
  ON DELETE CASCADE;

ALTER TABLE work_session
  ADD CONSTRAINT fk_start_terminal
  FOREIGN KEY (fk_start_terminal)
  REFERENCES terminal (id)
  ON DELETE RESTRICT;

ALTER TABLE work_session
  ADD CONSTRAINT fk_end_terminal
  FOREIGN KEY (fk_end_terminal)
  REFERENCES terminal (id)
  ON DELETE RESTRICT;

ALTER TABLE work_session
  ADD CONSTRAINT fk_project
  FOREIGN KEY (fk_project)
  REFERENCES project (id)
  ON DELETE CASCADE;

ALTER TABLE terminal
  ADD CONSTRAINT fk_location
  FOREIGN KEY (fk_location)
  REFERENCES location_table (id)
  ON DELETE RESTRICT;

ALTER TABLE project
  ADD CONSTRAINT fk_overseer_employee
  FOREIGN KEY (fk_overseer_employee)
  REFERENCES employee (id)
  ON DELETE SET NULL;

ALTER TABLE project
  ADD CONSTRAINT fk_location
  FOREIGN KEY (fk_location)
  REFERENCES location_table (id)
  ON DELETE RESTRICT;

ALTER TABLE competence
  ADD CONSTRAINT fk_employee
  FOREIGN KEY (fk_employee)
  REFERENCES employee (id)
  ON DELETE CASCADE;

ALTER TABLE absence
  ADD CONSTRAINT fk_employee
  FOREIGN KEY (fk_employee)
  REFERENCES employee (id)
  ON DELETE CASCADE;

ALTER TABLE project_assignment
  ADD CONSTRAINT fk_employee
  FOREIGN KEY (fk_employee)
  REFERENCES employee (id)
  ON DELETE CASCADE;

ALTER TABLE project_assignment
  ADD CONSTRAINT fk_project
  FOREIGN KEY (fk_project)
  REFERENCES project (id)
  ON DELETE CASCADE;
