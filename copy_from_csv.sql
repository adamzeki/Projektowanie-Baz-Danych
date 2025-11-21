BEGIN;
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT conrelid::regclass AS table_name,
               conname AS constraint_name
        FROM pg_constraint
        WHERE contype = 'f'  -- foreign keys only
    LOOP
        EXECUTE format(
            'ALTER TABLE %I ALTER CONSTRAINT %I DEFERRABLE INITIALLY DEFERRED;',
            r.table_name, r.constraint_name
        );
        RAISE NOTICE 'Changed % to DEFERRABLE INITIALLY DEFERRED', r.constraint_name;
    END LOOP;
END;
$$;

SET CONSTRAINTS ALL DEFERRED;

\copy absence FROM 'C:\Users\adamz\Desktop\Edukacja\Sem_5\Projektowanie_baz_danych\tables\absence.csv' WITH (FORMAT csv);
\copy absence_type FROM 'C:\Users\adamz\Desktop\Edukacja\Sem_5\Projektowanie_baz_danych\tables\absence_type.csv' WITH (FORMAT csv); 
\copy competence FROM 'C:\Users\adamz\Desktop\Edukacja\Sem_5\Projektowanie_baz_danych\tables\competence.csv' WITH (FORMAT csv);
\copy skill_type FROM 'C:\Users\adamz\Desktop\Edukacja\Sem_5\Projektowanie_baz_danych\tables\skill_type.csv' WITH (FORMAT csv);
\copy work_schedule FROM 'C:\Users\adamz\Desktop\Edukacja\Sem_5\Projektowanie_baz_danych\tables\work_schedule.csv' WITH (FORMAT csv);
\copy project_assignment FROM 'C:\Users\adamz\Desktop\Edukacja\Sem_5\Projektowanie_baz_danych\tables\project_assignment.csv' WITH (FORMAT csv);
\copy project FROM 'C:\Users\adamz\Desktop\Edukacja\Sem_5\Projektowanie_baz_danych\tables\project.csv' WITH (FORMAT csv);
\copy employee FROM 'C:\Users\adamz\Desktop\Edukacja\Sem_5\Projektowanie_baz_danych\tables\employee.csv' WITH (FORMAT csv);
\copy department FROM 'C:\Users\adamz\Desktop\Edukacja\Sem_5\Projektowanie_baz_danych\tables\department.csv' WITH (FORMAT csv);
\copy work_session FROM 'C:\Users\adamz\Desktop\Edukacja\Sem_5\Projektowanie_baz_danych\tables\work_session.csv' WITH (FORMAT csv);
\copy location_table FROM 'C:\Users\adamz\Desktop\Edukacja\Sem_5\Projektowanie_baz_danych\tables\location_table.csv' WITH (FORMAT csv);
\copy terminal FROM 'C:\Users\adamz\Desktop\Edukacja\Sem_5\Projektowanie_baz_danych\tables\terminal.csv' WITH (FORMAT csv);
\copy project_role FROM 'C:\Users\adamz\Desktop\Edukacja\Sem_5\Projektowanie_baz_danych\tables\project_role.csv' WITH (FORMAT csv);
\copy monthly_score FROM 'C:\Users\adamz\Desktop\Edukacja\Sem_5\Projektowanie_baz_danych\tables\monthly_score.csv' WITH (FORMAT csv);
COMMIT;
