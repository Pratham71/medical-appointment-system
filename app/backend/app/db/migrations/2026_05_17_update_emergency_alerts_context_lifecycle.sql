-- Add structured emergency alert context and response lifecycle fields.

SET @has_alert_reason = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
        AND table_name = 'emergency_alerts'
        AND column_name = 'reason'
);

SET @add_alert_reason_sql = IF(
    @has_alert_reason = 0,
    'ALTER TABLE emergency_alerts
        ADD COLUMN reason VARCHAR(120) NOT NULL DEFAULT ''Other''
        AFTER student_id',
    'SELECT 1'
);

PREPARE add_alert_reason_stmt FROM @add_alert_reason_sql;
EXECUTE add_alert_reason_stmt;
DEALLOCATE PREPARE add_alert_reason_stmt;

SET @has_alert_location = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
        AND table_name = 'emergency_alerts'
        AND column_name = 'location'
);

SET @add_alert_location_sql = IF(
    @has_alert_location = 0,
    'ALTER TABLE emergency_alerts
        ADD COLUMN location VARCHAR(255) NOT NULL DEFAULT ''Not provided''
        AFTER reason',
    'SELECT 1'
);

PREPARE add_alert_location_stmt FROM @add_alert_location_sql;
EXECUTE add_alert_location_stmt;
DEALLOCATE PREPARE add_alert_location_stmt;

SET @has_alert_contact_number = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
        AND table_name = 'emergency_alerts'
        AND column_name = 'contact_number'
);

SET @add_alert_contact_number_sql = IF(
    @has_alert_contact_number = 0,
    'ALTER TABLE emergency_alerts
        ADD COLUMN contact_number VARCHAR(30) NULL
        AFTER location',
    'SELECT 1'
);

PREPARE add_alert_contact_number_stmt FROM @add_alert_contact_number_sql;
EXECUTE add_alert_contact_number_stmt;
DEALLOCATE PREPARE add_alert_contact_number_stmt;

SET @has_alert_acknowledged_by = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
        AND table_name = 'emergency_alerts'
        AND column_name = 'acknowledged_by'
);

SET @add_alert_acknowledged_by_sql = IF(
    @has_alert_acknowledged_by = 0,
    'ALTER TABLE emergency_alerts
        ADD COLUMN acknowledged_by INT NULL
        AFTER created_at',
    'SELECT 1'
);

PREPARE add_alert_acknowledged_by_stmt FROM @add_alert_acknowledged_by_sql;
EXECUTE add_alert_acknowledged_by_stmt;
DEALLOCATE PREPARE add_alert_acknowledged_by_stmt;

SET @has_alert_acknowledged_at = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
        AND table_name = 'emergency_alerts'
        AND column_name = 'acknowledged_at'
);

SET @add_alert_acknowledged_at_sql = IF(
    @has_alert_acknowledged_at = 0,
    'ALTER TABLE emergency_alerts
        ADD COLUMN acknowledged_at TIMESTAMP NULL
        AFTER acknowledged_by',
    'SELECT 1'
);

PREPARE add_alert_acknowledged_at_stmt FROM @add_alert_acknowledged_at_sql;
EXECUTE add_alert_acknowledged_at_stmt;
DEALLOCATE PREPARE add_alert_acknowledged_at_stmt;

SET @has_alert_resolved_by = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
        AND table_name = 'emergency_alerts'
        AND column_name = 'resolved_by'
);

SET @add_alert_resolved_by_sql = IF(
    @has_alert_resolved_by = 0,
    'ALTER TABLE emergency_alerts
        ADD COLUMN resolved_by INT NULL
        AFTER acknowledged_at',
    'SELECT 1'
);

PREPARE add_alert_resolved_by_stmt FROM @add_alert_resolved_by_sql;
EXECUTE add_alert_resolved_by_stmt;
DEALLOCATE PREPARE add_alert_resolved_by_stmt;

