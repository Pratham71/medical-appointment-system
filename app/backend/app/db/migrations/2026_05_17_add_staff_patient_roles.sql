INSERT INTO roles (role_name)
SELECT 'college-staff'
WHERE NOT EXISTS (
    SELECT 1
    FROM roles
    WHERE roles.role_name = 'college-staff'
);

INSERT INTO roles (role_name)
SELECT 'hostel-staff'
WHERE NOT EXISTS (
    SELECT 1
    FROM roles
    WHERE roles.role_name = 'hostel-staff'
);

INSERT INTO users (role_id, name, email, password_hash, is_active)
SELECT
    roles.role_id,
    'College Staff Patient',
    'college.staff@college.edu',
    '$2b$12$udxQAJyAC4wZKM6UjEkor.Gne2d86EwvkPMrRx8BjKFtIVUzgsAsm',
    TRUE
FROM roles
WHERE roles.role_name = 'college-staff'
    AND NOT EXISTS (
        SELECT 1
        FROM users
        WHERE users.email = 'college.staff@college.edu'
    );

INSERT INTO users (role_id, name, email, password_hash, is_active)
SELECT
    roles.role_id,
    'Hostel Staff Patient',
    'hostel.staff@college.edu',
    '$2b$12$udxQAJyAC4wZKM6UjEkor.Gne2d86EwvkPMrRx8BjKFtIVUzgsAsm',
    TRUE
FROM roles
WHERE roles.role_name = 'hostel-staff'
    AND NOT EXISTS (
        SELECT 1
        FROM users
        WHERE users.email = 'hostel.staff@college.edu'
    );

INSERT INTO students (user_id, roll_number, department, year_level)
SELECT
    users.user_id,
    'CSTAFF-001',
    'College Administration',
    1
FROM users
WHERE users.email = 'college.staff@college.edu'
    AND NOT EXISTS (
        SELECT 1
        FROM students
        WHERE students.roll_number = 'CSTAFF-001'
    );

INSERT INTO students (user_id, roll_number, department, year_level)
SELECT
    users.user_id,
    'HSTAFF-001',
    'Hostel Administration',
    1
FROM users
WHERE users.email = 'hostel.staff@college.edu'
    AND NOT EXISTS (
        SELECT 1
        FROM students
        WHERE students.roll_number = 'HSTAFF-001'
    );
