-- Store emergency alerts triggered by students from the app.

CREATE TABLE IF NOT EXISTS emergency_alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    message VARCHAR(500) NOT NULL DEFAULT 'Student requested emergency assistance',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_emergency_alerts_student
        FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

SET @has_emergency_alerts_index = (
    SELECT COUNT(*)
    FROM information_schema.statistics
    WHERE table_schema = DATABASE()
        AND table_name = 'emergency_alerts'
        AND index_name = 'idx_emergency_alerts_student_created'
);

SET @create_emergency_alerts_index_sql = IF(
    @has_emergency_alerts_index = 0,
    'CREATE INDEX idx_emergency_alerts_student_created
        ON emergency_alerts(student_id, created_at)',
    'SELECT 1'
);

PREPARE create_emergency_alerts_index_stmt
    FROM @create_emergency_alerts_index_sql;
EXECUTE create_emergency_alerts_index_stmt;
DEALLOCATE PREPARE create_emergency_alerts_index_stmt;
