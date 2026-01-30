/*
    Maintenance Contractor Payment Data Warehouse
    Target: Azure SQL Database
*/

-- Create schema
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'mdw')
    EXEC('CREATE SCHEMA mdw');
GO

-- Drop existing tables
IF OBJECT_ID('mdw.fact_Maintenance_Contractor_Payment', 'U') IS NOT NULL
    DROP TABLE mdw.fact_Maintenance_Contractor_Payment;
IF OBJECT_ID('mdw.dim_Date', 'U') IS NOT NULL
    DROP TABLE mdw.dim_Date;
IF OBJECT_ID('mdw.dim_Maintenance_Job', 'U') IS NOT NULL
    DROP TABLE mdw.dim_Maintenance_Job;
IF OBJECT_ID('mdw.dim_Staff', 'U') IS NOT NULL
    DROP TABLE mdw.dim_Staff;
IF OBJECT_ID('mdw.dim_Department', 'U') IS NOT NULL
    DROP TABLE mdw.dim_Department;
IF OBJECT_ID('mdw.dim_Travel_Allowance_Policy', 'U') IS NOT NULL
    DROP TABLE mdw.dim_Travel_Allowance_Policy;
IF OBJECT_ID('mdw.dim_Weather_Allowance_Policy', 'U') IS NOT NULL
    DROP TABLE mdw.dim_Weather_Allowance_Policy;
GO

-- ============================================================================
-- DIMENSION TABLES
-- ============================================================================

CREATE TABLE mdw.dim_Date (
    Date_Key            INT             NOT NULL,
    Date_Text           VARCHAR(20)     NOT NULL,
    Day_Name            VARCHAR(15)     NOT NULL,
    Month_Name          VARCHAR(15)     NOT NULL,
    Month_Number        INT             NOT NULL,
    Year                INT             NOT NULL,
    IsHoliday_NSW       BIT             NOT NULL DEFAULT 0,
    IsHoliday_VIC       BIT             NOT NULL DEFAULT 0,
    IsHoliday_QLD       BIT             NOT NULL DEFAULT 0,
    CONSTRAINT PK_dim_Date PRIMARY KEY CLUSTERED (Date_Key)
);
GO

CREATE TABLE mdw.dim_Maintenance_Job (
    Maintenance_Job_Key         INT             NOT NULL,
    Maintenance_Job_ID          VARCHAR(50)     NOT NULL,
    Maintenance_Job_TypeCode    VARCHAR(20)     NOT NULL,
    Maintenance_Job_Desc        NVARCHAR(255)   NULL,
    IsHoliday                   BIT             NOT NULL DEFAULT 0,
    HourRate                    DECIMAL(10, 2)  NOT NULL,
    CONSTRAINT PK_dim_Maintenance_Job PRIMARY KEY CLUSTERED (Maintenance_Job_Key),
    CONSTRAINT UK_dim_Maintenance_Job_NK UNIQUE (Maintenance_Job_ID)
);
GO

CREATE TABLE mdw.dim_Staff (
    Staff_Key           INT             NOT NULL,
    Staff_ID            VARCHAR(50)     NOT NULL,
    Name                NVARCHAR(100)   NOT NULL,
    Contact_Phone       VARCHAR(20)     NULL,
    Home_Address        NVARCHAR(255)   NULL,
    Email_Address       VARCHAR(100)    NULL,
    Department          NVARCHAR(100)   NULL,
    CONSTRAINT PK_dim_Staff PRIMARY KEY CLUSTERED (Staff_Key),
    CONSTRAINT UK_dim_Staff_NK UNIQUE (Staff_ID)
);
GO

CREATE TABLE mdw.dim_Department (
    Department_Key          INT             NOT NULL,
    Department_Name         NVARCHAR(100)   NOT NULL,
    Department_Location     NVARCHAR(255)   NULL,
    Front_Desk_Phone        VARCHAR(20)     NULL,
    CONSTRAINT PK_dim_Department PRIMARY KEY CLUSTERED (Department_Key)
);
GO

CREATE TABLE mdw.dim_Travel_Allowance_Policy (
    Travel_Allowance_Policy_Key     INT             NOT NULL,
    Travel_Allowance_Policy_ID      VARCHAR(50)     NOT NULL,
    Vehicle_Type                    VARCHAR(50)     NOT NULL,
    Allowance_Per_Km                DECIMAL(10, 4)  NOT NULL,
    CONSTRAINT PK_dim_Travel_Allowance_Policy PRIMARY KEY CLUSTERED (Travel_Allowance_Policy_Key),
    CONSTRAINT UK_dim_Travel_Allowance_Policy_NK UNIQUE (Travel_Allowance_Policy_ID)
);
GO

