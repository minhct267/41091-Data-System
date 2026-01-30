/*
    Sample Data: dim_Travel_Allowance_Policy
    6 rows - travel allowance by vehicle type
*/

INSERT INTO mdw.dim_Travel_Allowance_Policy (Travel_Allowance_Policy_Key, Travel_Allowance_Policy_ID, Vehicle_Type, Allowance_Per_Km)
VALUES
(1, 'TAP001', 'Sedan', 0.78),
(2, 'TAP002', 'SUV', 0.85),
(3, 'TAP003', 'Van', 0.92),
(4, 'TAP004', 'Truck', 1.05),
(5, 'TAP005', 'Motorcycle', 0.45),
(6, 'TAP006', 'Electric Vehicle', 0.65);
GO
