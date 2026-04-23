import requests
import time

BASE_URL = "http://127.0.0.1:8000"
RUN_ID = str(int(time.time()))[-4:]

# ─── credentials ───────────────────────────────
ADMIN        = {"email": "admin@clinic.com",            "password": "adminpass123"}
PATIENT      = {"email": f"patient{RUN_ID}@clinic.com", "password": "patientpass123"}
DOCTOR       = {"email": f"doctor{RUN_ID}@clinic.com",  "password": "doctorpass123"}
RECEPTIONIST = {"email": f"recep{RUN_ID}@clinic.com",   "password": "receppass123"}

# ─── state ─────────────────────────────────────
admin_token      = None
patient_token    = None
doctor_token     = None
doctor_user_id   = None
doctor_profile_pk = None

# ─── helpers ───────────────────────────────────

def _print(method, path, r):
    try:
        body = r.json()
    except Exception:
        body = f"[non-JSON {len(r.text)} chars]"
    print(f"{method} {path} → {r.status_code}: {body}")
    return r

def post(path, data, token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    r = requests.post(f"{BASE_URL}{path}", json=data, headers=headers)
    return _print("POST", path, r)

def get(path, token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    r = requests.get(f"{BASE_URL}{path}", headers=headers)
    return _print("GET ", path, r)

def put(path, data, token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    r = requests.put(f"{BASE_URL}{path}", json=data, headers=headers)
    return _print("PUT ", path, r)

def delete(path, token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    r = requests.delete(f"{BASE_URL}{path}", headers=headers)
    return _print("DEL ", path, r)

def login(email, password):
    r = post("/accounts/login/", {"email": email, "password": password})
    return r.json().get("access") if r.status_code == 200 else None

def section(title):
    print(f"\n{'='*50}\n {title}\n{'='*50}")

def expect(label, condition):
    print(f"  {'✓' if condition else '✗ FAIL'}  {label}")

# ═══════════════════════════════════════════════

section("1. ADMIN LOGIN")
admin_token = login(**ADMIN)
expect("admin gets token", admin_token is not None)

# ───────────────────────────────────────────────

section("2. REGISTER PATIENT")
r = post("/accounts/register/", {
    "email": PATIENT["email"],
    "first_name": "Ahmed", "last_name": "Ali",
    "phone": "01012345678",
    "password": PATIENT["password"],
    "password_confirm": PATIENT["password"],
    "user_role": "patient"
})
expect("patient registered (201)", r.status_code == 201)
expect("patient is active", r.json().get("is_active") is True)
expect("patient_profile created", r.json().get("patient_profile") is not None)
expect("patient role assigned", "Patients" in r.json().get("groups", []))

# ───────────────────────────────────────────────

section("3. REGISTER DOCTOR")
r = post("/accounts/register/", {
    "email": DOCTOR["email"],
    "first_name": "Sara", "last_name": "Hassan",
    "password": DOCTOR["password"],
    "password_confirm": DOCTOR["password"],
    "user_role": "doctor"
})
expect("doctor registered (201)", r.status_code == 201)
expect("doctor is inactive", r.json().get("is_active") is False)
expect("doctor_profile created", r.json().get("doctor_profile") is not None)
expect("doctor role assigned", "Doctors" in r.json().get("groups", []))

# store this run's doctor user id and profile pk for later use
doctor_user_id    = r.json().get("id")
doctor_profile_pk = r.json().get("doctor_profile", {}).get("id")

# ───────────────────────────────────────────────

section("4. DOCTOR CANNOT LOGIN BEFORE APPROVAL")
r = post("/accounts/login/", {"email": DOCTOR["email"], "password": DOCTOR["password"]})
expect("doctor login blocked (401)", r.status_code == 401)

# ───────────────────────────────────────────────

section("5. ADMIN CREATES RECEPTIONIST")
r = post("/accounts/admin/create-internal-user/", {
    "email": RECEPTIONIST["email"],
    "password": RECEPTIONIST["password"],
    "first_name": "Nour", "last_name": "Saad",
    "role": "receptionist"
}, token=admin_token)
expect("receptionist created (201)", r.status_code == 201)
expect("receptionist is active", r.json().get("is_active") is True)
expect("receptionist role assigned", "Receptionists" in r.json().get("groups", []))

# ───────────────────────────────────────────────

section("6. ADMIN CREATES ANOTHER ADMIN")
r = post("/accounts/admin/create-internal-user/", {
    "email": f"admin2{RUN_ID}@clinic.com",
    "password": "adminpass123",
    "first_name": "Second", "last_name": "Admin",
    "role": "admin"
}, token=admin_token)
expect("second admin created (201)", r.status_code == 201)
expect("admin role assigned", "Admins" in r.json().get("groups", []))

# ───────────────────────────────────────────────

section("7. ADMIN LISTS PENDING DOCTORS")
r = get("/accounts/admin/pending-doctors/", token=admin_token)
expect("pending list returned (200)", r.status_code == 200)
pending = r.json()
expect("at least one pending doctor", len(pending) > 0)

# find THIS run's doctor in the pending list by matching stored profile pk
this_run_pending = next((p for p in pending if p["id"] == doctor_profile_pk), None)
expect("this run's doctor is in pending list", this_run_pending is not None)

# ───────────────────────────────────────────────

section("8. ADMIN APPROVES DOCTOR")
if this_run_pending:
    r = post(f"/accounts/admin/approve-doctor/{doctor_profile_pk}/", {}, token=admin_token)
    expect("doctor approved (200)", r.status_code == 200)
    expect("is_approved is True", r.json().get("doctor", {}).get("is_approved") is True)
    expect("approved_by_name set", r.json().get("doctor", {}).get("approved_by_name") is not None)
    expect("approved_at set", r.json().get("doctor", {}).get("approved_at") is not None)

    r2 = post(f"/accounts/admin/approve-doctor/{doctor_profile_pk}/", {}, token=admin_token)
    expect("approving twice returns 400", r2.status_code == 400)
else:
    print("  skipped — this run's doctor not found in pending list")

# ───────────────────────────────────────────────

section("9. DOCTOR CAN LOGIN AFTER APPROVAL")
doctor_token = login(**DOCTOR)
expect("doctor login works after approval", doctor_token is not None)

# ───────────────────────────────────────────────

section("10. DOCTOR PROFILE FLOW")
if doctor_token:
    r = get("/accounts/doctor-profile/", token=doctor_token)
    expect("doctor profile exists (200)", r.status_code == 200)
    expect("is_approved reflected", r.json().get("is_approved") is True)

    r = put("/accounts/doctor-profile/", {
        "specialization": "Cardiology",
        "bio": "10 years experience",
        "consultationDuration": 30
    }, token=doctor_token)
    expect("doctor profile updated (200)", r.status_code == 200)
    expect("specialization saved", r.json().get("specialization") == "Cardiology")
    expect("bio saved", r.json().get("bio") == "10 years experience")
    expect("consultationDuration saved", r.json().get("consultationDuration") == 30)

    r = get("/accounts/doctor-profile/", token=doctor_token)
    expect("updates persisted", r.json().get("specialization") == "Cardiology")
else:
    print("  skipped — doctor login failed")

# ───────────────────────────────────────────────

section("11. PATIENT PROFILE FLOW")
patient_token = login(**PATIENT)
expect("patient login (200)", patient_token is not None)

r = get("/accounts/patient-profile/", token=patient_token)
expect("patient profile exists (200)", r.status_code == 200)

r = put("/accounts/patient-profile/", {
    "dateOfBirth": "1995-06-15",
    "gender": "M"
}, token=patient_token)
expect("patient profile updated (200)", r.status_code == 200)
expect("gender saved", r.json().get("gender") == "M")
expect("dateOfBirth saved", r.json().get("dateOfBirth") == "1995-06-15")

r = get("/accounts/patient-profile/", token=patient_token)
expect("updates persisted", r.json().get("gender") == "M")

# ───────────────────────────────────────────────

section("12. USER PROFILE UPDATE")
r = put("/accounts/profile/", {"first_name": "Ahmed Updated"}, token=patient_token)
expect("profile updated (200)", r.status_code == 200)
expect("first_name changed", r.json().get("first_name") == "Ahmed Updated")

r = get("/accounts/profile/", token=patient_token)
expect("GET profile correct (200)", r.status_code == 200)
expect("change persisted", r.json().get("first_name") == "Ahmed Updated")

r = put("/accounts/profile/", {"email": "hacked@test.com"}, token=patient_token)
expect("email is read-only (ignored)", r.json().get("email") == PATIENT["email"])

# ───────────────────────────────────────────────

section("13. ADMIN USER MANAGEMENT")
r = get("/accounts/users/", token=admin_token)
expect("user list returned (200)", r.status_code == 200)
expect("list is not empty", len(r.json()) > 0)

if doctor_user_id:
    r = get(f"/accounts/users/{doctor_user_id}/", token=admin_token)
    expect("single user retrieved (200)", r.status_code == 200)
    expect("correct user returned", r.json().get("email") == DOCTOR["email"])

# ───────────────────────────────────────────────

section("14. SECURITY CHECKS")
r = get("/accounts/users/")
expect("no token → 401", r.status_code == 401)

r = get("/accounts/users/", token=patient_token)
expect("patient cannot list users → 403", r.status_code == 403)

r = post("/accounts/admin/create-internal-user/", {"email": "x@x.com"}, token=patient_token)
expect("patient cannot create internal user → 403", r.status_code == 403)

if doctor_token:
    r = post("/accounts/admin/create-internal-user/", {"email": "x@x.com"}, token=doctor_token)
    expect("doctor cannot create internal user → 403", r.status_code == 403)

r = get("/accounts/admin/pending-doctors/", token=patient_token)
expect("patient cannot see pending doctors → 403", r.status_code == 403)

if patient_token and doctor_profile_pk:
    r = post(f"/accounts/admin/approve-doctor/{doctor_profile_pk}/", {}, token=patient_token)
    expect("patient cannot approve doctor → 403", r.status_code == 403)

# ───────────────────────────────────────────────

section("15. DUPLICATE & BAD REGISTRATION")
r = post("/accounts/register/", {
    "email": PATIENT["email"],
    "first_name": "X", "last_name": "Y",
    "password": "pass12345", "password_confirm": "pass12345",
    "user_role": "patient"
})
expect("duplicate email rejected (400)", r.status_code == 400)

r = post("/accounts/register/", {
    "email": f"bad{RUN_ID}@test.com",
    "first_name": "X", "last_name": "Y",
    "password": "pass12345", "password_confirm": "wrong",
    "user_role": "patient"
})
expect("password mismatch rejected (400)", r.status_code == 400)

r = post("/accounts/register/", {
    "email": f"bad2{RUN_ID}@test.com",
    "first_name": "X", "last_name": "Y",
    "password": "pass12345", "password_confirm": "pass12345",
    "user_role": "receptionist"
})
expect("invalid role rejected (400)", r.status_code == 400)

r = post("/accounts/register/", {
    "first_name": "X", "last_name": "Y",
    "password": "pass12345", "password_confirm": "pass12345",
    "user_role": "patient"
})
expect("missing email rejected (400)", r.status_code == 400)

# ───────────────────────────────────────────────

section("16. TOKEN REFRESH")
r = post("/accounts/login/", {"email": PATIENT["email"], "password": PATIENT["password"]})
refresh_token = r.json().get("refresh")
r = post("/accounts/token/refresh/", {"refresh": refresh_token})
expect("token refresh works (200)", r.status_code == 200)
expect("new access token returned", r.json().get("access") is not None)

# ───────────────────────────────────────────────

print(f"\n{'='*50}\n Done\n{'='*50}\n")