CREATE TABLE mdw.dim_Weather_Allowance_Policy (
    Weather_Allowance_Policy_Key    INT             NOT NULL,
    Policy_Key                      VARCHAR(50)     NOT NULL,
    Weather                         VARCHAR(50)     NOT NULL,
    Temperature                     DECIMAL(5, 2)   NULL,
    Weather_Allowance               DECIMAL(10, 2)  NOT NULL,
    CONSTRAINT PK_dim_Weather_Allowance_Policy PRIMARY KEY CLUSTERED (Weather_Allowance_Policy_Key),
    CONSTRAINT UK_dim_Weather_Allowance_Policy_NK UNIQUE (Policy_Key)
);
GO

-- ============================================================================
-- FACT TABLE
-- ============================================================================

CREATE TABLE mdw.fact_Maintenance_Contractor_Payment (
    Payment_ID                      INT             NOT NULL,
    Date_Key                        INT             NOT NULL,
    Maintenance_Job_Key             INT             NOT NULL,
    Staff_Key                       INT             NOT NULL,
    Department_Key                  INT             NOT NULL,
    Travel_Allowance_Policy_Key     INT             NOT NULL,
    Weather_Allowance_Policy_Key    INT             NOT NULL,
    Maintenance_Hours               DECIMAL(10, 2)  NOT NULL,
    HolidayPayment                  DECIMAL(12, 2)  NOT NULL DEFAULT 0,
    Length_of_Travel                DECIMAL(10, 2)  NOT NULL DEFAULT 0,
    Travel_Allowance_Amount         DECIMAL(12, 2)  NOT NULL DEFAULT 0,
    Weather_Condition               VARCHAR(50)     NULL,
    Weather_Allowance_Amount        DECIMAL(12, 2)  NOT NULL DEFAULT 0,
    Total_Amount_Paid               DECIMAL(14, 2)  NOT NULL,
    CONSTRAINT PK_fact_Maintenance_Contractor_Payment PRIMARY KEY CLUSTERED (Payment_ID),
    CONSTRAINT FK_fact_Payment_Date FOREIGN KEY (Date_Key) REFERENCES mdw.dim_Date (Date_Key),
    CONSTRAINT FK_fact_Payment_MaintenanceJob FOREIGN KEY (Maintenance_Job_Key) REFERENCES mdw.dim_Maintenance_Job (Maintenance_Job_Key),
    CONSTRAINT FK_fact_Payment_Staff FOREIGN KEY (Staff_Key) REFERENCES mdw.dim_Staff (Staff_Key),
    CONSTRAINT FK_fact_Payment_Department FOREIGN KEY (Department_Key) REFERENCES mdw.dim_Department (Department_Key),
    CONSTRAINT FK_fact_Payment_TravelAllowancePolicy FOREIGN KEY (Travel_Allowance_Policy_Key) REFERENCES mdw.dim_Travel_Allowance_Policy (Travel_Allowance_Policy_Key),
    CONSTRAINT FK_fact_Payment_WeatherAllowancePolicy FOREIGN KEY (Weather_Allowance_Policy_Key) REFERENCES mdw.dim_Weather_Allowance_Policy (Weather_Allowance_Policy_Key)
);
GO

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE NONCLUSTERED INDEX IX_fact_Payment_Date_Key ON mdw.fact_Maintenance_Contractor_Payment (Date_Key);
CREATE NONCLUSTERED INDEX IX_fact_Payment_Maintenance_Job_Key ON mdw.fact_Maintenance_Contractor_Payment (Maintenance_Job_Key);
CREATE NONCLUSTERED INDEX IX_fact_Payment_Staff_Key ON mdw.fact_Maintenance_Contractor_Payment (Staff_Key);
CREATE NONCLUSTERED INDEX IX_fact_Payment_Department_Key ON mdw.fact_Maintenance_Contractor_Payment (Department_Key);
CREATE NONCLUSTERED INDEX IX_fact_Payment_Travel_Policy_Key ON mdw.fact_Maintenance_Contractor_Payment (Travel_Allowance_Policy_Key);
CREATE NONCLUSTERED INDEX IX_fact_Payment_Weather_Policy_Key ON mdw.fact_Maintenance_Contractor_Payment (Weather_Allowance_Policy_Key);
CREATE NONCLUSTERED INDEX IX_dim_Date_Year ON mdw.dim_Date (Year, Month_Number);
CREATE NONCLUSTERED INDEX IX_dim_Staff_Department ON mdw.dim_Staff (Department);
CREATE NONCLUSTERED INDEX IX_dim_Maintenance_Job_TypeCode ON mdw.dim_Maintenance_Job (Maintenance_Job_TypeCode);
GO

-- Verify tables created
SELECT 
    t.name AS TableName,
    CASE WHEN t.name LIKE 'fact_%' THEN 'Fact' ELSE 'Dimension' END AS TableType
FROM sys.tables t
INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
WHERE s.name = 'mdw'
ORDER BY TableType, TableName;
GO

PRINT 'Schema [mdw] created successfully with 6 dimension tables and 1 fact table.';
GO
