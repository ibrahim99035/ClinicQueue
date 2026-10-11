# ClinicQueue

A **Django 6 + Vue 3** clinic appointment scheduling and queue-management system.

- JWT auth with role-based access (Admin · Doctor · Receptionist · Patient)
- Doctor approval workflow (doctors stay *pending* until an admin approves them)
- Weekly schedules → auto-generated 15-minute time slots (with a 5-minute buffer)
- Appointments with the full lifecycle: Requested → Confirmed → Checked-In → Completed
- Patient self-booking + rescheduling, EMR/consultation records, analytics export

---

## Tech stack

| Layer    | Tech |
|----------|------|
| Backend  | Django 6, Django REST Framework, SimpleJWT, drf-spectacular, dj-database-url |
| Frontend | Vue 3, Pinia, Vue Router, Tailwind CSS 4, Vite |
| Database | SQLite (local dev) · PostgreSQL (production, via `DATABASE_URL`) |

---

## Setup

### Backend

The virtual environment lives at the **project root** (`ClinicQueue/.venv`), not inside `server/`.

```bash
cd ClinicQueue
python3 -m venv .venv
.venv/bin/pip install -r server/requirements.txt

cd server
../.venv/bin/python manage.py migrate
../.venv/bin/python manage.py runserver 127.0.0.1:8000
```

> `server/config/settings.py` falls back to SQLite automatically when `DATABASE_URL` is empty,
> so no PostgreSQL instance is required for local development.

### Frontend

```bash
cd ClinicQueue/client
npm install
npm run dev          # Vite dev server on http://127.0.0.1:5173 (proxies /api -> :8000)
```

Open **http://127.0.0.1:5173**.

---

## Environment

`server/.env` (optional — the defaults are fine for local dev):

```plaintext
DJANGO_SECRET=
DATABASE_URL=           # empty -> local SQLite
SLOT_BUFFER_MINUTES=5
```

---

## Demo accounts & seeded data

The demo data lives in `server/db.sqlite3`, which is **git-ignored**. After a fresh clone,
run the script below (from `server/`) to recreate every account, schedule, slot and appointment:

```bash
../.venv/bin/python manage.py shell <<'PYEOF'
from datetime import time, timedelta
from django.utils import timezone
from django.contrib.auth.models import Group
from accounts.models.user import User
from accounts.models.doctor import DoctorProfile
from accounts.models.patient import PatientProfile
from scheduling.models import WeeklySchedule, TimeSlot
from scheduling.services import generate_slots
from appointments.models import Appointment

for g in ['Patients','Doctors','Receptionists','Admins']:
    Group.objects.get_or_create(name=g)

if not User.objects.filter(email='admin@clinic.test').exists():
    admin = User.create_user(email='admin@clinic.test', password='AdminPass1!', first_name='Admin', last_name='User')
    admin.groups.add(Group.objects.get(name='Admins')); admin.is_staff = True; admin.is_active = True; admin.save()
else:
    admin = User.objects.get(email='admin@clinic.test')

def upsert(email, first, last, active, is_staff, group, pw):
    u, created = User.objects.get_or_create(email=email, defaults={'username': email, 'first_name': first, 'last_name': last})
    if not u.username: u.username = email
    if created: u.set_password(pw)
    u.is_active = active; u.is_staff = is_staff; u.save()
    u.groups.add(Group.objects.get(name=group)); return u

dp_u = upsert('doctor.approved@clinic.test','Ahmed','Karim',True,True,'Doctors','DoctorPass1!')
dp, _ = DoctorProfile.objects.get_or_create(user=dp_u, defaults={'specialization':'Cardiology','consultationDuration':15})
dp.is_approved = True; dp.approved_by = admin; dp.approved_at = timezone.now(); dp.save()

up_u = upsert('doctor.pending@clinic.test','Sara','Mostafa',False,False,'Doctors','DoctorPass1!')
DoctorProfile.objects.get_or_create(user=up_u, defaults={'specialization':'Dermatology','consultationDuration':15,'is_approved':False})

upsert('receptionist@clinic.test','Nour','Saad',True,False,'Receptionists','ReceptPass1!')
pu = upsert('patient@clinic.test','Hassan','Ali',True,False,'Patients','PatientPass1!')
pp, _ = PatientProfile.objects.get_or_create(user=pu)

for dow in range(5):
    WeeklySchedule.objects.get_or_create(doctor=dp, day_of_week=dow, defaults={'start_time':time(9,0),'end_time':time(17,0),'is_active':True})

start = timezone.now().date()
generate_slots(start, start + timedelta(days=5), dp.id)

for slot, (st, reason) in zip(TimeSlot.objects.filter(doctor=dp, is_available=True).order_by('start_datetime')[:3],
                              [('REQUESTED','Annual checkup'),('CONFIRMED','Follow-up visit'),('REQUESTED','Chest pain review')]):
    a, created = Appointment.objects.get_or_create(slot_id=slot, defaults={'patient_id':pp,'doctor_id':dp,'status':st,'reason':reason})
    if created and st == 'CONFIRMED': a.confirmed_at = timezone.now(); a.save()
    slot.is_available = False; slot.save()

print('Seeded.')
PYEOF
```

### Accounts

| Role              | Email                        | Password      | Notes |
|-------------------|------------------------------|---------------|-------|
| Admin             | `admin@clinic.test`          | `AdminPass1!` | Full access |
| Approved doctor   | `doctor.approved@clinic.test`| `DoctorPass1!`| Active, Cardiology, has schedules/slots/appointments |
| Pending doctor    | `doctor.pending@clinic.test` | `DoctorPass1!`| **Inactive** – login returns *"Your doctor account is pending admin approval."* |
| Receptionist      | `receptionist@clinic.test`   | `ReceptPass1!`| Creates schedules & generates slots |
| Patient           | `patient@clinic.test`        | `PatientPass1!`| Books & reschedules appointments |

Login endpoint: `POST http://127.0.0.1:8000/accounts/login/` with JSON `{"email","password"}`.

---

## Main flows to test

### 1. Patient books an appointment
1. Log in as the patient → dashboard
2. Pick a doctor + date → view available slots
3. Book a slot → status **Requested**
4. Admin / receptionist confirms → **Confirmed**
5. Patient checks in → **Checked In**
6. Doctor completes → **Completed**

### 2. Receptionist generates slots
1. Log in as the receptionist
2. Create a **Weekly Schedule** (doctor, day, time range)
3. Open **Slot Generator** → choose doctor + date range → **Generate Slots**
4. Creates 15-minute slots with a 5-minute buffer → verify under **Available Slots**

### 3. Patient reschedules
1. Patient → **My Appointments** → **Reschedule** on a Confirmed/Requested appointment
2. Pick a new available slot → submit → the appointment moves

### 4. Admin exports analytics
1. Admin → dashboard → **Export CSV** under Analytics
2. Downloads summary stats (users, appointments by status, rates)

---

## Key API endpoints

| Method | Path | Notes |
|--------|------|-------|
| POST   | `/accounts/login/` | JWT login |
| POST   | `/accounts/register/` | Self-registration (patients, doctors) |
| GET    | `/accounts/admin/pending-doctors/` | Admin: list doctors awaiting approval |
| GET/POST | `/scheduling/weekly-schedule/` | Weekly schedules (admin/receptionist) |
| POST   | `/scheduling/generate-slots/` | Generate time slots |
| GET    | `/scheduling/slots/?doctor=<id>&date=YYYY-MM-DD` | Available slots |
| GET/POST | `/appointments/appointments/` | List / book appointments |
