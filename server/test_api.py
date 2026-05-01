#!/usr/bin/env python3
"""
Clinic API End-to-End Test Suite
Hits every endpoint, logs every request/response, and prints a summary report.

Usage:
    python test_api.py
    python test_api.py --base-url http://localhost:8000
    python test_api.py --base-url http://localhost:8000 --log clinic_test.log
"""

import argparse
import json
import sys
import time
import traceback
from datetime import date, timedelta
from typing import Any, Optional

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library not found. Run: pip install requests")
    sys.exit(1)

# ---------------------------------------------------------------------------
# CLI args
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="Clinic API end-to-end test suite")
parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
parser.add_argument("--log", default="api_test_results.log", help="Log file path")
args = parser.parse_args()

BASE_URL = args.base_url.rstrip("/")
LOG_FILE = args.log

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------
log_lines: list[str] = []

def log(msg: str = "") -> None:
    print(msg)
    log_lines.append(msg)

def log_section(title: str) -> None:
    bar = "=" * 70
    log(f"\n{bar}")
    log(f"  {title}")
    log(bar)

def log_sub(title: str) -> None:
    log(f"\n--- {title} ---")

# ---------------------------------------------------------------------------
# Result tracking
# ---------------------------------------------------------------------------
results: list[dict] = []

def record(
    name: str,
    passed: bool,
    status_code: Optional[int],
    expected: Any,
    note: str = "",
) -> None:
    results.append(
        {
            "name": name,
            "passed": passed,
            "status_code": status_code,
            "expected": expected,
            "note": note,
        }
    )
    icon = "✓ PASS" if passed else "✗ FAIL"
    sc   = f"[HTTP {status_code}]" if status_code is not None else "[NO RESPONSE]"
    log(f"  {icon}  {sc}  {name}")
    if note:
        log(f"         ↳ {note}")

# ---------------------------------------------------------------------------
# HTTP wrapper — logs every call in detail
# ---------------------------------------------------------------------------
class Client:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers["Content-Type"] = "application/json"
        self._token: Optional[str] = None

    def set_token(self, token: Optional[str]) -> None:
        self._token = token
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        else:
            self.session.headers.pop("Authorization", None)

    def _call(
        self,
        method: str,
        path: str,
        expected_status: int,
        test_name: str,
        body: Optional[dict] = None,
        params: Optional[dict] = None,
        note_on_fail: str = "",
    ) -> Optional[dict]:
        url = f"{BASE_URL}{path}"
        log(f"\n  ► {method} {path}")
        if body:
            log(f"    Body    : {json.dumps(body)}")
        if params:
            log(f"    Params  : {params}")

        response = None
        data = None
        try:
            response = self.session.request(
                method,
                url,
                json=body,
                params=params,
                timeout=15,
            )
            try:
                data = response.json()
            except Exception:
                data = {"_raw": response.text}

            log(f"    Status  : {response.status_code}")
            log(f"    Response: {json.dumps(data, default=str)[:800]}")

            passed = response.status_code == expected_status
            record(
                test_name,
                passed,
                response.status_code,
                expected_status,
                note_on_fail if not passed else "",
            )
            return data if passed else None

        except requests.exceptions.ConnectionError:
            msg = f"Cannot connect to {BASE_URL} — is the server running?"
            log(f"    ERROR: {msg}")
            record(test_name, False, None, expected_status, msg)
            return None

        except Exception:
            tb = traceback.format_exc()
            log(f"    ERROR:\n{tb}")
            sc = response.status_code if response else None
            record(test_name, False, sc, expected_status, str(tb).split("\n")[-2])
            return None

    # Convenience shorthands
    def get(self, path, test_name, *, expected=200, params=None, note=""):
        return self._call("GET", path, expected, test_name, params=params, note_on_fail=note)

    def post(self, path, body, test_name, *, expected=201, note=""):
        return self._call("POST", path, expected, test_name, body=body, note_on_fail=note)

    def put(self, path, body, test_name, *, expected=200, note=""):
        return self._call("PUT", path, expected, test_name, body=body, note_on_fail=note)

    def delete(self, path, test_name, *, expected=204, note=""):
        return self._call("DELETE", path, expected, test_name, note_on_fail=note)


c = Client()

# ---------------------------------------------------------------------------
# Shared state — filled in as tests run
# ---------------------------------------------------------------------------
state: dict[str, Any] = {}

# Dates: pick a future Monday and the days that follow
def next_weekday(weekday: int) -> date:
    """Return the next occurrence of weekday (0=Mon). Always in the future."""
    today = date.today()
    days_ahead = (weekday - today.weekday() + 7) % 7 or 7
    return today + timedelta(days=days_ahead)

MONDAY   = next_weekday(0)
TUESDAY  = MONDAY + timedelta(days=1)
THURSDAY = MONDAY + timedelta(days=3)

# ---------------------------------------------------------------------------
# TEST SUITE
# ---------------------------------------------------------------------------

