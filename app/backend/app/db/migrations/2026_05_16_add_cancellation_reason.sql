-- Add infirmary cancellation context for doctor availability overrides.

SET @has_cancellation_reason = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
        AND table_name = 'appointments'
        AND column_name = 'cancellation_reason'
);

SET @add_cancellation_reason_sql = IF(
    @has_cancellation_reason = 0,
    'ALTER TABLE appointments
        ADD COLUMN cancellation_reason VARCHAR(500) NULL DEFAULT NULL
        AFTER reason',
    'SELECT 1'
);

PREPARE add_cancellation_reason_stmt
    FROM @add_cancellation_reason_sql;
EXECUTE add_cancellation_reason_stmt;
DEALLOCATE PREPARE add_cancellation_reason_stmt;

CREATE OR REPLACE VIEW v_appointment_details AS
SELECT
    appointments.appointment_id,
    appointments.student_id,
    student_users.name AS student_name,
    student_users.email AS student_email,
    staff.staff_id AS doctor_id,
    doctor_users.name AS doctor_name,
    appointment_slots.slot_date,
    appointment_slots.start_time,
    appointment_slots.end_time,
    appointment_statuses.status_name AS status,
    appointments.reason,
    appointments.cancellation_reason,
    medical_notes.diagnosis,
    medical_notes.remarks,
    medical_certificates.certificate_id,
    certificate_types.certificate_type
FROM appointments
INNER JOIN students ON students.student_id = appointments.student_id
INNER JOIN users AS student_users ON student_users.user_id = students.user_id
INNER JOIN appointment_slots
    ON appointment_slots.slot_id = appointments.slot_id
INNER JOIN staff ON staff.staff_id = appointment_slots.staff_id
INNER JOIN users AS doctor_users ON doctor_users.user_id = staff.user_id
INNER JOIN appointment_statuses
    ON appointment_statuses.status_id = appointments.status_id
LEFT JOIN medical_notes
    ON medical_notes.appointment_id = appointments.appointment_id
LEFT JOIN medical_certificates
    ON medical_certificates.appointment_id = appointments.appointment_id
LEFT JOIN certificate_types
    ON certificate_types.certificate_type_id =
        medical_certificates.certificate_type_id;
