-- CREATE USER user_name WITH PASSWORD = 'password';

-- Remove broad role if previously granted
ALTER ROLE db_datareader DROP MEMBER mimi;

-- Grant only SELECT and INSERT on schema mdw (no UPDATE, no DELETE)
GRANT SELECT ON SCHEMA::mdw TO mimi;
GRANT INSERT ON SCHEMA::mdw TO mimi;
