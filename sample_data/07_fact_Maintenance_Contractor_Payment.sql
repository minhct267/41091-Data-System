/*
    Sample Data: fact_Maintenance_Contractor_Payment
    20 rows - payment transactions
    
    Note: All foreign keys reference valid dimension records
    - Date_Key: 20240101-20240126 (from dim_Date)
    - Maintenance_Job_Key: 1-20 (from dim_Maintenance_Job)
    - Staff_Key: 1-20 (from dim_Staff)
    - Department_Key: 1-6 (from dim_Department)
    - Travel_Allowance_Policy_Key: 1-6 (from dim_Travel_Allowance_Policy)
    - Weather_Allowance_Policy_Key: 1-6 (from dim_Weather_Allowance_Policy)
*/

INSERT INTO mdw.fact_Maintenance_Contractor_Payment (
    Payment_ID, Date_Key, Maintenance_Job_Key, Staff_Key, Department_Key,
    Travel_Allowance_Policy_Key, Weather_Allowance_Policy_Key,
    Maintenance_Hours, HolidayPayment, Length_of_Travel,
    Travel_Allowance_Amount, Weather_Condition, Weather_Allowance_Amount, Total_Amount_Paid
)
VALUES
(1, 20240101, 1, 1, 1, 1, 1, 8.00, 680.00, 25.50, 19.89, 'Normal', 0.00, 699.89),
(2, 20240102, 3, 2, 2, 2, 1, 6.50, 0.00, 32.00, 27.20, 'Normal', 0.00, 547.20),
(3, 20240103, 5, 3, 3, 3, 2, 7.00, 0.00, 45.00, 41.40, 'Hot', 25.00, 766.40),
(4, 20240104, 7, 5, 4, 1, 1, 5.50, 0.00, 18.00, 14.04, 'Normal', 0.00, 426.54),
(5, 20240105, 9, 6, 4, 2, 1, 8.00, 0.00, 22.50, 19.13, 'Normal', 0.00, 539.13),
(6, 20240108, 11, 7, 4, 4, 5, 6.00, 0.00, 55.00, 57.75, 'Rainy', 20.00, 737.75),
(7, 20240109, 13, 8, 5, 1, 1, 7.50, 0.00, 28.00, 21.84, 'Normal', 0.00, 434.34),
(8, 20240110, 15, 9, 6, 2, 1, 4.00, 0.00, 15.00, 12.75, 'Normal', 0.00, 192.75),
(9, 20240111, 2, 4, 1, 3, 3, 8.00, 0.00, 38.00, 34.96, 'Extreme Heat', 50.00, 844.96),
(10, 20240112, 4, 10, 2, 1, 1, 6.00, 0.00, 20.00, 15.60, 'Normal', 0.00, 555.60),
(11, 20240115, 6, 11, 3, 4, 2, 7.00, 0.00, 60.00, 63.00, 'Hot', 25.00, 753.00),
(12, 20240116, 8, 13, 4, 2, 5, 5.00, 0.00, 25.00, 21.25, 'Rainy', 20.00, 391.25),
(13, 20240117, 10, 16, 4, 1, 1, 6.50, 0.00, 30.00, 23.40, 'Normal', 0.00, 478.40),
(14, 20240118, 12, 15, 4, 3, 6, 4.50, 0.00, 42.00, 38.64, 'Stormy', 40.00, 348.64),
(15, 20240119, 14, 18, 5, 5, 1, 5.00, 0.00, 35.00, 15.75, 'Normal', 0.00, 340.75),
(16, 20240122, 16, 20, 6, 2, 1, 6.00, 0.00, 28.00, 23.80, 'Normal', 0.00, 353.80),
(17, 20240123, 17, 12, 1, 6, 3, 4.00, 0.00, 50.00, 32.50, 'Extreme Heat', 50.00, 762.50),
(18, 20240124, 18, 17, 2, 1, 5, 5.00, 0.00, 22.00, 17.16, 'Rainy', 20.00, 837.16),
(19, 20240125, 19, 19, 3, 4, 2, 3.00, 0.00, 65.00, 68.25, 'Hot', 25.00, 693.25),
(20, 20240126, 20, 14, 6, 2, 1, 8.00, 480.00, 18.00, 15.30, 'Normal', 0.00, 975.30);
GO
