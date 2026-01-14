-- Liczba różnych lokacji, w których pracował pracownik (wersja wolna)
-- 12 -> 10s
SELECT employee.id, employee.login, employee.name, employee.surname, COUNT(DISTINCT location_table.id) AS location_count
FROM employee
LEFT JOIN work_session ON employee.id = work_session.fk_employee
LEFT JOIN terminal AS start_terminal ON work_session.fk_start_terminal = start_terminal.id
LEFT JOIN terminal AS end_terminal ON work_session.fk_end_terminal = end_terminal.id
LEFT JOIN location_table ON start_terminal.fk_location = location_table.id OR end_terminal.fk_location = location_table.id
GROUP BY employee.id
ORDER BY location_count DESC;

-- Liczba różnych lokacji, w których pracował pracownik (wersja zoptymalizowana 12s -> 7s), pozbywamy się ORa
-- 7s -> 7s
WITH employee_locations AS (
    SELECT 
        ws.fk_employee, 
        t.fk_location AS location_id
    FROM work_session ws
    JOIN terminal t ON ws.fk_start_terminal = t.id
    WHERE t.fk_location IS NOT NULL

    UNION

    SELECT 
        ws.fk_employee, 
        t.fk_location AS location_id
    FROM work_session ws
    JOIN terminal t ON ws.fk_end_terminal = t.id
    WHERE t.fk_location IS NOT NULL
)
SELECT
    e.id,
    e.login,
    e.name,
    e.surname,
    COUNT(el.location_id) AS location_count
FROM employee e
LEFT JOIN employee_locations el ON e.id = el.fk_employee
GROUP BY e.id
ORDER BY location_count DESC;

-- Stosunek aktywnych do zakończonych assignmentów w projektach
-- <0.1s
SELECT 
    active_count,
    finished_count,
    CASE 
        WHEN finished_count = 0 THEN -1 
        ELSE active_count::float / finished_count 
    END AS active_finished_ratio
FROM (
    SELECT 
        SUM(CASE WHEN project_assignment.date_end IS NULL THEN 1 END) AS active_count,
        SUM(CASE WHEN project_assignment.date_end IS NOT NULL THEN 1 END) AS finished_count
    FROM project
    LEFT JOIN project_assignment ON project.id = project_assignment.fk_project
    GROUP BY project.id
) AS subquery
ORDER BY active_finished_ratio DESC;

-- Sesje pracy, które odbyły się innego dnia, niż zaplanowane work schedule
-- 1.9s -> 1.9s
SELECT work_session.*
FROM work_session
INNER JOIN project ON work_session.fk_project = project.id
LEFT JOIN
    project_assignment
        ON project.id = project_assignment.fk_project
        AND work_session.fk_employee = project_assignment.fk_employee
LEFT JOIN
    work_schedule
        ON project_assignment.id = work_schedule.fk_project_assignment
        AND work_schedule.time_from <= work_session.time_from::time
        AND (work_session.time_to IS NULL OR work_schedule.time_to >= work_session.time_to::time)
        AND EXTRACT(ISODOW FROM work_session.time_from) - 1 = work_schedule.weekday
WHERE work_schedule.id IS NULL;

-- Zróżnicowanie kompetencji w różnych departamentach – ile średnio kompetencji przypada na jednego pracownika
-- 0.1s
SELECT department.id, department.name, AVG(competence_count) AS avg_competence_types_per_employee
FROM (
    SELECT COUNT(competence.id) AS competence_count, fk_department
    FROM employee
    LEFT JOIN competence ON employee.id = competence.fk_employee
    GROUP BY employee.id, employee.fk_department
) AS subquery
INNER JOIN department ON fk_department = department.id
GROUP BY department.id
ORDER BY avg_competence_types_per_employee DESC;

-- Pracownicy, którzy najwyższy poziom danej kompetencji w projekcie
-- 12s -> 9s
SELECT
    employee.id,
    employee.login,
    employee.name,
    employee.surname,
    project.id,
    project.name AS project_name,
    skill_type.id,
    skill_type.name AS skill_type
