# ClinicQueue — Database Schema

---

## Applications

### `accounts` app

**User:**

- `id` — int, PK
- `email` — string, unique
- `password` — string
- `first_name` — string
- `last_name` — string
- `role` — string, choices: PATIENT / DOCTOR / RECEPTIONIST / ADMIN
- `phone` — string, nullable
- `is_active` — bool, default True
- `created_at` — datetime, auto

**PatientProfile:**

- `id` — int, PK
- `user_id` — OneToOne FK → User
- `date_of_birth` — date, nullable
- `gender` — string, choices: MALE / FEMALE / OTHER, nullable

**DoctorProfile:**

- `id` — int, PK
- `user_id` — OneToOne FK → User
- `specialty` — string
- `consultation_duration` — int (minutes, choices: 15 / 30)
- `bio` — text, nullable

---

### `scheduling` app

**WeeklySchedule:**

- `id` — int, PK
- `doctor_id` — FK → DoctorProfile
- `day_of_week` — int, choices: 0=Monday … 6=Sunday
- `start_time` — time
- `end_time` — time
- `is_active` — bool, default True
- unique together: `(doctor_id, day_of_week)`

**ScheduleException:**

- `id` — int, PK
- `doctor_id` — FK → DoctorProfile
- `exception_date` — date
- `type` — string, choices: DAY_OFF / VACATION / EXTRA_WORKING
- `note` — string, nullable
- unique together: `(doctor_id, exception_date)`

**TimeSlot:**

- `id` — int, PK
- `doctor_id` — FK → DoctorProfile
- `start_datetime` — datetime
- `end_datetime` — datetime
- `is_available` — bool, default True
- unique together: `(doctor_id, start_datetime)`

---

### `appointments` app

**Appointment:**

- `id` — int, PK
- `patient_id` — FK → PatientProfile
- `doctor_id` — FK → DoctorProfile
- `slot_id` — OneToOne FK → TimeSlot (DB unique constraint — prevents double booking)
- `status` — string, choices: REQUESTED / CONFIRMED / CHECKED_IN / COMPLETED / CANCELLED / NO_SHOW
- `type` — string, choices: IN_PERSON / ONLINE, default IN_PERSON
- `reason` — text, nullable
- `meeting_link` — URL, nullable (telemedicine)
- `created_at` — datetime, auto
- `confirmed_at` — datetime, nullable
- `checked_in_at` — datetime, nullable
- `completed_at` — datetime, nullable

**RescheduleHistory:**

- `id` — int, PK
- `appointment_id` — FK → Appointment
- `old_slot_id` — FK → TimeSlot
- `new_slot_id` — FK → TimeSlot
- `changed_by_id` — FK → User
- `reason` — text
- `timestamp` — datetime, auto

**WaitingList:** (Bonus)

- `id` — int, PK
- `patient_id` — FK → PatientProfile
- `doctor_id` — FK → DoctorProfile
- `preferred_date` — date
- `hold_expires_at` — datetime, nullable
- `created_at` — datetime, auto

---

### `emr` app

**ConsultationRecord:**

- `id` — int, PK
- `appointment_id` — OneToOne FK → Appointment
- `created_by_id` — FK → User (always the doctor)
- `diagnosis` — string
- `notes` — text (hidden from receptionist)
- `created_at` — datetime, auto
- `updated_at` — datetime, auto

**PrescriptionItem:**

- `id` — int, PK
- `consultation_id` — FK → ConsultationRecord
- `drug_name` — string
- `dose` — string
- `duration` — string

**RequestedTest:**

- `id` — int, PK
- `consultation_id` — FK → ConsultationRecord
- `test_name` — string
- `notes` — string, nullable

---

### `analytics` app

**No models** —  No tables.

---

### `dashboard` app

**No models** — No tables.

---

### Bonus tables

**Notification** (in `accounts` app)

- `id` — int, PK
- `user_id` — FK → User (recipient)
- `appointment_id` — FK → Appointment, nullable
- `type` — string, choices: APPOINTMENT_CONFIRMED / APPOINTMENT_CANCELLED / APPOINTMENT_REMINDER / SLOT_AVAILABLE / CHECKED_IN
- `message` — text
- `is_read` — bool, default False
- `created_at` — datetime, auto

**Payment** (in `appointments` app):

- `id` — int, PK
- `appointment_id` — OneToOne FK → Appointment
- `amount` — decimal(8,2)
- `status` — string, choices: PENDING / PAID / REFUNDED
- `paid_at` — datetime, nullable
- `refunded_at` — datetime, nullable

---

## Relationships summary

| Table | Related to | Type |
| ----- | ---------- | ---- |
| PatientProfile | User | OneToOne |
| DoctorProfile | User | OneToOne |
| WeeklySchedule | DoctorProfile | ManyToOne |
| ScheduleException | DoctorProfile | ManyToOne |
| TimeSlot | DoctorProfile | ManyToOne |
| Appointment | PatientProfile | ManyToOne |
| Appointment | DoctorProfile | ManyToOne |
| Appointment | TimeSlot | OneToOne |
| RescheduleHistory | Appointment | ManyToOne |
| WaitingList | PatientProfile | ManyToOne |
| WaitingList | DoctorProfile | ManyToOne |
| ConsultationRecord | Appointment | OneToOne |
| PrescriptionItem | ConsultationRecord | ManyToOne |
| RequestedTest | ConsultationRecord | ManyToOne |
| Notification | User | ManyToOne |
| Notification | Appointment | ManyToOne |
| Payment | Appointment | OneToOne |

---

## Constraints that must exist at DB level

- `TimeSlot`: unique on `(doctor_id, start_datetime)` — no duplicate slots
- `Appointment.slot_id`: OneToOne — one appointment per slot maximum
- `WeeklySchedule`: unique on `(doctor_id, day_of_week)` — one schedule entry per day per doctor
- `ScheduleException`: unique on `(doctor_id, exception_date)` — one exception per date per doctor
- `ConsultationRecord.appointment_id`: OneToOne — one record per appointment
- `Payment.appointment_id`: OneToOne — one payment per appointment
