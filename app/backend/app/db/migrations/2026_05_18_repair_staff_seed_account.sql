-- Repair local databases where the staff login account or staff profile is missing.

INSERT INTO roles (role_name)
SELECT 'staff'
WHERE NOT EXISTS (
    SELECT 1
    FROM roles
    WHERE roles.role_name = 'staff'
);

SET @staff_role_id = (
    SELECT roles.role_id
    FROM roles
    WHERE roles.role_name = 'staff'
    LIMIT 1
);

SET @staff_user_id = (
    SELECT users.user_id
    FROM users
    WHERE users.email = 'staff@college.edu'
    LIMIT 1
);

INSERT INTO users (role_id, name, email, password_hash, is_active)
SELECT
    @staff_role_id,
    'Infirmary Staff',
    'staff@college.edu',
    '$2b$12$udxQAJyAC4wZKM6UjEkor.Gne2d86EwvkPMrRx8BjKFtIVUzgsAsm',
    TRUE
WHERE @staff_user_id IS NULL;

UPDATE users
SET
    users.role_id = @staff_role_id,
    users.name = 'Infirmary Staff',
    users.is_active = TRUE
WHERE users.email = 'staff@college.edu';

SET @staff_user_id = (
    SELECT users.user_id
    FROM users
    WHERE users.email = 'staff@college.edu'
    LIMIT 1
);

UPDATE staff
SET
    staff.user_id = @staff_user_id,
    staff.employee_number = 'STAFF-001',
    staff.specialization = NULL,
    staff.is_doctor = FALSE
WHERE staff.employee_number = 'STAFF-001';

INSERT INTO staff (user_id, employee_number, specialization, is_doctor)
SELECT
    @staff_user_id,
    'STAFF-001',
    NULL,
    FALSE
WHERE @staff_user_id IS NOT NULL
    AND NOT EXISTS (
        SELECT 1
        FROM staff
        WHERE staff.user_id = @staff_user_id
    )
    AND NOT EXISTS (
        SELECT 1
        FROM staff
        WHERE staff.employee_number = 'STAFF-001'
    );

UPDATE staff
SET
    staff.employee_number = 'STAFF-001',
    staff.specialization = NULL,
    staff.is_doctor = FALSE
WHERE staff.user_id = @staff_user_id;
