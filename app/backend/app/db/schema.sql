SET FOREIGN_KEY_CHECKS = 0;

DROP TRIGGER IF EXISTS trg_medical_certificates_validate_update;
DROP TRIGGER IF EXISTS trg_medical_certificates_validate_insert;

DROP VIEW IF EXISTS v_student_certificate_summaries;
DROP VIEW IF EXISTS v_student_report_summaries;
DROP VIEW IF EXISTS v_doctor_appointment_summaries;
DROP VIEW IF EXISTS v_appointment_details;
DROP VIEW IF EXISTS v_available_appointment_slots;

DROP TABLE IF EXISTS prescription_items;
DROP TABLE IF EXISTS prescriptions;
DROP TABLE IF EXISTS medical_certificates;
DROP TABLE IF EXISTS medical_notes;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS appointment_slots;
DROP TABLE IF EXISTS slot_statuses;
DROP TABLE IF EXISTS appointment_statuses;
DROP TABLE IF EXISTS staff;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS certificate_types;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL,
    UNIQUE (role_name)
) ENGINE=InnoDB;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT NOT NULL,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE (email),
    CONSTRAINT fk_users_role
        FOREIGN KEY (role_id) REFERENCES roles(role_id)
) ENGINE=InnoDB;

CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    roll_number VARCHAR(50) NOT NULL,
    department VARCHAR(120) NOT NULL,
    year_level TINYINT UNSIGNED NOT NULL,
    UNIQUE (user_id),
    UNIQUE (roll_number),
    CONSTRAINT fk_students_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT chk_students_year_level
        CHECK (year_level BETWEEN 1 AND 6)
) ENGINE=InnoDB;

CREATE TABLE staff (
    staff_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    employee_number VARCHAR(50) NOT NULL,
    specialization VARCHAR(120) NULL,
    is_doctor BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (user_id),
    UNIQUE (employee_number),
    CONSTRAINT fk_staff_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE appointment_statuses (
    status_id INT AUTO_INCREMENT PRIMARY KEY,
    status_name VARCHAR(50) NOT NULL,
    UNIQUE (status_name)
) ENGINE=InnoDB;

CREATE TABLE slot_statuses (
    slot_status_id INT AUTO_INCREMENT PRIMARY KEY,
    status_name VARCHAR(50) NOT NULL,
    UNIQUE (status_name)
) ENGINE=InnoDB;

CREATE TABLE appointment_slots (
    slot_id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL,
    slot_status_id INT NOT NULL,
    slot_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (staff_id, slot_date, start_time, end_time),
    CONSTRAINT fk_appointment_slots_staff
        FOREIGN KEY (staff_id) REFERENCES staff(staff_id),
    CONSTRAINT fk_appointment_slots_status
        FOREIGN KEY (slot_status_id) REFERENCES slot_statuses(slot_status_id),
    CONSTRAINT chk_appointment_slots_time_range
        CHECK (end_time > start_time)
) ENGINE=InnoDB;

CREATE TABLE appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    slot_id INT NOT NULL,
    status_id INT NOT NULL,
    active_slot_id INT GENERATED ALWAYS AS (
        CASE WHEN status_id = 2 THEN NULL ELSE slot_id END
    ) STORED,
    reason VARCHAR(500) NULL,
    booked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE (active_slot_id),
    CONSTRAINT fk_appointments_student
        FOREIGN KEY (student_id) REFERENCES students(student_id),
    CONSTRAINT fk_appointments_slot
        FOREIGN KEY (slot_id) REFERENCES appointment_slots(slot_id),
    CONSTRAINT fk_appointments_status
        FOREIGN KEY (status_id) REFERENCES appointment_statuses(status_id)
) ENGINE=InnoDB;