SET @has_alert_resolved_at = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
        AND table_name = 'emergency_alerts'
        AND column_name = 'resolved_at'
);

SET @add_alert_resolved_at_sql = IF(
    @has_alert_resolved_at = 0,
    'ALTER TABLE emergency_alerts
        ADD COLUMN resolved_at TIMESTAMP NULL
        AFTER resolved_by',
    'SELECT 1'
);

PREPARE add_alert_resolved_at_stmt FROM @add_alert_resolved_at_sql;
EXECUTE add_alert_resolved_at_stmt;
DEALLOCATE PREPARE add_alert_resolved_at_stmt;

SET @has_alert_resolution_note = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
        AND table_name = 'emergency_alerts'
        AND column_name = 'resolution_note'
);

SET @add_alert_resolution_note_sql = IF(
    @has_alert_resolution_note = 0,
    'ALTER TABLE emergency_alerts
        ADD COLUMN resolution_note VARCHAR(1000) NULL
        AFTER resolved_at',
    'SELECT 1'
);

PREPARE add_alert_resolution_note_stmt FROM @add_alert_resolution_note_sql;
EXECUTE add_alert_resolution_note_stmt;
DEALLOCATE PREPARE add_alert_resolution_note_stmt;

SET @has_alert_acknowledged_by_fk = (
    SELECT COUNT(*)
    FROM information_schema.referential_constraints
    WHERE constraint_schema = DATABASE()
        AND constraint_name = 'fk_emergency_alerts_acknowledged_by'
);

SET @add_alert_acknowledged_by_fk_sql = IF(
    @has_alert_acknowledged_by_fk = 0,
    'ALTER TABLE emergency_alerts
        ADD CONSTRAINT fk_emergency_alerts_acknowledged_by
        FOREIGN KEY (acknowledged_by) REFERENCES users(user_id)
        ON DELETE SET NULL',
    'SELECT 1'
);

PREPARE add_alert_acknowledged_by_fk_stmt
    FROM @add_alert_acknowledged_by_fk_sql;
EXECUTE add_alert_acknowledged_by_fk_stmt;
DEALLOCATE PREPARE add_alert_acknowledged_by_fk_stmt;

SET @has_alert_resolved_by_fk = (
    SELECT COUNT(*)
    FROM information_schema.referential_constraints
    WHERE constraint_schema = DATABASE()
        AND constraint_name = 'fk_emergency_alerts_resolved_by'
);

SET @add_alert_resolved_by_fk_sql = IF(
    @has_alert_resolved_by_fk = 0,
    'ALTER TABLE emergency_alerts
        ADD CONSTRAINT fk_emergency_alerts_resolved_by
        FOREIGN KEY (resolved_by) REFERENCES users(user_id)
        ON DELETE SET NULL',
    'SELECT 1'
);

PREPARE add_alert_resolved_by_fk_stmt
    FROM @add_alert_resolved_by_fk_sql;
EXECUTE add_alert_resolved_by_fk_stmt;
DEALLOCATE PREPARE add_alert_resolved_by_fk_stmt;

SET @has_emergency_alerts_lifecycle_index = (
    SELECT COUNT(*)
    FROM information_schema.statistics
    WHERE table_schema = DATABASE()
        AND table_name = 'emergency_alerts'
        AND index_name = 'idx_emergency_alerts_lifecycle_created'
);

SET @create_emergency_alerts_lifecycle_index_sql = IF(
    @has_emergency_alerts_lifecycle_index = 0,
    'CREATE INDEX idx_emergency_alerts_lifecycle_created
        ON emergency_alerts(resolved_at, acknowledged_at, created_at)',
    'SELECT 1'
);

PREPARE create_emergency_alerts_lifecycle_index_stmt
    FROM @create_emergency_alerts_lifecycle_index_sql;
EXECUTE create_emergency_alerts_lifecycle_index_stmt;
DEALLOCATE PREPARE create_emergency_alerts_lifecycle_index_stmt;
