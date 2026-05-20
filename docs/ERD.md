Entity Relationship Diagram

This ERD represents the current MySQL schema for the college infirmary medical appointment system.

Views are not modeled as separate entities because they are derived from the base tables.
Professor, college-staff, and hostel-staff accounts currently use the same patient profile workflow as students while keeping distinct role names in `roles`.

```mermaid
erDiagram
    ROLES {
        int role_id PK
        varchar role_name UK
    }

    USERS {
        int user_id PK
        int role_id FK
        varchar name
        varchar email UK
        varchar password_hash
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    STUDENTS {
        int student_id PK
        int user_id FK "unique"
        varchar roll_number UK
        varchar department
        tinyint year_level
    }

    STAFF {
        int staff_id PK
        int user_id FK "unique"
        varchar employee_number UK
        varchar specialization
        boolean is_doctor
    }

    DOCTOR_WEEKLY_AVAILABILITY {
        int availability_id PK
        int staff_id FK
        tinyint weekday
        boolean is_available
        time start_time
        time end_time
        timestamp created_at
        timestamp updated_at
    }

    DOCTOR_AVAILABILITY_OVERRIDES {
        int override_id PK
        int staff_id FK
        date override_date
        boolean is_available
        time start_time
        time end_time
        varchar note
        timestamp created_at
        timestamp updated_at
    }

    SLOT_STATUSES {
        int slot_status_id PK
        varchar status_name UK
    }

    APPOINTMENT_STATUSES {
        int status_id PK
        varchar status_name UK
    }

    APPOINTMENT_SLOTS {
        int slot_id PK
        int staff_id FK
        int slot_status_id FK
        date slot_date
        time start_time
        time end_time
        timestamp created_at
    }

    APPOINTMENTS {
        int appointment_id PK
        int student_id FK
        int slot_id FK
        int status_id FK
        int active_slot_id "generated unique for non-cancelled"
        varchar reason
        varchar cancellation_reason
        timestamp booked_at
        timestamp updated_at
    }

    MEDICAL_NOTES {
        int note_id PK
        int appointment_id FK "unique"
        varchar diagnosis
        varchar remarks
        timestamp created_at
        timestamp updated_at
    }

    PRESCRIPTIONS {
        int prescription_id PK
        int appointment_id FK "unique"
        timestamp created_at
    }

    PRESCRIPTION_ITEMS {
        int item_id PK
        int prescription_id FK
        varchar medicine_name
        varchar dosage
    }

    CERTIFICATE_TYPES {
        int certificate_type_id PK
        varchar certificate_type UK
    }

    MEDICAL_CERTIFICATES {
        int certificate_id PK
        int appointment_id FK
        int certificate_type_id FK
        date issue_date
        date leave_start_date
        date leave_end_date
        text certificate_notes
        timestamp created_at
    }

    EMERGENCY_ALERTS {
        int alert_id PK
        int student_id FK
        varchar reason
        varchar location
        varchar contact_number
        varchar message
        timestamp created_at
        int acknowledged_by FK
        timestamp acknowledged_at
        int resolved_by FK
        timestamp resolved_at
        varchar resolution_note
    }

    ROLES ||--o{ USERS : assigned_to
    USERS ||--o| STUDENTS : has_patient_profile
    USERS ||--o| STAFF : has_staff_profile

    STAFF ||--o{ DOCTOR_WEEKLY_AVAILABILITY : has_weekly_rules
    STAFF ||--o{ DOCTOR_AVAILABILITY_OVERRIDES : has_date_overrides
    STAFF ||--o{ APPOINTMENT_SLOTS : owns_slots
    SLOT_STATUSES ||--o{ APPOINTMENT_SLOTS : labels

    STUDENTS ||--o{ APPOINTMENTS : books
    APPOINTMENT_SLOTS ||--o{ APPOINTMENTS : used_by
    APPOINTMENT_STATUSES ||--o{ APPOINTMENTS : labels

    APPOINTMENTS ||--o| MEDICAL_NOTES : has_note
    APPOINTMENTS ||--o| PRESCRIPTIONS : has_prescription
    PRESCRIPTIONS ||--o{ PRESCRIPTION_ITEMS : contains

    APPOINTMENTS ||--o{ MEDICAL_CERTIFICATES : produces
    CERTIFICATE_TYPES ||--o{ MEDICAL_CERTIFICATES : classifies

    STUDENTS ||--o{ EMERGENCY_ALERTS : raises
    USERS ||--o{ EMERGENCY_ALERTS : acknowledges
    USERS ||--o{ EMERGENCY_ALERTS : resolves
```

Key Constraints

- `users.email`, `roles.role_name`, status names, certificate type names, roll numbers, and employee numbers are unique.
- `students.user_id` and `staff.user_id` are unique, giving each account at most one patient or staff profile.
- `appointment_slots` are unique by doctor, date, start time, and end time.
- `appointments.active_slot_id` is generated and unique so cancelled appointments release the slot while active appointments cannot double-book it.
- `medical_notes.appointment_id` and `prescriptions.appointment_id` are unique, making each appointment have at most one note and one prescription.
- `medical_certificates` are unique by appointment and certificate type.
- Doctor availability has one weekly rule per doctor and weekday, plus one override per doctor and date.
