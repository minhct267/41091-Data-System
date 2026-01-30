/*
    Sample Data: dim_Staff
    20 rows - maintenance contractors/staff
*/

INSERT INTO mdw.dim_Staff (Staff_Key, Staff_ID, Name, Contact_Phone, Home_Address, Email_Address, Department)
VALUES
(1, 'STF001', 'James Wilson', '0412345678', '12 George St, Sydney NSW 2000', 'james.wilson@email.com', 'Electrical'),
(2, 'STF002', 'Sarah Johnson', '0423456789', '45 Collins St, Melbourne VIC 3000', 'sarah.johnson@email.com', 'Plumbing'),
(3, 'STF003', 'Michael Brown', '0434567890', '78 Queen St, Brisbane QLD 4000', 'michael.brown@email.com', 'HVAC'),
(4, 'STF004', 'Emma Davis', '0445678901', '23 Pitt St, Sydney NSW 2000', 'emma.davis@email.com', 'Electrical'),
(5, 'STF005', 'William Taylor', '0456789012', '56 Bourke St, Melbourne VIC 3000', 'william.taylor@email.com', 'Carpentry'),
(6, 'STF006', 'Olivia Martin', '0467890123', '89 Adelaide St, Brisbane QLD 4000', 'olivia.martin@email.com', 'Painting'),
(7, 'STF007', 'Thomas Anderson', '0478901234', '34 York St, Sydney NSW 2000', 'thomas.anderson@email.com', 'Roofing'),
(8, 'STF008', 'Sophie White', '0489012345', '67 Flinders St, Melbourne VIC 3000', 'sophie.white@email.com', 'Landscaping'),
(9, 'STF009', 'Daniel Harris', '0490123456', '12 Edward St, Brisbane QLD 4000', 'daniel.harris@email.com', 'Cleaning'),
(10, 'STF010', 'Isabella Clark', '0401234567', '45 Kent St, Sydney NSW 2000', 'isabella.clark@email.com', 'Plumbing'),
(11, 'STF011', 'Alexander Lee', '0412345670', '78 Spencer St, Melbourne VIC 3000', 'alexander.lee@email.com', 'HVAC'),
(12, 'STF012', 'Mia Robinson', '0423456781', '23 Albert St, Brisbane QLD 4000', 'mia.robinson@email.com', 'Electrical'),
(13, 'STF013', 'Benjamin Hall', '0434567892', '56 Market St, Sydney NSW 2000', 'benjamin.hall@email.com', 'Carpentry'),
(14, 'STF014', 'Charlotte Young', '0445678903', '89 Lonsdale St, Melbourne VIC 3000', 'charlotte.young@email.com', 'General'),
(15, 'STF015', 'Henry King', '0456789014', '34 Ann St, Brisbane QLD 4000', 'henry.king@email.com', 'Roofing'),
(16, 'STF016', 'Amelia Wright', '0467890125', '67 Clarence St, Sydney NSW 2000', 'amelia.wright@email.com', 'Painting'),
(17, 'STF017', 'Jack Scott', '0478901236', '12 Exhibition St, Melbourne VIC 3000', 'jack.scott@email.com', 'Plumbing'),
(18, 'STF018', 'Grace Green', '0489012347', '45 Creek St, Brisbane QLD 4000', 'grace.green@email.com', 'Landscaping'),
(19, 'STF019', 'Samuel Adams', '0490123458', '78 Bridge St, Sydney NSW 2000', 'samuel.adams@email.com', 'HVAC'),
(20, 'STF020', 'Chloe Baker', '0401234569', '23 Russell St, Melbourne VIC 3000', 'chloe.baker@email.com', 'Cleaning');
GO