CREATE TABLE medical_notes (
    note_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL,
    diagnosis VARCHAR(255) NOT NULL,
    remarks VARCHAR(1000) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE (appointment_id),
    CONSTRAINT fk_medical_notes_appointment
        FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE prescriptions (
    prescription_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (appointment_id),
    CONSTRAINT fk_prescriptions_appointment
        FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE prescription_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    prescription_id INT NOT NULL,
    medicine_name VARCHAR(255) NOT NULL,
    dosage VARCHAR(255) NOT NULL,
    CONSTRAINT fk_prescription_items_prescription
        FOREIGN KEY (prescription_id) REFERENCES prescriptions(prescription_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE certificate_types (
    certificate_type_id INT AUTO_INCREMENT PRIMARY KEY,
    certificate_type VARCHAR(120) NOT NULL,
    UNIQUE (certificate_type)
) ENGINE=InnoDB;

CREATE TABLE medical_certificates (
    certificate_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL,
    certificate_type_id INT NOT NULL,
    issue_date DATE NOT NULL,
    leave_start_date DATE NULL,
    leave_end_date DATE NULL,
    certificate_notes TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (appointment_id, certificate_type_id),
    CONSTRAINT chk_medical_certificates_leave_range
        CHECK (
            leave_start_date IS NULL
            OR leave_end_date IS NULL
            OR leave_end_date >= leave_start_date
        ),
    CONSTRAINT fk_medical_certificates_appointment
        FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_medical_certificates_type
        FOREIGN KEY (certificate_type_id) REFERENCES certificate_types(certificate_type_id)
) ENGINE=InnoDB;

CREATE INDEX idx_users_role ON users(role_id);
CREATE INDEX idx_students_user ON students(user_id);
CREATE INDEX idx_staff_user ON staff(user_id);
CREATE INDEX idx_appointment_slots_staff_date ON appointment_slots(staff_id, slot_date);
CREATE INDEX idx_appointment_slots_date_status ON appointment_slots(slot_date, slot_status_id);
CREATE INDEX idx_appointments_student ON appointments(student_id);
CREATE INDEX idx_appointments_status ON appointments(status_id);
CREATE INDEX idx_medical_notes_appointment ON medical_notes(appointment_id);
CREATE INDEX idx_prescriptions_appointment ON prescriptions(appointment_id);
CREATE INDEX idx_prescription_items_prescription ON prescription_items(prescription_id);
CREATE INDEX idx_medical_certificates_type ON medical_certificates(certificate_type_id);

DELIMITER //

CREATE TRIGGER trg_medical_certificates_validate_insert
BEFORE INSERT ON medical_certificates
FOR EACH ROW
BEGIN
    DECLARE appointment_date DATE;

    SELECT appointment_slots.slot_date
    INTO appointment_date
    FROM appointments
    INNER JOIN appointment_slots
        ON appointment_slots.slot_id = appointments.slot_id
    WHERE appointments.appointment_id = NEW.appointment_id;

    IF appointment_date IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Appointment not found for certificate';
    END IF;

    IF NEW.issue_date < appointment_date THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Certificate issue date cannot be before appointment date';
    END IF;

    IF appointment_date > CURRENT_DATE THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot issue certificate for a future appointment';
    END IF;
END//

CREATE TRIGGER trg_medical_certificates_validate_update
BEFORE UPDATE ON medical_certificates
FOR EACH ROW
BEGIN
    DECLARE appointment_date DATE;

    SELECT appointment_slots.slot_date
    INTO appointment_date
    FROM appointments
    INNER JOIN appointment_slots
        ON appointment_slots.slot_id = appointments.slot_id
    WHERE appointments.appointment_id = NEW.appointment_id;

    IF appointment_date IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Appointment not found for certificate';
    END IF;

    IF NEW.issue_date < appointment_date THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Certificate issue date cannot be before appointment date';
    END IF;

    IF appointment_date > CURRENT_DATE THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot issue certificate for a future appointment';
    END IF;
END//

DELIMITER ;

CREATE VIEW v_available_appointment_slots AS
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
WHERE slot_statuses.status_name = 'available'
    AND staff.is_doctor = TRUE;

CREATE VIEW v_appointment_details AS
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

CREATE VIEW v_doctor_appointment_summaries AS
SELECT
    appointments.appointment_id,
    staff.staff_id AS doctor_id,
    appointment_slots.slot_date,
    appointment_slots.start_time,
    appointment_slots.end_time,
    students.student_id,
    student_users.name AS student_name,
    appointment_statuses.status_name AS status
FROM appointments
INNER JOIN appointment_slots
    ON appointment_slots.slot_id = appointments.slot_id
INNER JOIN staff ON staff.staff_id = appointment_slots.staff_id
INNER JOIN appointment_statuses
    ON appointment_statuses.status_id = appointments.status_id
INNER JOIN students ON students.student_id = appointments.student_id
INNER JOIN users AS student_users ON student_users.user_id = students.user_id;

CREATE VIEW v_student_report_summaries AS
SELECT
    appointments.appointment_id,
    appointments.student_id,
    appointment_slots.slot_date AS appointment_date,
    staff.staff_id AS doctor_id,
    doctor_users.name AS doctor_name,
    medical_notes.diagnosis,
    medical_notes.remarks,
    COUNT(prescription_items.item_id) AS prescription_count
FROM appointments
INNER JOIN appointment_slots
    ON appointment_slots.slot_id = appointments.slot_id
INNER JOIN staff ON staff.staff_id = appointment_slots.staff_id
INNER JOIN users AS doctor_users ON doctor_users.user_id = staff.user_id
INNER JOIN medical_notes
    ON medical_notes.appointment_id = appointments.appointment_id
LEFT JOIN prescriptions
    ON prescriptions.appointment_id = appointments.appointment_id
LEFT JOIN prescription_items
    ON prescription_items.prescription_id = prescriptions.prescription_id
GROUP BY
    appointments.appointment_id,
    appointments.student_id,
    appointment_slots.slot_date,
    staff.staff_id,
    doctor_users.name,
    medical_notes.diagnosis,
    medical_notes.remarks;

CREATE VIEW v_student_certificate_summaries AS
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
