ER Diagram Notes

Entities

Users

- user_id (PK)
- name
- email
- role_id (FK)

Roles

- role_id (PK)
- role_name

Students

- student_id (PK)
- user_id (FK)

Staff

- staff_id (PK)
- user_id (FK)

Appointment_Slots

- slot_id (PK)
- staff_id (FK)
- date
- start_time
- end_time

Appointments

- appointment_id (PK)
- student_id (FK)
- staff_id (FK)
- slot_id (FK, UNIQUE)
- status

Medical_Notes

- note_id (PK)
- appointment_id (FK)
- diagnosis
- remarks

Prescriptions

- prescription_id (PK)
- appointment_id (FK)

Prescription_Items

- item_id (PK)
- prescription_id (FK)
- medicine_name
- dosage

Medical_Certificates

- certificate_id (PK)
- appointment_id (FK)
- type
- issue_date

Relationships

User → Student (1:1)
User → Staff (1:1)
Staff → Appointment Slots (1:M)
Student → Appointments (1:M)
Slot → Appointment (1:1)
Appointment → Notes (1:1)
Appointment → Prescriptions (1:M)
Prescription → Items (1:M)
Appointment → Certificate (1:1)

Normalization

- Role stored separately
- No repeated doctor/student info in appointments
- Prescription split into items table
- Slot separated from appointment

Constraints

- UNIQUE(slot_id) in appointments
- Foreign keys everywhere
- Prevent duplicate bookings
