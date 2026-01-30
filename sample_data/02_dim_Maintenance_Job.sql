/*
    Sample Data: dim_Maintenance_Job
    20 rows - various maintenance job types
*/

INSERT INTO mdw.dim_Maintenance_Job (Maintenance_Job_Key, Maintenance_Job_ID, Maintenance_Job_TypeCode, Maintenance_Job_Desc, IsHoliday, HourRate)
VALUES
(1, 'MJ001', 'ELEC', 'Electrical Repair', 0, 85.00),
(2, 'MJ002', 'ELEC', 'Electrical Installation', 0, 95.00),
(3, 'MJ003', 'PLUM', 'Plumbing Repair', 0, 80.00),
(4, 'MJ004', 'PLUM', 'Plumbing Installation', 0, 90.00),
(5, 'MJ005', 'HVAC', 'Air Conditioning Service', 0, 100.00),
(6, 'MJ006', 'HVAC', 'Heating System Repair', 0, 95.00),
(7, 'MJ007', 'CARP', 'Carpentry Work', 0, 75.00),
(8, 'MJ008', 'CARP', 'Door and Window Repair', 0, 70.00),
(9, 'MJ009', 'PAINT', 'Interior Painting', 0, 65.00),
(10, 'MJ010', 'PAINT', 'Exterior Painting', 0, 70.00),
(11, 'MJ011', 'ROOF', 'Roof Repair', 0, 110.00),
(12, 'MJ012', 'ROOF', 'Gutter Cleaning', 0, 60.00),
(13, 'MJ013', 'LAND', 'Landscaping', 0, 55.00),
(14, 'MJ014', 'LAND', 'Tree Trimming', 0, 65.00),
(15, 'MJ015', 'CLEAN', 'General Cleaning', 0, 45.00),
(16, 'MJ016', 'CLEAN', 'Deep Cleaning', 0, 55.00),
(17, 'MJ017', 'ELEC', 'Emergency Electrical', 1, 170.00),
(18, 'MJ018', 'PLUM', 'Emergency Plumbing', 1, 160.00),
(19, 'MJ019', 'HVAC', 'Emergency HVAC', 1, 200.00),
(20, 'MJ020', 'GEN', 'General Maintenance', 0, 60.00);
GO
