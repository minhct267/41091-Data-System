/*
    Master Script: Load All Sample Data
    Run this file to load all sample data in correct order
    
    Prerequisites: Run db_maintenance_payment.sql first to create schema and tables
*/

PRINT 'Loading sample data...';
PRINT '';

-- Dimension tables first (no dependencies)
PRINT '1. Loading dim_Date...';
:r 01_dim_Date.sql

PRINT '2. Loading dim_Maintenance_Job...';
:r 02_dim_Maintenance_Job.sql

PRINT '3. Loading dim_Staff...';
:r 03_dim_Staff.sql

PRINT '4. Loading dim_Department...';
:r 04_dim_Department.sql

PRINT '5. Loading dim_Travel_Allowance_Policy...';
:r 05_dim_Travel_Allowance_Policy.sql

PRINT '6. Loading dim_Weather_Allowance_Policy...';
:r 06_dim_Weather_Allowance_Policy.sql

-- Fact table last (depends on all dimensions)
PRINT '7. Loading fact_Maintenance_Contractor_Payment...';
:r 07_fact_Maintenance_Contractor_Payment.sql

PRINT '';
PRINT 'All sample data loaded successfully!';

-- Verify row counts
SELECT 'dim_Date' AS TableName, COUNT(*) AS RowCount FROM mdw.dim_Date
UNION ALL
SELECT 'dim_Maintenance_Job', COUNT(*) FROM mdw.dim_Maintenance_Job
UNION ALL
SELECT 'dim_Staff', COUNT(*) FROM mdw.dim_Staff
UNION ALL
SELECT 'dim_Department', COUNT(*) FROM mdw.dim_Department
UNION ALL
SELECT 'dim_Travel_Allowance_Policy', COUNT(*) FROM mdw.dim_Travel_Allowance_Policy
UNION ALL
SELECT 'dim_Weather_Allowance_Policy', COUNT(*) FROM mdw.dim_Weather_Allowance_Policy
UNION ALL
SELECT 'fact_Maintenance_Contractor_Payment', COUNT(*) FROM mdw.fact_Maintenance_Contractor_Payment;
GO
