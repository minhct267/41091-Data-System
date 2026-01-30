/*
    Sample Data: dim_Department
    6 rows - organizational departments
*/

INSERT INTO mdw.dim_Department (Department_Key, Department_Name, Department_Location, Front_Desk_Phone)
VALUES
(1, 'Electrical Services', 'Building A, Level 2, Sydney', '02 9111 1111'),
(2, 'Plumbing Services', 'Building A, Level 3, Sydney', '02 9222 2222'),
(3, 'HVAC Services', 'Building B, Level 1, Melbourne', '03 9333 3333'),
(4, 'Building Maintenance', 'Building B, Level 2, Melbourne', '03 9444 4444'),
(5, 'Grounds & Landscaping', 'Building C, Level 1, Brisbane', '07 9555 5555'),
(6, 'General Services', 'Building C, Level 2, Brisbane', '07 9666 6666');
GO
