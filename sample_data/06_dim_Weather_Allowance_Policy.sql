/*
    Sample Data: dim_Weather_Allowance_Policy
    6 rows - weather-based allowance policies
*/

INSERT INTO mdw.dim_Weather_Allowance_Policy (Weather_Allowance_Policy_Key, Policy_Key, Weather, Temperature, Weather_Allowance)
VALUES
(1, 'WAP001', 'Normal', 25.00, 0.00),
(2, 'WAP002', 'Hot', 35.00, 25.00),
(3, 'WAP003', 'Extreme Heat', 40.00, 50.00),
(4, 'WAP004', 'Cold', 10.00, 15.00),
(5, 'WAP005', 'Rainy', 20.00, 20.00),
(6, 'WAP006', 'Stormy', 18.00, 40.00);
GO