log_section("CLINIC API END-TO-END TEST SUITE")
log(f"  Base URL : {BASE_URL}")
log(f"  Log file : {LOG_FILE}")
log(f"  Run at   : {time.strftime('%Y-%m-%d %H:%M:%S')}")
log(f"  Mon date : {MONDAY}  (slot generation target)")


# ============================================================
# 1. ACCOUNTS — REGISTRATION
# ============================================================
log_section("1. ACCOUNTS — REGISTRATION")

log_sub("1.1 Register patient")
patient_payload = {
    "email": "testpatient@clinic.test",
    "first_name": "Mona",
    "last_name": "Samir",
    "phone": "01011112222",
    "password": "PatientPass1!",
    "password_confirm": "PatientPass1!",
    "user_role": "patient",
}
r = c.post("/accounts/register/", patient_payload, "Register patient (201)")

log_sub("1.2 Register doctor")
doctor_payload = {
    "email": "testdoctor@clinic.test",
    "first_name": "Khaled",
    "last_name": "Hassan",
    "phone": "01033334444",
    "password": "DoctorPass1!",
    "password_confirm": "DoctorPass1!",
    "user_role": "doctor",
}
r = c.post("/accounts/register/", doctor_payload, "Register doctor (201)")

log_sub("1.3 Duplicate email rejected")
c.post(
    "/accounts/register/",
    patient_payload,
    "Duplicate email → 400",
    expected=400,
    note="email already exists",
)

log_sub("1.4 Password mismatch rejected")
bad = {**patient_payload, "email": "other@clinic.test", "password_confirm": "WrongPass!"}
c.post("/accounts/register/", bad, "Password mismatch → 400", expected=400)

log_sub("1.5 Invalid user_role rejected")
bad2 = {**patient_payload, "email": "bad@clinic.test", "user_role": "superadmin"}
c.post("/accounts/register/", bad2, "Invalid user_role → 400", expected=400)

log_sub("1.6 Doctor cannot log in before approval")
c._call(
    "POST",
    "/accounts/login/",
    401,
    "Doctor login before approval → 401",
    body={"email": "testdoctor@clinic.test", "password": "DoctorPass1!"},
)


# ============================================================
# 2. ACCOUNTS — LOGIN & TOKEN
# ============================================================
log_section("2. ACCOUNTS — LOGIN & TOKENS")

log_sub("2.1 Patient login")
r = c._call(
    "POST",
    "/accounts/login/",
    200,
    "Patient login (200)",
    body={"email": "testpatient@clinic.test", "password": "PatientPass1!"},
)
if r:
    state["patient_token"]   = r.get("access")
    state["patient_refresh"] = r.get("refresh")

log_sub("2.2 Wrong password rejected")
c._call(
    "POST",
    "/accounts/login/",
    401,
    "Wrong password → 401",
    body={"email": "testpatient@clinic.test", "password": "WrongPass!"},
)

log_sub("2.3 Token refresh")
if state.get("patient_refresh"):
    c._call(
        "POST",
        "/accounts/token/refresh/",
        200,
        "Token refresh (200)",
        body={"refresh": state["patient_refresh"]},
    )
else:
    record("Token refresh (200)", False, None, 200, "No refresh token — patient login failed")


# ============================================================
# 3. ADMIN BOOTSTRAP (shell-created admin)
# ============================================================
log_section("3. ADMIN BOOTSTRAP")
log("""
  NOTE: An admin account must exist before this script can proceed.
  If you haven't created one yet, run:

      python manage.py shell -c "
      from accounts.models.user import User
      from django.contrib.auth.models import Group
      g = Group.objects.get(name='Admins')
      u = User.create_user(email='admin@clinic.test', password='AdminPass1!',
                           first_name='Admin', last_name='User')
      u.groups.add(g); u.is_staff=True; u.save()
      print('Admin created.')
      "

  Then re-run this script.
""")

log_sub("3.1 Admin login")
r = c._call(
    "POST",
    "/accounts/login/",
    200,
    "Admin login (200)",
    body={"email": "admin@clinic.test", "password": "AdminPass1!"},
)
if r:
    state["admin_token"] = r.get("access")

if not state.get("admin_token"):
    log("\n  CRITICAL: Admin login failed. Many tests below will be skipped.")
    log("  Create the admin account using the command above, then re-run.\n")


# ============================================================
# 4. ADMIN — USER MANAGEMENT
# ============================================================
log_section("4. ADMIN — USER MANAGEMENT")

log_sub("4.1 List users (admin)")
c.set_token(state.get("admin_token"))
r = c.get("/accounts/users/", "List users — admin (200)")
if r and "results" in r:
    for u_item in r["results"]:
        email = u_item.get("email", "")
        if email == "testdoctor@clinic.test":
            state["doctor_user_id"] = u_item.get("id")
        if email == "testpatient@clinic.test":
            state["patient_user_id"] = u_item.get("id")

log_sub("4.2 List users — patient forbidden")
c.set_token(state.get("patient_token"))
c.get("/accounts/users/", "List users — patient → 403", expected=403)

