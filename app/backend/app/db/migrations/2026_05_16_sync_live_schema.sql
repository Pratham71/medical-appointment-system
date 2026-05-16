-- Repair older local MySQL databases without dropping existing appointment data.
-- This syncs the live DB with the availability and certificate view changes.

CREATE TABLE IF NOT EXISTS doctor_weekly_availability (
    availability_id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL,
    weekday TINYINT UNSIGNED NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    start_time TIME NULL,
    end_time TIME NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE (staff_id, weekday),
    CONSTRAINT fk_doctor_weekly_availability_staff
        FOREIGN KEY (staff_id) REFERENCES staff(staff_id)
        ON DELETE CASCADE,
    CONSTRAINT chk_doctor_weekly_availability_weekday
        CHECK (weekday BETWEEN 0 AND 6),
    CONSTRAINT chk_doctor_weekly_availability_time_range
        CHECK (
            start_time IS NULL
            OR end_time IS NULL
            OR end_time > start_time
        )
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS doctor_availability_overrides (
    override_id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL,
    override_date DATE NOT NULL,
    is_available BOOLEAN NOT NULL,
    start_time TIME NULL,
    end_time TIME NULL,
    note VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE (staff_id, override_date),
    CONSTRAINT fk_doctor_availability_overrides_staff
        FOREIGN KEY (staff_id) REFERENCES staff(staff_id)
        ON DELETE CASCADE,
    CONSTRAINT chk_doctor_availability_overrides_time_range
        CHECK (
            start_time IS NULL
            OR end_time IS NULL
            OR end_time > start_time
        )
) ENGINE=InnoDB;

SET @has_legacy_doctor_availability = (
    SELECT COUNT(*)
    FROM information_schema.tables
    WHERE table_schema = DATABASE()
        AND table_name = 'doctor_availability'
);

SET @copy_legacy_doctor_availability_sql = IF(
    @has_legacy_doctor_availability > 0,
    'INSERT INTO doctor_weekly_availability (
        staff_id,
        weekday,
        is_available,
        start_time,
        end_time
    )
    SELECT
        doctor_availability.staff_id,
        doctor_availability.day_of_week,
        CASE
            WHEN doctor_availability.day_of_week = 6 THEN FALSE
            ELSE doctor_availability.is_available
        END,
        CASE
            WHEN doctor_availability.day_of_week = 6 THEN NULL
            ELSE doctor_availability.start_time
        END,
        CASE
            WHEN doctor_availability.day_of_week = 6 THEN NULL
            ELSE doctor_availability.end_time
        END
    FROM doctor_availability
    ON DUPLICATE KEY UPDATE
        is_available = VALUES(is_available),
        start_time = VALUES(start_time),
        end_time = VALUES(end_time)',
    'SELECT 1'
);

PREPARE copy_legacy_doctor_availability_stmt
    FROM @copy_legacy_doctor_availability_sql;
EXECUTE copy_legacy_doctor_availability_stmt;
DEALLOCATE PREPARE copy_legacy_doctor_availability_stmt;

INSERT INTO doctor_weekly_availability (
    staff_id,
    weekday,
    is_available,
    start_time,
    end_time
)
SELECT
    staff.staff_id,
    weekdays.weekday,
    weekdays.is_available,
    weekdays.start_time,
    weekdays.end_time
FROM staff
CROSS JOIN (
    SELECT 0 AS weekday, TRUE AS is_available, TIME '09:00:00' AS start_time, TIME '17:00:00' AS end_time
    UNION ALL SELECT 1, TRUE, TIME '09:00:00', TIME '17:00:00'
    UNION ALL SELECT 2, TRUE, TIME '09:00:00', TIME '17:00:00'
    UNION ALL SELECT 3, TRUE, TIME '09:00:00', TIME '17:00:00'
    UNION ALL SELECT 4, TRUE, TIME '09:00:00', TIME '17:00:00'
    UNION ALL SELECT 5, TRUE, TIME '09:00:00', TIME '17:00:00'
    UNION ALL SELECT 6, FALSE, NULL, NULL
) AS weekdays
WHERE staff.is_doctor = TRUE
ON DUPLICATE KEY UPDATE
    weekday = VALUES(weekday);

