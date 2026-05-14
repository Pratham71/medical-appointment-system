SET FOREIGN_KEY_CHECKS = 0;

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
    reason VARCHAR(500) NULL,
    booked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE (slot_id),
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
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (appointment_id, certificate_type_id),
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