log_sub("4.3 Retrieve single user (admin)")
c.set_token(state.get("admin_token"))
if state.get("patient_user_id"):
    c.get(f"/accounts/users/{state['patient_user_id']}/", "Retrieve user by ID (200)")
else:
    record("Retrieve user by ID (200)", False, None, 200, "patient_user_id not found")

log_sub("4.4 Create receptionist via admin endpoint")
c.set_token(state.get("admin_token"))
r = c.post(
    "/accounts/admin/create-staff/",
    {
        "email": "testreceptionist@clinic.test",
        "password": "ReceptPass1!",
        "first_name": "Sara",
        "last_name": "Ali",
        "phone": "01055556666",
        "role": "receptionist",
    },
    "Create receptionist (201)",
)

log_sub("4.5 create-staff with invalid role rejected")
c.post(
    "/accounts/admin/create-staff/",
    {
        "email": "bad_role@clinic.test",
        "password": "Pass1234!",
        "first_name": "X",
        "last_name": "Y",
        "role": "superadmin",
    },
    "create-staff bad role → 400",
    expected=400,
)

log_sub("4.6 Receptionist login")
r = c._call(
    "POST",
    "/accounts/login/",
    200,
    "Receptionist login (200)",
    body={"email": "testreceptionist@clinic.test", "password": "ReceptPass1!"},
)
if r:
    state["reception_token"] = r.get("access")


# ============================================================
# 5. PENDING DOCTORS & APPROVAL
# ============================================================
log_section("5. PENDING DOCTORS & APPROVAL")

log_sub("5.1 List pending doctors")
c.set_token(state.get("admin_token"))
r = c.get("/accounts/admin/pending-doctors/", "List pending doctors (200)")
if r and isinstance(r, list) and r:
    state["doctor_profile_id"] = r[0].get("id")
    log(f"    Doctor profile ID: {state['doctor_profile_id']}")

log_sub("5.2 Non-admin blocked from pending-doctors")
c.set_token(state.get("patient_token"))
c.get("/accounts/admin/pending-doctors/", "Pending doctors — patient → 403", expected=403)

log_sub("5.3 Approve doctor")
c.set_token(state.get("admin_token"))
if state.get("doctor_profile_id"):
    r = c.post(
        f"/accounts/admin/approve-doctor/{state['doctor_profile_id']}/",
        {},
        "Approve doctor (200)",
        expected=200,
    )
    log_sub("5.4 Approve same doctor again — already approved")
    c.post(
        f"/accounts/admin/approve-doctor/{state['doctor_profile_id']}/",
        {},
        "Re-approve doctor → 400",
        expected=400,
    )
else:
    record("Approve doctor (200)", False, None, 200, "doctor_profile_id not found")
    record("Re-approve doctor → 400", False, None, 400, "doctor_profile_id not found")

log_sub("5.5 Doctor login after approval")
r = c._call(
    "POST",
    "/accounts/login/",
    200,
    "Doctor login after approval (200)",
    body={"email": "testdoctor@clinic.test", "password": "DoctorPass1!"},
)
if r:
    state["doctor_token"] = r.get("access")


# ============================================================
# 6. PROFILES
# ============================================================
log_section("6. PROFILES")

log_sub("6.1 Get own profile (patient)")
c.set_token(state.get("patient_token"))
c.get("/accounts/profile/", "Get profile — patient (200)")

log_sub("6.2 Update own profile (patient)")
c.put(
    "/accounts/profile/",
    {"first_name": "Mona Updated", "phone": "01099999999"},
    "Update profile — patient (200)",
)

log_sub("6.3 Get patient profile")
c.get("/accounts/patient-profile/", "Get patient profile (200)")

log_sub("6.4 Update patient profile")
c.put(
    "/accounts/patient-profile/",
    {"dateOfBirth": "1995-04-12", "gender": "F"},
    "Update patient profile (200)",
)

log_sub("6.5 Get doctor profile")
c.set_token(state.get("doctor_token"))
r = c.get("/accounts/doctor-profile/", "Get doctor profile (200)")

log_sub("6.6 Update doctor profile")
r = c.put(
    "/accounts/doctor-profile/",
    {"specialization": "Cardiology", "consultationDuration": 15, "bio": "Expert cardiologist."},
    "Update doctor profile (200)",
)
if r and "user" in r:
    state["doctor_profile_id_from_profile"] = r.get("id")


# ============================================================
# 7. SCHEDULING — WEEKLY SCHEDULE
# ============================================================
log_section("7. SCHEDULING — WEEKLY SCHEDULE")

# Get doctor profile id if not already set
if not state.get("doctor_profile_id"):
    c.set_token(state.get("doctor_token"))
    r = c.get("/accounts/doctor-profile/", "Fetch doctor profile for scheduling (200)")
    if r:
        state["doctor_profile_id"] = r.get("id")

