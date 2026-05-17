INSERT INTO roles (role_id, role_name) VALUES
    (1, 'student'),
    (2, 'doctor'),
    (3, 'admin'),
    (4, 'staff'),
    (5, 'professor'),
    (6, 'college-staff'),
    (7, 'hostel-staff');

INSERT INTO appointment_statuses (status_id, status_name) VALUES
    (1, 'booked'),
    (2, 'cancelled'),
    (3, 'completed');

INSERT INTO slot_statuses (slot_status_id, status_name) VALUES
    (1, 'available'),
    (2, 'booked'),
    (3, 'unavailable');

INSERT INTO certificate_types (certificate_type_id, certificate_type) VALUES
    (1, 'Medical Leave'),
    (2, 'Fitness Certificate'),
    (3, 'Consultation Proof');

INSERT INTO users (user_id, role_id, name, email, password_hash, is_active) VALUES
    (
        1,
        1,
        'Aarav Sharma',
        'student@college.edu',
        '$2b$12$udxQAJyAC4wZKM6UjEkor.Gne2d86EwvkPMrRx8BjKFtIVUzgsAsm',
        TRUE
    ),
    (
        2,
        2,
        'Dr. Meera Singh',
        'doctor@college.edu',
        '$2b$12$udxQAJyAC4wZKM6UjEkor.Gne2d86EwvkPMrRx8BjKFtIVUzgsAsm',
        TRUE
    ),
    (
        3,
        3,
        'Clinic Admin',
        'admin@college.edu',
        '$2b$12$udxQAJyAC4wZKM6UjEkor.Gne2d86EwvkPMrRx8BjKFtIVUzgsAsm',
        TRUE
    ),
    (
        4,
        4,
        'Infirmary Staff',
        'staff@college.edu',
        '$2b$12$udxQAJyAC4wZKM6UjEkor.Gne2d86EwvkPMrRx8BjKFtIVUzgsAsm',
        TRUE
    ),
    (
        5,
        5,
        'Prof. Arjun Rao',
        'professor@college.edu',
        '$2b$12$udxQAJyAC4wZKM6UjEkor.Gne2d86EwvkPMrRx8BjKFtIVUzgsAsm',
        TRUE
    ),
    (
        6,
        6,
        'College Staff Patient',
        'college.staff@college.edu',
        '$2b$12$udxQAJyAC4wZKM6UjEkor.Gne2d86EwvkPMrRx8BjKFtIVUzgsAsm',
        TRUE
    ),
    (
        7,
        7,
        'Hostel Staff Patient',
        'hostel.staff@college.edu',
        '$2b$12$udxQAJyAC4wZKM6UjEkor.Gne2d86EwvkPMrRx8BjKFtIVUzgsAsm',
        TRUE
    );

INSERT INTO students (student_id, user_id, roll_number, department, year_level) VALUES
    (1, 1, 'CSE-2026-001', 'Computer Science', 2),
    (2, 5, 'PROF-001', 'Computer Science', 1),
    (3, 6, 'CSTAFF-001', 'College Administration', 1),
    (4, 7, 'HSTAFF-001', 'Hostel Administration', 1);

INSERT INTO staff (staff_id, user_id, employee_number, specialization, is_doctor) VALUES
    (1, 2, 'DOC-001', 'General Medicine', TRUE),
    (2, 4, 'STAFF-001', NULL, FALSE);

INSERT INTO doctor_weekly_availability (
    staff_id,
    weekday,
    is_available,
    start_time,
    end_time
) VALUES
    (1, 0, TRUE, '09:00:00', '17:00:00'),
    (1, 1, TRUE, '09:00:00', '17:00:00'),
    (1, 2, TRUE, '09:00:00', '17:00:00'),
    (1, 3, TRUE, '09:00:00', '17:00:00'),
    (1, 4, TRUE, '09:00:00', '17:00:00'),
    (1, 5, TRUE, '09:00:00', '17:00:00'),
    (1, 6, FALSE, NULL, NULL);

INSERT INTO appointment_slots (
    slot_id,
    staff_id,
    slot_status_id,
    slot_date,
    start_time,
    end_time
) VALUES
    (1, 1, 1, DATE_ADD(CURRENT_DATE, INTERVAL 1 DAY), '09:00:00', '09:30:00'),
    (2, 1, 1, DATE_ADD(CURRENT_DATE, INTERVAL 1 DAY), '09:30:00', '10:00:00'),
    (3, 1, 2, DATE_ADD(CURRENT_DATE, INTERVAL 2 DAY), '10:00:00', '10:30:00'),
    (4, 1, 2, DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY), '11:00:00', '11:30:00');

INSERT INTO appointments (appointment_id, student_id, slot_id, status_id, reason) VALUES
    (1, 1, 3, 1, 'Fever and headache'),
    (2, 1, 4, 3, 'Follow-up consultation');

INSERT INTO medical_notes (note_id, appointment_id, diagnosis, remarks) VALUES
    (1, 2, 'Seasonal fever', 'Rest advised for two days');

INSERT INTO prescriptions (prescription_id, appointment_id) VALUES
    (1, 2);

INSERT INTO prescription_items (item_id, prescription_id, medicine_name, dosage) VALUES
    (1, 1, 'Paracetamol', '500mg twice daily after food');

INSERT INTO medical_certificates (
    certificate_id,
    appointment_id,
    certificate_type_id,
    issue_date
) VALUES
    (1, 2, 1, DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY));
