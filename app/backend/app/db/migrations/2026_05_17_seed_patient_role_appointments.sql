-- Adds appointment slots, appointments, and emergency alerts for
-- professor, college-staff, and hostel-staff seed accounts.
-- Uses email-based lookups so it works on both fresh and migrated databases.

-- Slots: upcoming (booked), past (completed), today-cancelled (available/freed)
INSERT IGNORE INTO appointment_slots (slot_id, staff_id, slot_status_id, slot_date, start_time, end_time) VALUES
    -- professor
    (5,  1, 2, DATE_ADD(CURRENT_DATE, INTERVAL 3 DAY),  '09:00:00', '09:30:00'),
    (6,  1, 2, DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY),  '10:00:00', '10:30:00'),
    (7,  1, 1, CURRENT_DATE,                             '11:00:00', '11:30:00'),
    -- college-staff
    (8,  1, 2, DATE_ADD(CURRENT_DATE, INTERVAL 4 DAY),  '09:30:00', '10:00:00'),
    (9,  1, 2, DATE_SUB(CURRENT_DATE, INTERVAL 5 DAY),  '09:00:00', '09:30:00'),
    (10, 1, 1, CURRENT_DATE,                             '10:30:00', '11:00:00'),
    -- hostel-staff
    (11, 1, 2, DATE_ADD(CURRENT_DATE, INTERVAL 2 DAY),  '10:00:00', '10:30:00'),
    (12, 1, 2, DATE_SUB(CURRENT_DATE, INTERVAL 3 DAY),  '09:30:00', '10:00:00'),
    (13, 1, 1, CURRENT_DATE,                             '11:30:00', '12:00:00');

-- Professor appointments
INSERT IGNORE INTO appointments (student_id, slot_id, status_id, reason, cancellation_reason)
SELECT s.student_id, 5, 1, 'Annual checkup', NULL
FROM students s JOIN users u ON u.user_id = s.user_id WHERE u.email = 'professor@college.edu';

INSERT IGNORE INTO appointments (student_id, slot_id, status_id, reason, cancellation_reason)
SELECT s.student_id, 6, 3, 'Seasonal flu symptoms', NULL
FROM students s JOIN users u ON u.user_id = s.user_id WHERE u.email = 'professor@college.edu';

INSERT IGNORE INTO appointments (student_id, slot_id, status_id, reason, cancellation_reason)
SELECT s.student_id, 7, 2, 'Routine consultation', 'Doctor unavailable: on emergency duty'
FROM students s JOIN users u ON u.user_id = s.user_id WHERE u.email = 'professor@college.edu';

-- College-staff appointments
INSERT IGNORE INTO appointments (student_id, slot_id, status_id, reason, cancellation_reason)
SELECT s.student_id, 8, 1, 'General wellness check', NULL
FROM students s JOIN users u ON u.user_id = s.user_id WHERE u.email = 'college.staff@college.edu';

INSERT IGNORE INTO appointments (student_id, slot_id, status_id, reason, cancellation_reason)
SELECT s.student_id, 9, 3, 'Back pain consultation', NULL
FROM students s JOIN users u ON u.user_id = s.user_id WHERE u.email = 'college.staff@college.edu';

INSERT IGNORE INTO appointments (student_id, slot_id, status_id, reason, cancellation_reason)
SELECT s.student_id, 10, 2, 'Follow-up', 'Student request: rescheduled'
FROM students s JOIN users u ON u.user_id = s.user_id WHERE u.email = 'college.staff@college.edu';

-- Hostel-staff appointments
INSERT IGNORE INTO appointments (student_id, slot_id, status_id, reason, cancellation_reason)
SELECT s.student_id, 11, 1, 'Routine checkup', NULL
FROM students s JOIN users u ON u.user_id = s.user_id WHERE u.email = 'hostel.staff@college.edu';

INSERT IGNORE INTO appointments (student_id, slot_id, status_id, reason, cancellation_reason)
SELECT s.student_id, 12, 3, 'Headache and fatigue', NULL
FROM students s JOIN users u ON u.user_id = s.user_id WHERE u.email = 'hostel.staff@college.edu';

INSERT IGNORE INTO appointments (student_id, slot_id, status_id, reason, cancellation_reason)
SELECT s.student_id, 13, 2, 'Consultation', 'No-show'
FROM students s JOIN users u ON u.user_id = s.user_id WHERE u.email = 'hostel.staff@college.edu';

-- Emergency alerts so the Dashboard "Emergency Alert Status" section is visible
INSERT IGNORE INTO emergency_alerts (student_id, reason, location, contact_number, message)
SELECT s.student_id, 'Injury', 'Lab Block B, Room 101', NULL, 'Twisted ankle during lab session'
FROM students s JOIN users u ON u.user_id = s.user_id WHERE u.email = 'professor@college.edu';

INSERT IGNORE INTO emergency_alerts (student_id, reason, location, contact_number, message)
SELECT s.student_id, 'Chest pain', 'Hostel Block C', NULL, 'Mild chest discomfort after lunch'
FROM students s JOIN users u ON u.user_id = s.user_id WHERE u.email = 'college.staff@college.edu';

INSERT IGNORE INTO emergency_alerts (student_id, reason, location, contact_number, message)
SELECT s.student_id, 'Allergic reaction', 'Cafeteria', NULL, 'Rash after eating'
FROM students s JOIN users u ON u.user_id = s.user_id WHERE u.email = 'hostel.staff@college.edu';