log_sub("7.1 Create weekly schedule — Monday (receptionist)")
c.set_token(state.get("reception_token"))
r = c.post(
    "/scheduling/weekly-schedule/",
    {
        "doctor": state.get("doctor_profile_id"),
        "day_of_week": 0,
        "start_time": "09:00:00",
        "end_time": "13:00:00",
        "is_active": True,
    },
    "Create weekly schedule Mon (201)",
)
if r:
    state["weekly_schedule_id"] = r.get("id")

log_sub("7.2 Create weekly schedule — Tuesday")
c.post(
    "/scheduling/weekly-schedule/",
    {
        "doctor": state.get("doctor_profile_id"),
        "day_of_week": 1,
        "start_time": "14:00:00",
        "end_time": "18:00:00",
        "is_active": True,
    },
    "Create weekly schedule Tue (201)",
)

log_sub("7.3 Duplicate day rejected")
c.post(
    "/scheduling/weekly-schedule/",
    {
        "doctor": state.get("doctor_profile_id"),
        "day_of_week": 0,
        "start_time": "10:00:00",
        "end_time": "12:00:00",
        "is_active": True,
    },
    "Duplicate weekly schedule day → 400",
    expected=400,
)

log_sub("7.4 List weekly schedule (doctor sees own)")
c.set_token(state.get("doctor_token"))
c.get("/scheduling/weekly-schedule/", "List weekly schedule — doctor (200)")

log_sub("7.5 List weekly schedule (receptionist sees all)")
c.set_token(state.get("reception_token"))
c.get("/scheduling/weekly-schedule/", "List weekly schedule — receptionist (200)")

log_sub("7.6 Patient cannot create weekly schedule")
c.set_token(state.get("patient_token"))
c.post(
    "/scheduling/weekly-schedule/",
    {"doctor": state.get("doctor_profile_id"), "day_of_week": 2, "start_time": "09:00:00", "end_time": "12:00:00"},
    "Create weekly schedule — patient → 403",
    expected=403,
)

log_sub("7.7 Update weekly schedule")
c.set_token(state.get("reception_token"))
if state.get("weekly_schedule_id"):
    c.put(
        f"/scheduling/weekly-schedule/{state['weekly_schedule_id']}/",
        {
            "doctor": state.get("doctor_profile_id"),
            "day_of_week": 0,
            "start_time": "08:00:00",
            "end_time": "12:00:00",
            "is_active": True,
        },
        "Update weekly schedule (200)",
    )

log_sub("7.8 Delete weekly schedule")
# Create a throwaway one to delete
r = c.post(
    "/scheduling/weekly-schedule/",
    {"doctor": state.get("doctor_profile_id"), "day_of_week": 6, "start_time": "10:00:00", "end_time": "12:00:00"},
    "Create throwaway schedule for delete (201)",
)
if r:
    c.delete(f"/scheduling/weekly-schedule/{r['id']}/", "Delete weekly schedule (204)")


# ============================================================
# 8. SCHEDULING — EXCEPTIONS
# ============================================================
log_section("8. SCHEDULING — EXCEPTIONS")

log_sub("8.1 Create DAY_OFF exception (Thursday)")
c.set_token(state.get("reception_token"))
r = c.post(
    "/scheduling/exceptions/",
    {
        "doctor": state.get("doctor_profile_id"),
        "exception_date": str(THURSDAY),
        "type": "DAY_OFF",
        "note": "Doctor unavailable",
    },
    "Create DAY_OFF exception (201)",
)
if r:
    state["day_off_exception_id"] = r.get("id")

log_sub("8.2 Create EXTRA_WORKING exception")
extra_date = MONDAY + timedelta(days=14)
r = c.post(
    "/scheduling/exceptions/",
    {
        "doctor": state.get("doctor_profile_id"),
        "exception_date": str(extra_date),
        "type": "EXTRA_WORKING",
        "start_time": "07:00:00",
        "end_time": "09:00:00",
    },
    "Create EXTRA_WORKING exception (201)",
)
if r:
    state["extra_working_exception_id"] = r.get("id")

log_sub("8.3 DAY_OFF with times provided → 400")
c.post(
    "/scheduling/exceptions/",
    {
        "doctor": state.get("doctor_profile_id"),
        "exception_date": str(MONDAY + timedelta(days=21)),
        "type": "DAY_OFF",
        "start_time": "09:00:00",
        "end_time": "12:00:00",
    },
    "DAY_OFF with times → 400",
    expected=400,
)

log_sub("8.4 EXTRA_WORKING missing times → 400")
c.post(
    "/scheduling/exceptions/",
    {
        "doctor": state.get("doctor_profile_id"),
        "exception_date": str(MONDAY + timedelta(days=28)),
        "type": "EXTRA_WORKING",
    },
    "EXTRA_WORKING missing times → 400",
    expected=400,
)

log_sub("8.5 Past date rejected")
c.post(
    "/scheduling/exceptions/",
    {
        "doctor": state.get("doctor_profile_id"),
        "exception_date": "2020-01-01",
        "type": "DAY_OFF",
    },
    "Past exception date → 400",
    expected=400,
)

