INSERT INTO roles (role_name)
SELECT 'professor'
WHERE NOT EXISTS (
    SELECT 1
    FROM roles
    WHERE roles.role_name = 'professor'
);
