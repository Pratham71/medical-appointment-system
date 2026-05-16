ER Diagram Notes

Status

- Do not generate the final ER diagram yet.
- These notes track the current MySQL schema shape.

Entities

Users

- user_id (PK)
- role_id (FK)
- name
- email
- password_hash
- is_active

Roles

- role_id (PK)
- role_name

Students

- student_id (PK)
- user_id (FK)
- roll_number
- department
- year_level

Staff

- staff_id (PK)
- user_id (FK)
- employee_number
- specialization
- is_doctor

Doctor_Weekly_Availability

- availability_id (PK)
- staff_id (FK)
- weekday
- is_available
- start_time
- end_time

Doctor_Availability_Overrides

- override_id (PK)
- staff_id (FK)
- override_date
- is_available
- start_time
- end_time
- note

Appointment_Statuses

- status_id (PK)
- status_name

Slot_Statuses

- slot_status_id (PK)
- status_name

Appointment_Slots

- slot_id (PK)
- staff_id (FK)
- slot_status_id (FK)
- slot_date
- start_time
- end_time

Appointments

- appointment_id (PK)
- student_id (FK)
- slot_id (FK)
- status_id (FK)
- active_slot_id (generated, UNIQUE for non-cancelled appointments)
- reason

Medical_Notes

- note_id (PK)
- appointment_id (FK, UNIQUE)
- diagnosis
- remarks

Prescriptions

- prescription_id (PK)
- appointment_id (FK, UNIQUE)

Prescription_Items

- item_id (PK)
- prescription_id (FK)
- medicine_name
- dosage

Certificate_Types

- certificate_type_id (PK)
- certificate_type

Medical_Certificates

- certificate_id (PK)
- appointment_id (FK)
- certificate_type_id (FK)
- issue_date
- leave_start_date
- leave_end_date
- certificate_notes

Relationships

- User -> Student (1:1)
- User -> Staff (1:1)
- Staff -> Doctor Weekly Availability (1:M)
- Staff -> Doctor Availability Overrides (1:M)
- Staff -> Appointment Slots (1:M)
- Student -> Appointments (1:M)
- Slot -> Appointment (1:1)
- Appointment -> Medical Notes (1:1)
- Appointment -> Prescription (1:1)
- Prescription -> Items (1:M)
- Appointment -> Medical Certificates (1:M)

Normalization

- Role stored separately.
- Status values stored in lookup tables.
- No repeated doctor or student info in appointments.
- Prescription split into prescription and prescription item tables.
- Slot separated from appointment to prevent duplicate bookings.
- Doctor weekly availability and date overrides are separated from appointment slots so recurring rules do not duplicate per slot.

Constraints

- UNIQUE(active_slot_id) in appointments prevents double booking for active appointments while allowing cancelled appointments to release the slot.
- UNIQUE(staff_id, weekday) in doctor_weekly_availability.
- UNIQUE(staff_id, override_date) in doctor_availability_overrides.
- Foreign keys across all related tables.
- UNIQUE(appointment_id) in medical_notes and prescriptions.
- UNIQUE(appointment_id, certificate_type_id) in medical_certificates.