FROM employee
INNER JOIN project_assignment ON employee.id = project_assignment.fk_employee
INNER JOIN project ON project_assignment.fk_project = project.id
INNER JOIN competence ON employee.id = competence.fk_employee
INNER JOIN skill_type ON competence.fk_skill_type = skill_type.id
LEFT JOIN project_assignment AS others_assignment
    ON project_assignment.fk_project = others_assignment.fk_project
    AND project_assignment.fk_employee != others_assignment.fk_employee
LEFT JOIN competence AS others_competence
    ON others_assignment.fk_employee = others_competence.fk_employee
    AND competence.fk_skill_type = others_competence.fk_skill_type
    AND competence.level < others_competence.level
GROUP BY employee.id, project.id, project.name, skill_type.id, skill_type.name
HAVING COUNT(others_competence.id) = 0;

-- Porównanie, ile work session odbywa się w głównej lokacji projektu, a ile poza nią
-- 1s -> 0.9s
SELECT
    project.id,
    project.name,
    SUM(case terminal.fk_location when project.fk_location then 1 else 0 end) AS main_location,
    SUM(case terminal.fk_location when project.fk_location then 0 else 1 end) AS off_site
FROM project
INNER JOIN work_session ON project.id = work_session.fk_project
INNER JOIN terminal ON work_session.fk_start_terminal = terminal.id
GROUP BY project.id, project.name;

-- Sredni score pracownika we wszystkich projektach --
-- <0.1s
SELECT
	e.id,
	e.name,
	e.surname,
	p.id,
	p.name,
	p_r.name,
	AVG(m_s.score) as avg_score
FROM
	employee e
INNER JOIN
	project_assignment p_a ON e.id = p_a.fk_employee
INNER JOIN
	project p ON p_a.fk_project = p.id
INNER JOIN
	project_role p_r ON p_a.fk_project_role = p_r.id
INNER JOIN
	monthly_score m_s ON m_s.fk_project_assignment = p_a.id
WHERE
	e.id = 1178
GROUP BY
	e.id, e.name, e.surname, p.id, p.name, p_r.name
ORDER BY
	avg_score DESC;

-- Ilosc dni urlopu ktore wykorzystal pracownik w danym roku --
-- <0.1s
SELECT
	e.id,
	e.name,
	e.surname,
	COALESCE(SUM((a.date_to - a.date_from) + 1), 0) AS vacation_days
FROM
	employee e
LEFT JOIN
	absence a ON e.id = a.fk_employee
LEFT JOIN 
	absence_type a_t ON a.fk_absence_type = a_t.id
WHERE
	LOWER(a_t.name) = 'vacation'
	AND EXTRACT(YEAR FROM a.date_to) = 2024
GROUP BY
	e.id, e.name, e.surname
ORDER BY
	vacation_days ASC;

-- Wszystkie role pelnione przez pracownika --
-- <0.1s
SELECT
	p.id,
	p.name,
	p_r.name
FROM
	project_assignment p_a
INNER JOIN
	project_role p_r ON p_a.fk_project_role = p_r.id
INNER JOIN
	employee e ON p_a.fk_employee = e.id
INNER JOIN
	project p ON p_a.fk_project = p.id
WHERE
	e.id = 1854
GROUP BY
	p.id, p.name, p_r.name
ORDER BY
	p.id ASC, p_r.name ASC;

-- Pracownicy ktorzy w danym okresie byli w danej lokacji --
-- 0.13s -> 0.4s :)
SELECT
	e.id,
	e.name,
	e.surname
FROM
	employee e
INNER JOIN
	work_session w_s ON e.id = w_s.fk_employee
INNER JOIN
	terminal t ON w_s.fk_start_terminal = t.id
INNER JOIN
	location_table l_t ON t.fk_location = l_t.id
WHERE
	l_t.name = 'Bridge'
	AND w_s.time_from > '2024-05-01'
	AND w_s.time_from < '2024-06-01'
GROUP BY
	e.id, e.name, e.surname;

