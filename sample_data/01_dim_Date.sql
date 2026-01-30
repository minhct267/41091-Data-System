/*
    Sample Data: dim_Date
    20 rows - dates from January 2024
*/

INSERT INTO mdw.dim_Date (Date_Key, Date_Text, Day_Name, Month_Name, Month_Number, Year, IsHoliday_NSW, IsHoliday_VIC, IsHoliday_QLD)
VALUES
(20240101, '2024-01-01', 'Monday', 'January', 1, 2024, 1, 1, 1),
(20240102, '2024-01-02', 'Tuesday', 'January', 1, 2024, 0, 0, 0),
(20240103, '2024-01-03', 'Wednesday', 'January', 1, 2024, 0, 0, 0),
(20240104, '2024-01-04', 'Thursday', 'January', 1, 2024, 0, 0, 0),
(20240105, '2024-01-05', 'Friday', 'January', 1, 2024, 0, 0, 0),
(20240108, '2024-01-08', 'Monday', 'January', 1, 2024, 0, 0, 0),
(20240109, '2024-01-09', 'Tuesday', 'January', 1, 2024, 0, 0, 0),
(20240110, '2024-01-10', 'Wednesday', 'January', 1, 2024, 0, 0, 0),
(20240111, '2024-01-11', 'Thursday', 'January', 1, 2024, 0, 0, 0),
(20240112, '2024-01-12', 'Friday', 'January', 1, 2024, 0, 0, 0),
(20240115, '2024-01-15', 'Monday', 'January', 1, 2024, 0, 0, 0),
(20240116, '2024-01-16', 'Tuesday', 'January', 1, 2024, 0, 0, 0),
(20240117, '2024-01-17', 'Wednesday', 'January', 1, 2024, 0, 0, 0),
(20240118, '2024-01-18', 'Thursday', 'January', 1, 2024, 0, 0, 0),
(20240119, '2024-01-19', 'Friday', 'January', 1, 2024, 0, 0, 0),
(20240122, '2024-01-22', 'Monday', 'January', 1, 2024, 0, 0, 0),
(20240123, '2024-01-23', 'Tuesday', 'January', 1, 2024, 0, 0, 0),
(20240124, '2024-01-24', 'Wednesday', 'January', 1, 2024, 0, 0, 0),
(20240125, '2024-01-25', 'Thursday', 'January', 1, 2024, 0, 0, 0),
(20240126, '2024-01-26', 'Friday', 'January', 1, 2024, 1, 1, 1);
GO
