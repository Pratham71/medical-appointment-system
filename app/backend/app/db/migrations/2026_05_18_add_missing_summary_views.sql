-- Repair live databases that were migrated before the report and doctor
-- appointment summary views were added.

CREATE OR REPLACE VIEW v_doctor_appointment_summaries AS
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

CREATE OR REPLACE VIEW v_student_report_summaries AS
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