log_sub("8.6 List exceptions (doctor sees own)")
c.set_token(state.get("doctor_token"))
c.get("/scheduling/exceptions/", "List exceptions — doctor (200)")

log_sub("8.7 Delete EXTRA_WORKING exception")
c.set_token(state.get("reception_token"))
if state.get("extra_working_exception_id"):
    c.delete(f"/scheduling/exceptions/{state['extra_working_exception_id']}/", "Delete exception (204)")


# ============================================================
# 9. SCHEDULING — SLOT GENERATION & RETRIEVAL
# ============================================================
log_section("9. SCHEDULING — SLOT GENERATION & RETRIEVAL")

log_sub("9.1 Generate slots for Monday")
c.set_token(state.get("reception_token"))
r = c.post(
    "/scheduling/generate-slots/",
    {
        "doctor": state.get("doctor_profile_id"),
        "start_date": str(MONDAY),
        "end_date": str(TUESDAY),
    },
    "Generate slots Mon–Tue (201)",
)
if r:
    log(f"    Slots generated: {r.get('count')}")

log_sub("9.2 Range > 90 days rejected")
c.post(
    "/scheduling/generate-slots/",
    {
        "doctor": state.get("doctor_profile_id"),
        "start_date": str(MONDAY),
        "end_date": str(MONDAY + timedelta(days=100)),
    },
    "Generate slots > 90 days → 400",
    expected=400,
)

log_sub("9.3 Missing fields rejected")
c.post(
    "/scheduling/generate-slots/",
    {"doctor": state.get("doctor_profile_id")},
    "Generate slots missing dates → 400",
    expected=400,
)

log_sub("9.4 Patient cannot generate slots")
c.set_token(state.get("patient_token"))
c.post(
    "/scheduling/generate-slots/",
    {"doctor": state.get("doctor_profile_id"), "start_date": str(MONDAY), "end_date": str(MONDAY)},
    "Generate slots — patient → 403",
    expected=403,
)

log_sub("9.5 Retrieve available slots for Monday")
c.set_token(state.get("patient_token"))
r = c.get(
    "/scheduling/slots/",
    "Get available slots Mon (200)",
    params={"doctor": state.get("doctor_profile_id"), "date": str(MONDAY)},
)
if r and isinstance(r, list) and r:
    state["slot_id_1"] = r[0]["id"]
    state["slot_id_2"] = r[1]["id"] if len(r) > 1 else None
    state["slot_id_3"] = r[2]["id"] if len(r) > 2 else None
    log(f"    First slot ID: {state['slot_id_1']}  Second: {state['slot_id_2']}")

log_sub("9.6 No slots on DAY_OFF date (Thursday)")
r = c.get(
    "/scheduling/slots/",
    "No slots on DAY_OFF date (200 empty list)",
    params={"doctor": state.get("doctor_profile_id"), "date": str(THURSDAY)},
)
if r is not None:
    if isinstance(r, list) and len(r) == 0:
        record("DAY_OFF date returns empty list", True, 200, 200, "")
    else:
        record("DAY_OFF date returns empty list", False, 200, 200,
               f"Expected empty list, got {len(r) if isinstance(r, list) else '?'} items")

log_sub("9.7 Missing query params rejected")
c.get(
    "/scheduling/slots/",
    "Get slots missing params → 400",
    expected=400,
    params={"doctor": state.get("doctor_profile_id")},
)


# ============================================================
# 10. APPOINTMENTS — BOOKING
# ============================================================
log_section("10. APPOINTMENTS — BOOKING")

log_sub("10.1 Patient books appointment")
c.set_token(state.get("patient_token"))
if state.get("slot_id_1") and state.get("doctor_profile_id"):
    r = c.post(
        "/appointments/appointments/",
        {
            "slot_id": state["slot_id_1"],
            "doctor_id": state["doctor_profile_id"],
            "reason": "Chest pain and shortness of breath",
        },
        "Book appointment (201)",
    )
    if r:
        state["appointment_id"] = r.get("id")
        log(f"    Appointment ID: {state['appointment_id']}")
else:
    record("Book appointment (201)", False, None, 201, "slot_id_1 or doctor_profile_id missing")

log_sub("10.2 Book same slot again → 400")
if state.get("slot_id_1") and state.get("doctor_profile_id"):
    c.post(
        "/appointments/appointments/",
        {"slot_id": state["slot_id_1"], "doctor_id": state["doctor_profile_id"], "reason": "Dup"},
        "Duplicate slot booking → 400",
        expected=400,
    )

log_sub("10.3 Doctor cannot book")
c.set_token(state.get("doctor_token"))
if state.get("slot_id_2"):
    c.post(
        "/appointments/appointments/",
        {"slot_id": state["slot_id_2"], "doctor_id": state["doctor_profile_id"], "reason": "Test"},
        "Doctor books appointment → 403",
        expected=403,
    )

log_sub("10.4 List appointments (patient sees own)")
c.set_token(state.get("patient_token"))
c.get("/appointments/appointments/", "List appointments — patient (200)")