-- Ilosc projektow nadzorowanych przez pracownikow --
-- <0.1s
SELECT
	e.id,
	e.name,
	e.surname,
	COUNT(p.id) AS oversee_count
FROM
	employee e
INNER JOIN
	project p ON e.id = p.fk_overseer_employee
GROUP BY
	e.id, e.name, e.surname
HAVING
	COUNT(p.id) > 0
ORDER BY
	oversee_count ASC;

-- Pracownicy bez zadnych przydzialow projektowych --
-- <0.1s
SELECT
	e.id,
	e.name,
	e.surname
FROM
	employee e
LEFT JOIN
	project_assignment p_a ON e.id = p_a.fk_employee
WHERE
	p_a.id IS NULL
GROUP BY
	e.id, e.name, e.surname;

-- Laczna ilosc godzin ktora pracownik powinien wyrobic tygodniowo --
-- <0.1s
SELECT
	e.id,
	e.name,
	e.surname,
	SUM(
	  	CASE
			WHEN w_sch.time_to < w_sch.time_from
			THEN (w_sch.time_to + INTERVAL '1 day') - w_sch.time_from
			ELSE w_sch.time_to - w_sch.time_from
		END
	) AS weekly_shift
FROM
	work_schedule w_sch
INNER JOIN
	project_assignment p_a ON w_sch.fk_project_assignment = p_a.id
INNER JOIN
	employee e ON p_a.fk_employee = e.id
GROUP BY
	e.id, e.name, e.surname
ORDER BY
	weekly_shift DESC; 

-- lista pracowników pracujących nad wybranym projektem
-- <0.1s
PREPARE get_project_employees(integer) AS
SELECT employee.id, employee.name, employee.surname 
FROM project_assignment JOIN employee ON project_assignment.fk_employee = employee.id 
WHERE date_end IS NULL;

EXECUTE get_project_employees(1);

-- 10 pracowników, którzy przepracowali najwięcej godzin w październiku 2025
-- 0.114s -> 0.240s :)
SELECT employee.id, name, surname, SUM(time_to - time_from) AS time_worked 
FROM employee JOIN work_session ON employee.id = work_session.fk_employee 
WHERE time_from > '2025-10-01' AND time_to < '2025-11-01' GROUP BY employee.id ORDER BY time_worked DESC LIMIT 10;

-- Liczba pracowników dla każdego departamentu
-- <0.1s
SELECT department.id, department.name, COUNT(employee.id) AS liczba_pracownikow 
FROM department RIGHT JOIN employee ON employee.fk_department = department.id 
GROUP BY department.id ORDER BY liczba_pracownikow DESC;

-- Lista skilltype wg. popularności
-- <0.1s
SELECT name, COUNT(competence.id) AS liczba_pracownikow 
FROM skill_type JOIN competence ON skill_type.id = competence.fk_skill_type 
GROUP BY name ORDER BY liczba_pracownikow DESC;

-- Lista pracowników o poziomie danej umiejętności wyższym/równym od podanego
-- <0.1s
CREATE OR REPLACE FUNCTION workers_with_skill(skill text, level int)  
RETURNS TABLE(id int, name text, surname text, skill_name text, skill_level int) 
AS $$
       SELECT employee.id, employee.name, employee.surname, skill_type.name, competence.level FROM  
       employee JOIN (competence JOIN skill_type ON fk_skill_type = skill_type.id) ON fk_employee = employee.id
       WHERE skill_type.name = $1 AND competence.level >= $2;
$$
LANGUAGE SQL
IMMUTABLE
LEAKPROOF;
SELECT * FROM workers_with_skill('Python', 3);

-- Lista ile razy każda lokacja była odwiedzona w październiku
-- 0.128s -> 0.114s
SELECT location_table.id, location_table.name, COUNT(work_session.id) AS odwiedzenia  
FROM location_table RIGHT JOIN 
	(terminal JOIN work_session ON terminal.id = work_session.fk_start_terminal) ON location_table.id = terminal.fk_location
WHERE time_to < '2025-11-01' AND time_from > '2025-10-01' GROUP BY location_table.id ORDER BY odwiedzenia DESC;


