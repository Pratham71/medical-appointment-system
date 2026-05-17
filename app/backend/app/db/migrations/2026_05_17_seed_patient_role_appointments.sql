-- Adds sample appointment slots and appointments for professor, college-staff,
-- and hostel-staff seed accounts so their dashboards have visible data.
-- Safe to run on a database that already has the base seed applied.

INSERT IGNORE INTO appointment_slots (slot_id, staff_id, slot_status_id, slot_date, start_time, end_time) VALUES
    -- professor slots
    (5,  1, 2, DATE_ADD(CURRENT_DATE, INTERVAL 3 DAY),  '09:00:00', '09:30:00'),
    (6,  1, 2, DATE_SUB(CURRENT_DATE, INTERVAL 14 DAY), '10:00:00', '10:30:00'),
    (7,  1, 1, DATE_SUB(CURRENT_DATE, INTERVAL 5 DAY),  '11:00:00', '11:30:00'),
    -- college-staff slots
    (8,  1, 2, DATE_ADD(CURRENT_DATE, INTERVAL 4 DAY),  '09:30:00', '10:00:00'),
    (9,  1, 2, DATE_SUB(CURRENT_DATE, INTERVAL 10 DAY), '09:00:00', '09:30:00'),
    (10, 1, 1, DATE_SUB(CURRENT_DATE, INTERVAL 3 DAY),  '10:30:00', '11:00:00'),
    -- hostel-staff slots
    (11, 1, 2, DATE_ADD(CURRENT_DATE, INTERVAL 5 DAY),  '10:00:00', '10:30:00'),
    (12, 1, 2, DATE_SUB(CURRENT_DATE, INTERVAL 8 DAY),  '09:30:00', '10:00:00'),
    (13, 1, 1, DATE_SUB(CURRENT_DATE, INTERVAL 2 DAY),  '11:30:00', '12:00:00');

INSERT IGNORE INTO appointments (appointment_id, student_id, slot_id, status_id, reason, cancellation_reason) VALUES
    -- professor: upcoming (booked), past (completed), cancelled
    (3,  2, 5,  1, 'Annual checkup',          NULL),
    (4,  2, 6,  3, 'Seasonal flu symptoms',   NULL),
    (5,  2, 7,  2, 'Routine consultation',    'Doctor unavailable: on emergency duty'),
    -- college-staff: upcoming, past, cancelled
    (6,  3, 8,  1, 'General wellness check',  NULL),
    (7,  3, 9,  3, 'Back pain consultation',  NULL),
    (8,  3, 10, 2, 'Follow-up',               'Student request: rescheduled'),
    -- hostel-staff: upcoming, past, cancelled
    (9,  4, 11, 1, 'Routine checkup',         NULL),
    (10, 4, 12, 3, 'Headache and fatigue',    NULL),
    (11, 4, 13, 2, 'Consultation',            'No-show');
