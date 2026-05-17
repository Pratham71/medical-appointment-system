-- Repair cancelled appointment rebooking for local databases created before
-- active_slot_id was managed explicitly by appointment writes.

SET @active_slot_index_exists = (
    SELECT COUNT(*)
    FROM information_schema.statistics
    WHERE table_schema = DATABASE()
        AND table_name = 'appointments'
        AND index_name = 'active_slot_id'
);

SET @drop_active_slot_index_sql = IF(
    @active_slot_index_exists > 0,
    'DROP INDEX active_slot_id ON appointments',
    'SELECT 1'
);

PREPARE drop_active_slot_index_stmt
    FROM @drop_active_slot_index_sql;
EXECUTE drop_active_slot_index_stmt;
DEALLOCATE PREPARE drop_active_slot_index_stmt;

SET @active_slot_column_exists = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
        AND table_name = 'appointments'
        AND column_name = 'active_slot_id'
);

SET @drop_active_slot_column_sql = IF(
    @active_slot_column_exists > 0,
    'ALTER TABLE appointments DROP COLUMN active_slot_id',
    'SELECT 1'
);

PREPARE drop_active_slot_column_stmt
    FROM @drop_active_slot_column_sql;
EXECUTE drop_active_slot_column_stmt;
DEALLOCATE PREPARE drop_active_slot_column_stmt;

ALTER TABLE appointments
    ADD COLUMN active_slot_id INT NULL AFTER status_id;

UPDATE appointments
INNER JOIN appointment_statuses
    ON appointment_statuses.status_id = appointments.status_id
SET appointments.active_slot_id =
    CASE
        WHEN appointment_statuses.status_name = 'cancelled' THEN NULL
        ELSE appointments.slot_id
    END;

UPDATE appointments
INNER JOIN appointment_statuses
    ON appointment_statuses.status_id = appointments.status_id
SET appointments.active_slot_id = NULL
WHERE appointment_statuses.status_name = 'cancelled';

ALTER TABLE appointments
    ADD UNIQUE INDEX active_slot_id (active_slot_id);

UPDATE appointment_slots
INNER JOIN slot_statuses
    ON slot_statuses.status_name = 'available'
SET appointment_slots.slot_status_id = slot_statuses.slot_status_id
WHERE EXISTS (
        SELECT 1
        FROM appointments
        INNER JOIN appointment_statuses
            ON appointment_statuses.status_id = appointments.status_id
        WHERE appointments.slot_id = appointment_slots.slot_id
            AND appointment_statuses.status_name = 'cancelled'
    )
    AND NOT EXISTS (
        SELECT 1
        FROM appointments AS active_appointments
        INNER JOIN appointment_statuses AS active_statuses
            ON active_statuses.status_id = active_appointments.status_id
        WHERE active_appointments.slot_id = appointment_slots.slot_id
            AND active_statuses.status_name <> 'cancelled'
    );