log_sub("10.5 List appointments (doctor sees own)")
c.set_token(state.get("doctor_token"))
c.get("/appointments/appointments/", "List appointments — doctor (200)")

log_sub("10.6 List appointments (receptionist sees all)")
c.set_token(state.get("reception_token"))
c.get("/appointments/appointments/", "List appointments — receptionist (200)")


# ============================================================
# 11. APPOINTMENT LIFECYCLE — TRANSITIONS
# ============================================================
log_section("11. APPOINTMENT LIFECYCLE — TRANSITIONS")
appt_id = state.get("appointment_id")

if not appt_id:
    log("  SKIP: No appointment ID available — booking step failed.")
else:
    log_sub("11.1 Patient cannot confirm")
    c.set_token(state.get("patient_token"))
    c.post(f"/appointments/appointments/{appt_id}/confirm/", {}, "Patient confirm → 403", expected=403)

    log_sub("11.2 Doctor confirms appointment (REQUESTED → CONFIRMED)")
    c.set_token(state.get("doctor_token"))
    r = c.post(f"/appointments/appointments/{appt_id}/confirm/", {}, "Confirm appointment (200)", expected=200)
    if r:
        assert r.get("status") == "CONFIRMED", "Status should be CONFIRMED"
        assert r.get("confirmed_at") is not None, "confirmed_at should be set"

    log_sub("11.3 Confirm again → 400")
    c.post(f"/appointments/appointments/{appt_id}/confirm/", {}, "Re-confirm → 400", expected=400)

    log_sub("11.4 Book a second slot for reschedule test")
    c.set_token(state.get("patient_token"))
    if state.get("slot_id_2"):
        r2 = c.post(
            "/appointments/appointments/",
            {"slot_id": state["slot_id_2"], "doctor_id": state["doctor_profile_id"], "reason": "Follow-up"},
            "Book second appointment for reschedule (201)",
        )
        if r2:
            state["appointment_id_2"] = r2.get("id")

    log_sub("11.5 Reschedule appointment")
    if state.get("slot_id_3"):
        r = c.post(
            f"/appointments/appointments/{appt_id}/reschedule/",
            {"new_slot": state["slot_id_3"], "reason": "Patient requested afternoon"},
            "Reschedule appointment (200)",
            expected=200,
        )
    else:
        log("    SKIP: slot_id_3 not available")

    log_sub("11.6 Get reschedule history")
    r = c.get(
        f"/appointments/appointments/{appt_id}/history/",
        "Reschedule history (200)",
    )
    if r is not None:
        if isinstance(r, list) and len(r) >= 1:
            record("Reschedule history contains entry", True, 200, 200)
        else:
            record("Reschedule history contains entry", False, 200, 200, f"Got: {r}")

    log_sub("11.7 Patient cannot check_in")
    c.set_token(state.get("patient_token"))
    c.post(f"/appointments/appointments/{appt_id}/check_in/", {}, "Patient check_in → 403", expected=403)

    log_sub("11.8 Receptionist checks in (CONFIRMED → CHECKED_IN)")
    c.set_token(state.get("reception_token"))
    r = c.post(f"/appointments/appointments/{appt_id}/check_in/", {}, "Check in appointment (200)", expected=200)
    if r:
        assert r.get("status") == "CHECKED_IN", "Status should be CHECKED_IN"
        assert r.get("checked_in_at") is not None, "checked_in_at should be set"

    log_sub("11.9 View queue (receptionist)")
    c.get("/appointments/appointments/queue/", "View queue — receptionist (200)")

    log_sub("11.10 View queue (doctor)")
    c.set_token(state.get("doctor_token"))
    c.get("/appointments/appointments/queue/", "View queue — doctor (200)")

    log_sub("11.11 Complete without consultation → 400")
    c.set_token(state.get("doctor_token"))
    c.post(f"/appointments/appointments/{appt_id}/complete/", {}, "Complete without consult → 400", expected=400)


# ============================================================
# 12. EMR — CONSULTATION RECORDS
# ============================================================
log_section("12. EMR — CONSULTATION RECORDS")
appt_id = state.get("appointment_id")

if not appt_id:
    log("  SKIP: No appointment ID available.")