CREATE OR REPLACE VIEW v_available_appointment_slots AS
SELECT
    appointment_slots.slot_id,
    staff.staff_id AS doctor_id,
    users.name AS doctor_name,
    staff.specialization,
    appointment_slots.slot_date,
    appointment_slots.start_time,
    appointment_slots.end_time,
    slot_statuses.status_name AS slot_status
FROM appointment_slots
INNER JOIN staff ON staff.staff_id = appointment_slots.staff_id
INNER JOIN users ON users.user_id = staff.user_id
INNER JOIN slot_statuses
    ON slot_statuses.slot_status_id = appointment_slots.slot_status_id
LEFT JOIN doctor_availability_overrides
    ON doctor_availability_overrides.staff_id = appointment_slots.staff_id
    AND doctor_availability_overrides.override_date = appointment_slots.slot_date
LEFT JOIN doctor_weekly_availability
    ON doctor_weekly_availability.staff_id = appointment_slots.staff_id
    AND doctor_weekly_availability.weekday = WEEKDAY(appointment_slots.slot_date)
WHERE slot_statuses.status_name = 'available'
    AND staff.is_doctor = TRUE
    AND (
        (
            doctor_availability_overrides.override_id IS NOT NULL
            AND doctor_availability_overrides.is_available = TRUE
            AND (
                doctor_availability_overrides.start_time IS NULL
                OR appointment_slots.start_time >=
                    doctor_availability_overrides.start_time
            )
            AND (
                doctor_availability_overrides.end_time IS NULL
                OR appointment_slots.end_time <=
                    doctor_availability_overrides.end_time
            )
        )
        OR (
            doctor_availability_overrides.override_id IS NULL
            AND COALESCE(doctor_weekly_availability.is_available, WEEKDAY(appointment_slots.slot_date) < 6) = TRUE
            AND (
                doctor_weekly_availability.start_time IS NULL
                OR appointment_slots.start_time >=
                    doctor_weekly_availability.start_time
            )
            AND (
                doctor_weekly_availability.end_time IS NULL
                OR appointment_slots.end_time <=
                    doctor_weekly_availability.end_time
            )
        )
    );

CREATE OR REPLACE VIEW v_student_certificate_summaries AS
SELECT
    medical_certificates.certificate_id,
    appointments.appointment_id,
    appointments.student_id,
    student_users.name AS student_name,
    certificate_types.certificate_type_id,
    certificate_types.certificate_type,
    medical_certificates.issue_date,
    staff.staff_id AS doctor_id,
    doctor_users.name AS doctor_name,
    appointment_slots.slot_date AS appointment_date,
    appointments.reason AS appointment_reason,
    medical_notes.diagnosis,
    medical_notes.remarks,
    medical_certificates.leave_start_date,
    medical_certificates.leave_end_date,
    medical_certificates.certificate_notes
FROM medical_certificates
INNER JOIN appointments
    ON appointments.appointment_id = medical_certificates.appointment_id
INNER JOIN students ON students.student_id = appointments.student_id
INNER JOIN users AS student_users ON student_users.user_id = students.user_id
INNER JOIN certificate_types
    ON certificate_types.certificate_type_id =
        medical_certificates.certificate_type_id
INNER JOIN appointment_slots
    ON appointment_slots.slot_id = appointments.slot_id
INNER JOIN staff ON staff.staff_id = appointment_slots.staff_id
INNER JOIN users AS doctor_users ON doctor_users.user_id = staff.user_id
LEFT JOIN medical_notes
    ON medical_notes.appointment_id = appointments.appointment_id;
