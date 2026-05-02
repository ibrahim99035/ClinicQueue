# ClinicQueue

A Django + Vue 3 clinic appointment scheduling and queue management system.

---

## Setup

### Backend
```bash
cd server
python -m venv .venv
source .venv/bin/activate 
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

### Frontend
```bash
cd client
nvm use 22
npm install
npm run dev
```
Access at `http://localhost:5173`

---

## Sample Users

All users are created via `/accounts/register/` or `/accounts/admin/create-staff/`.

| Role | Email | Password | Notes |
|------|-------|----------|-------|
| Admin | `admin@clinic.test` | `AdminPass1!` | Created manually; required for first bootstrap |
| Doctor | `testdoctor@clinic.test` | `DoctorPass1!` | Must be approved by admin to log in |
| Receptionist | `testreceptionist@clinic.test` | `ReceptPass1!` | Can create schedules & generate slots |
| Patient | `testpatient@clinic.test` | `PatientPass1!` | Can book appointments & reschedule own |

**To create admin at startup:**
```bash
python manage.py shell <<EOF
from accounts.models.user import User
from django.contrib.auth.models import Group
g, _ = Group.objects.get_or_create(name='Admins')
u = User.create_user(email='eng_noha@clinic.test', password='AdminPass1!', first_name='Eng Noha', last_name='Shehab')
u.groups.add(g)
u.is_staff = True
u.save()
print('Admin created')
EOF
```

---

## Main Flows to Test

### 1. Patient Books Appointment
1. Patient logs in → Dashboard
2. Enter doctor + date → View available slots
3. Book a slot → Appointment in "Requested" status
4. Admin/Reception confirms → Status: "Confirmed"
5. Patient checks in → Status: "Checked In"
6. Doctor completes → Status: "Completed"

### 2. Receptionist Generates Slots
1. Receptionist logs in
2. Create **Weekly Schedule** (doctor, day, time range)
3. Go to **Slot Generator** → Select doctor + date range
4. Click **Generate Slots** → Creates 15-min slots with 5-min buffer
5. Verify in **Available Slots**

### 3. Patient Reschedules
1. Patient views "My Appointments"
2. Click **Reschedule** on a "Confirmed" or "Requested" appointment
3. Select new available slot
4. Submit → Appointment moves to new slot

### 4. Admin Exports Analytics
1. Admin logs in → Dashboard
2. Click **Export CSV** under Analytics
3. Download CSV with summary stats (users, appointments by status, rates)

---

## Tech Stack

- **Backend:** Django 6, Django REST Framework, PostgreSQL
- **Frontend:** Vue 3, Pinia (state), Vue Router, Tailwind CSS
- **Auth:** JWT via djangorestframework-simplejwt
- **Database:** PostgreSQL

---
## Environment would be provided upon submission

```plaintext
DJANGO_SECRET=
DATABASE_URL=
SLOT_BUFFER_MINUTES=5
```