else:
    log_sub("12.1 Patient cannot create consultation")
    c.set_token(state.get("patient_token"))
    c.post(
        "/emr/consultations/",
        {"appointment_id": appt_id, "diagnosis": "Test", "notes": "Test"},
        "Patient creates consult → 403",
        expected=403,
    )

    log_sub("12.2 Doctor creates consultation")
    c.set_token(state.get("doctor_token"))
    r = c.post(
        "/emr/consultations/",
        {
            "appointment_id": appt_id,
            "diagnosis": "Stable angina",
            "notes": "Patient reports exertional chest pain. ECG ordered.",
            "prescription_items": [
                {"drug_name": "Aspirin", "dose": "100mg", "duration": "Indefinite"},
                {"drug_name": "Metoprolol", "dose": "25mg", "duration": "90 days"},
            ],
            "requested_tests": [
                {"test_name": "ECG", "notes": "Baseline reading"},
                {"test_name": "Lipid panel", "notes": None},
            ],
        },
        "Create consultation (201)",
    )
    if r:
        state["consultation_id"] = r.get("id")
        log(f"    Consultation ID: {state['consultation_id']}")

    log_sub("12.3 Duplicate consultation → 400")
    c.post(
        "/emr/consultations/",
        {"appointment_id": appt_id, "diagnosis": "Dup", "notes": "Dup"},
        "Duplicate consultation → 400",
        expected=400,
    )

    log_sub("12.4 Empty diagnosis rejected")
    c.post(
        "/emr/consultations/",
        {"appointment_id": appt_id + 999, "diagnosis": "  ", "notes": "Test"},
        "Empty diagnosis → 400",
        expected=400,
    )

    log_sub("12.5 Doctor completes appointment (CHECKED_IN → COMPLETED)")
    c.set_token(state.get("doctor_token"))
    r = c.post(
        f"/appointments/appointments/{appt_id}/complete/",
        {},
        "Complete appointment (200)",
        expected=200,
    )
    if r:
        assert r.get("status") == "COMPLETED", "Status should be COMPLETED"
        assert r.get("completed_at") is not None, "completed_at should be set"

    log_sub("12.6 Get consultation by appointment ID (doctor)")
    c.set_token(state.get("doctor_token"))
    c.get(f"/emr/consultations/by-appointment/{appt_id}/", "Get consult by appt — doctor (200)")

    log_sub("12.7 Get consultation by appointment ID (patient)")
    c.set_token(state.get("patient_token"))
    c.get(f"/emr/consultations/by-appointment/{appt_id}/", "Get consult by appt — patient (200)")

    log_sub("12.8 Receptionist blocked from consultation")
    c.set_token(state.get("reception_token"))
    c.get(
        f"/emr/consultations/by-appointment/{appt_id}/",
        "Get consult — receptionist → 403",
        expected=403,
    )

    log_sub("12.9 Get consultation by ID (doctor)")
    c.set_token(state.get("doctor_token"))
    if state.get("consultation_id"):
        c.get(f"/emr/consultations/{state['consultation_id']}/", "Get consult by ID — doctor (200)")

    log_sub("12.10 Update consultation (doctor)")
    if state.get("consultation_id"):
        c.put(
            f"/emr/consultations/{state['consultation_id']}/",
            {
                "diagnosis": "Stable angina — controlled",
                "notes": "Follow-up in 4 weeks. Responding well to medication.",
                "prescription_items": [
                    {"drug_name": "Aspirin", "dose": "100mg", "duration": "Indefinite"},
                ],
                "requested_tests": [],
            },
            "Update consultation (200)",
        )

    log_sub("12.11 Patient cannot update consultation")
    c.set_token(state.get("patient_token"))
    if state.get("consultation_id"):
        c.put(
            f"/emr/consultations/{state['consultation_id']}/",
            {"diagnosis": "Hacked"},
            "Patient updates consult → 403",
            expected=403,
        )


# ============================================================
# 13. APPOINTMENT — CANCEL & NO_SHOW
# ============================================================
log_section("13. APPOINTMENT — CANCEL & NO_SHOW")

# Use second appointment for cancel/no_show tests (still in REQUESTED state)
appt2 = state.get("appointment_id_2")
if not appt2:
    log("  SKIP: appointment_id_2 not available.")
else:
    log_sub("13.1 Confirm second appointment")
    c.set_token(state.get("doctor_token"))
    c.post(f"/appointments/appointments/{appt2}/confirm/", {}, "Confirm 2nd appt (200)", expected=200)

    log_sub("13.2 Mark no_show (CONFIRMED → NO_SHOW)")
    c.post(f"/appointments/appointments/{appt2}/no_show/", {}, "No-show appointment (200)", expected=200)

    log_sub("13.3 Book another appointment then cancel it")
    c.set_token(state.get("patient_token"))
    # Get a fresh slot (slot_id_2 was freed by no_show freeing slot_id_2)
    r_slots = c.get(
        "/scheduling/slots/",
        "Get fresh slots for cancel test (200)",
        params={"doctor": state.get("doctor_profile_id"), "date": str(MONDAY)},
    )
    if r_slots and isinstance(r_slots, list) and r_slots:
        fresh_slot = r_slots[0]["id"]
        r3 = c.post(
            "/appointments/appointments/",
            {"slot_id": fresh_slot, "doctor_id": state["doctor_profile_id"], "reason": "Cancel test"},
            "Book appointment for cancel test (201)",
        )
        if r3:
            appt3_id = r3.get("id")
            log_sub("13.4 Patient cancels own appointment (REQUESTED → CANCELLED)")
            c.post(f"/appointments/appointments/{appt3_id}/cancel/", {}, "Cancel appointment (200)", expected=200)


# ============================================================
# 14. WAITING LIST
# ============================================================
log_section("14. WAITING LIST")

log_sub("14.1 Patient joins waiting list")
c.set_token(state.get("patient_token"))
r = c.post(
    "/appointments/waiting-list/",
    {"doctor_id": state.get("doctor_profile_id"), "preferred_date": str(THURSDAY)},
    "Join waiting list (201)",
)
if r:
    state["waiting_list_id"] = r.get("id")

log_sub("14.2 Duplicate waiting list entry → 400")
c.post(
    "/appointments/waiting-list/",
    {"doctor_id": state.get("doctor_profile_id"), "preferred_date": str(THURSDAY)},
    "Duplicate waiting list → 400",
    expected=400,
)

log_sub("14.3 List waiting list (patient)")
c.get("/appointments/waiting-list/", "List waiting list — patient (200)")

log_sub("14.4 List waiting list (receptionist sees all)")
c.set_token(state.get("reception_token"))
c.get("/appointments/waiting-list/", "List waiting list — receptionist (200)")

log_sub("14.5 Doctor cannot join waiting list")
c.set_token(state.get("doctor_token"))
c.post(
    "/appointments/waiting-list/",
    {"doctor_id": state.get("doctor_profile_id"), "preferred_date": str(MONDAY)},
    "Doctor joins waiting list → 403",
    expected=403,
)

log_sub("14.6 Delete waiting list entry (patient)")
c.set_token(state.get("patient_token"))
if state.get("waiting_list_id"):
    c.delete(f"/appointments/waiting-list/{state['waiting_list_id']}/", "Delete waiting list entry (204)")


# ============================================================
# 15. ANALYTICS
# ============================================================
log_section("15. ANALYTICS")

log_sub("15.1 Admin overview")
c.set_token(state.get("admin_token"))
r = c.get("/analytics/admin-overview/", "Admin overview (200)")
if r:
    required = ["users", "doctors", "patients", "appointments", "waiting_list", "notifications", "rates"]
    missing = [k for k in required if k not in r]
    if missing:
        record("Admin overview has all keys", False, 200, 200, f"Missing: {missing}")
    else:
        record("Admin overview has all keys", True, 200, 200)

log_sub("15.2 Appointments by status")
c.get("/analytics/appointments-by-status/", "Appointments by status (200)")

log_sub("15.3 Appointments by month")
r = c.get("/analytics/appointments-by-month/", "Appointments by month (200)")
if r:
    if "results" in r:
        record("Appointments by month has results key", True, 200, 200)
    else:
        record("Appointments by month has results key", False, 200, 200, f"Got: {list(r.keys())}")

log_sub("15.4 Top specializations")
c.get("/analytics/top-specializations/", "Top specializations (200)")

log_sub("15.5 Doctor performance")
c.get("/analytics/doctor-performance/", "Doctor performance (200)")

log_sub("15.6 Patient blocked from analytics")
c.set_token(state.get("patient_token"))
c.get("/analytics/admin-overview/", "Analytics — patient → 403", expected=403)

log_sub("15.7 Receptionist blocked from analytics")
c.set_token(state.get("reception_token"))
c.get("/analytics/admin-overview/", "Analytics — receptionist → 403", expected=403)

log_sub("15.8 Unauthenticated blocked from analytics")
c.set_token(None)
c.get("/analytics/admin-overview/", "Analytics — no token → 401", expected=401)


# ============================================================
# 16. AUTH EDGE CASES
# ============================================================
log_section("16. AUTH EDGE CASES")

log_sub("16.1 Unauthenticated request to protected endpoint")
c.set_token(None)
c.get("/accounts/profile/", "Profile — no token → 401", expected=401)

log_sub("16.2 Invalid token rejected")
c.set_token("thisisnotavalidtoken")
c.get("/accounts/profile/", "Profile — bad token → 401", expected=401)
c.set_token(None)


# ============================================================
# SUMMARY REPORT
# ============================================================
log_section("FINAL SUMMARY")

passed_list = [r for r in results if r["passed"]]
failed_list = [r for r in results if not r["passed"]]
total  = len(results)
passed = len(passed_list)
failed = len(failed_list)

log(f"\n  Total tests : {total}")
log(f"  Passed      : {passed}  ✓")
log(f"  Failed      : {failed}  ✗")
pct = (passed / total * 100) if total else 0
log(f"  Pass rate   : {pct:.1f}%")

if failed_list:
    log(f"\n  {'─'*60}")
    log("  FAILED TESTS:")
    log(f"  {'─'*60}")
    for r in failed_list:
        sc = f"HTTP {r['status_code']}" if r["status_code"] else "NO RESPONSE"
        log(f"  ✗  [{sc}]  {r['name']}")
        if r["note"]:
            log(f"       ↳ {r['note']}")

log(f"\n  {'─'*60}")
if failed == 0:
    log("  ALL TESTS PASSED ✓")
else:
    log(f"  {failed} TEST(S) FAILED — see above for details")
log(f"  {'─'*60}\n")

# ---------------------------------------------------------------------------
# Write log file
# ---------------------------------------------------------------------------
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))

print(f"\nFull log written to: {LOG_FILE}")
sys.exit(0 if failed == 0 else 1)