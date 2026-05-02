<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from "vue";
import PageHeader from "../../components/PageHeader.vue";
import BaseTable from "../../components/ui/BaseTable.vue";
import BaseButton from "../../components/ui/BaseButton.vue";
import { getDoctorsList } from "../../api/appointments";
import {
  getWeeklySchedules,
  createWeeklySchedule,
  updateWeeklySchedule,
  deleteWeeklySchedule,
  getScheduleExceptions,
  createScheduleException,
  updateScheduleException,
  deleteScheduleException,
  generateSlots,
  getAvailableSlots,
} from "../../api/scheduling";
import { normalizeApiError } from "../../composables/useApiError";

const doctorsRaw = ref([]);
const weeklySchedules = ref([]);
const exceptions = ref([]);
const availableSlots = ref([]);

const loading = ref(false);
const savingSchedule = ref(false);
const savingException = ref(false);
const generating = ref(false);
const loadingSlots = ref(false);
const editingScheduleId = ref(null);
const editingExceptionId = ref(null);

const dayOptions = [
  { value: 0, label: "Monday" },
  { value: 1, label: "Tuesday" },
  { value: 2, label: "Wednesday" },
  { value: 3, label: "Thursday" },
  { value: 4, label: "Friday" },
  { value: 5, label: "Saturday" },
  { value: 6, label: "Sunday" },
];

const exceptionTypes = [
  { value: "DAY_OFF", label: "Day Off" },
  { value: "VACATION", label: "Vacation" },
  { value: "EXTRA_WORKING", label: "Extra Working Day" },
];

const scheduleForm = ref({
  doctor: "",
  day_of_week: 0,
  start_time: "",
  end_time: "",
  is_active: true,
});

const exceptionForm = ref({
  doctor: "",
  exception_date: "",
  type: "DAY_OFF",
  start_time: "",
  end_time: "",
  note: "",
});

const generateForm = ref({
  doctor_id: "",
  from_date: "",
  to_date: "",
});

const slotsForm = ref({
  doctor: "",
  date: "",
});

const errorMessage = ref("");
const successMessage = ref("");
const toast = ref({
  show: false,
  type: "success",
  message: "",
});

let toastTimer = null;

function showToast(message, type) {
  toast.value = {
    show: true,
    type,
    message,
  };

  if (toastTimer) {
    clearTimeout(toastTimer);
    toastTimer = null;
  }

  toastTimer = setTimeout(() => {
    toast.value = { show: false, type: "success", message: "" };
    toastTimer = null;
  }, 4500);
}

function closeToast() {
  if (toastTimer) {
    clearTimeout(toastTimer);
    toastTimer = null;
  }
  toast.value = { show: false, type: "success", message: "" };
}

function normalizeDoctor(user) {
  const profile = user.doctor_profile || user.doctorProfile || user.profile || user;
  const firstName =
    user.first_name ||
    user.firstName ||
    user.user?.first_name ||
    user.user?.firstName ||
    "";
  const lastName =
    user.last_name ||
    user.lastName ||
    user.user?.last_name ||
    user.user?.lastName ||
    "";

  const name =
    user.name ||
    user.full_name ||
    user.fullName ||
    user.doctor_name ||
    user.doctorName ||
    `${firstName} ${lastName}`.trim() ||
    user.email ||
    user.user?.email ||
    "Unknown Doctor";

  return {
    userId: user.id || user.user?.id || null,
    profileId: profile.id || user.profileId || user.doctor_profile_id || user.id,
    name,
    email: user.email || user.user?.email || "",
    specialization: profile.specialization || user.specialization || "Specialization not specified",
    consultationDuration:
      profile.consultationDuration ||
      profile.consultation_duration ||
      user.consultationDuration ||
      user.consultation_duration ||
      15,
  };
}

const doctors = computed(() => doctorsRaw.value.map(normalizeDoctor));

function getDoctorByProfileId(profileId) {
  const id = Number(profileId);
  return doctors.value.find((item) => Number(item.profileId) === id);
}

function getDoctorName(profileId) {
  const doctor = getDoctorByProfileId(profileId);
  return doctor ? doctor.name : `Doctor #${profileId}`;
}

function getDayLabel(dayValue) {
  const day = dayOptions.find((item) => Number(item.value) === Number(dayValue));
  return day ? day.label : dayValue;
}

function getExceptionTypeLabel(type) {
  const matched = exceptionTypes.find((item) => item.value === type);
  return matched ? matched.label : type;
}

function formatDateTime(value) {
  if (!value) return "-";
  return new Date(value).toLocaleString();
}

function resetScheduleForm() {
  editingScheduleId.value = null;
  scheduleForm.value = {
    doctor: "",
    day_of_week: 0,
    start_time: "",
    end_time: "",
    is_active: true,
  };
}

function resetExceptionForm() {
  editingExceptionId.value = null;
  exceptionForm.value = {
    doctor: "",
    exception_date: "",
    type: "DAY_OFF",
    start_time: "",
    end_time: "",
    note: "",
  };
}

function getTodayDate() {
  return new Date().toISOString().slice(0, 10);
}

function startEditSchedule(schedule) {
  editingScheduleId.value = schedule.id;
  scheduleForm.value = {
    doctor: String(schedule.doctor?.id || schedule.doctor || ""),
    day_of_week: Number(schedule.day_of_week),
    start_time: schedule.start_time || "",
    end_time: schedule.end_time || "",
    is_active: Boolean(schedule.is_active),
  };
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function startEditException(exceptionItem) {
  editingExceptionId.value = exceptionItem.id;
  exceptionForm.value = {
    doctor: String(exceptionItem.doctor?.id || exceptionItem.doctor || ""),
    exception_date: exceptionItem.exception_date || "",
    type: exceptionItem.type || "DAY_OFF",
    start_time: exceptionItem.start_time || "",
    end_time: exceptionItem.end_time || "",
    note: exceptionItem.note || "",
  };
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function loadDoctors() {
  const rawDoctors = await getDoctorsList();
  const doctorsData = rawDoctors?.data || rawDoctors;
  doctorsRaw.value = Array.isArray(doctorsData) ? doctorsData : doctorsData?.results || [];
}

async function loadSchedulingData() {
  loading.value = true;
  errorMessage.value = "";
  successMessage.value = "";
  try {
    await loadDoctors();
    weeklySchedules.value = await getWeeklySchedules();
    exceptions.value = await getScheduleExceptions();
  } catch (error) {
    errorMessage.value = normalizeApiError(error);
    showToast(errorMessage.value, "error");
  } finally {
    loading.value = false;
  }
}

async function submitWeeklySchedule() {
  errorMessage.value = "";
  successMessage.value = "";
  if (!scheduleForm.value.doctor || !scheduleForm.value.start_time || !scheduleForm.value.end_time) {
    errorMessage.value = "Please select doctor, start time, and end time.";
    showToast(errorMessage.value, "error");
    return;
  }

  savingSchedule.value = true;
  try {
    const payload = {
      doctor: Number(scheduleForm.value.doctor),
      day_of_week: Number(scheduleForm.value.day_of_week),
      start_time: scheduleForm.value.start_time,
      end_time: scheduleForm.value.end_time,
      is_active: scheduleForm.value.is_active,
    };

    if (editingScheduleId.value) {
      await updateWeeklySchedule(editingScheduleId.value, payload);
      successMessage.value = "Weekly schedule updated successfully.";
    } else {
      await createWeeklySchedule(payload);
      successMessage.value = "Weekly schedule created successfully.";
    }

    showToast(successMessage.value, "success");
    resetScheduleForm();
    weeklySchedules.value = await getWeeklySchedules();
  } catch (error) {
    errorMessage.value = normalizeApiError(error);
    showToast(errorMessage.value, "error");
  } finally {
    savingSchedule.value = false;
  }
}

async function handleDeleteWeeklySchedule(schedule) {
  errorMessage.value = "";
  successMessage.value = "";
  const confirmed = window.confirm("Are you sure you want to delete this weekly schedule?");
  if (!confirmed) return;

  try {
    await deleteWeeklySchedule(schedule.id);
    successMessage.value = "Weekly schedule deleted successfully.";
    showToast(successMessage.value, "success");
    weeklySchedules.value = await getWeeklySchedules();
  } catch (error) {
    errorMessage.value = normalizeApiError(error);
    showToast(errorMessage.value, "error");
  }
}

async function submitScheduleException() {
  errorMessage.value = "";
  successMessage.value = "";

  if (!exceptionForm.value.doctor || !exceptionForm.value.exception_date) {
    errorMessage.value = "Please select doctor and exception date.";
    showToast(errorMessage.value, "error");
    return;
  }

  if (
    exceptionForm.value.type === "EXTRA_WORKING" &&
    (!exceptionForm.value.start_time || !exceptionForm.value.end_time)
  ) {
    errorMessage.value = "Extra working day requires start time and end time.";
    showToast(errorMessage.value, "error");
    return;
  }

  savingException.value = true;
  try {
    const payload = {
      doctor: Number(exceptionForm.value.doctor),
      exception_date: exceptionForm.value.exception_date,
      type: exceptionForm.value.type,
      note: exceptionForm.value.note,
    };

    if (exceptionForm.value.type === "EXTRA_WORKING") {
      payload.start_time = exceptionForm.value.start_time;
      payload.end_time = exceptionForm.value.end_time;
    } else {
      payload.start_time = null;
      payload.end_time = null;
    }

    if (editingExceptionId.value) {
      await updateScheduleException(editingExceptionId.value, payload);
      successMessage.value = "Schedule exception updated successfully.";
    } else {
      await createScheduleException(payload);
      successMessage.value = "Schedule exception created successfully.";
    }

    showToast(successMessage.value, "success");
    resetExceptionForm();
    exceptions.value = await getScheduleExceptions();
  } catch (error) {
    errorMessage.value = normalizeApiError(error);
    showToast(errorMessage.value, "error");
  } finally {
    savingException.value = false;
  }
}

async function handleDeleteException(exceptionItem) {
  errorMessage.value = "";
  successMessage.value = "";
  const confirmed = window.confirm("Are you sure you want to delete this exception?");
  if (!confirmed) return;

  try {
    await deleteScheduleException(exceptionItem.id);
    successMessage.value = "Schedule exception deleted successfully.";
    showToast(successMessage.value, "success");
    exceptions.value = await getScheduleExceptions();
  } catch (error) {
    errorMessage.value = normalizeApiError(error);
    showToast(errorMessage.value, "error");
  }
}

async function submitGenerateSlots() {
  errorMessage.value = "";
  successMessage.value = "";

  const doctor = generateForm.value.doctor_id;
  const startDate = generateForm.value.from_date;
  const endDate = generateForm.value.to_date;

  if (!doctor || !startDate || !endDate) {
    errorMessage.value = "Please select doctor, start date, and end date.";
    showToast(errorMessage.value, "error");
    return;
  }

  const today = getTodayDate();
  if (startDate < today) {
    errorMessage.value = "Cannot generate slots for past dates.";
    showToast(errorMessage.value, "error");
    return;
  }
  if (endDate < startDate) {
    errorMessage.value = "End date cannot be before start date.";
    showToast(errorMessage.value, "error");
    return;
  }

  generating.value = true;
  try {
    const payload = {
      doctor: Number(doctor),
      start_date: startDate,
      end_date: endDate,
    };
    const result = await generateSlots(payload);
    successMessage.value = `${result.count || 0} slots generated successfully.`;
    showToast(successMessage.value, "success");
  } catch (error) {
    errorMessage.value = normalizeApiError(error);
    showToast(errorMessage.value, "error");
  } finally {
    generating.value = false;
  }
}

async function submitLoadSlots() {
  errorMessage.value = "";
  successMessage.value = "";
  if (!slotsForm.value.doctor || !slotsForm.value.date) {
    errorMessage.value = "Please select doctor and date.";
    showToast(errorMessage.value, "error");
    return;
  }

  loadingSlots.value = true;
  try {
    availableSlots.value = await getAvailableSlots({
      doctor: Number(slotsForm.value.doctor),
      date: slotsForm.value.date,
    });
  } catch (error) {
    errorMessage.value = normalizeApiError(error);
    showToast(errorMessage.value, "error");
  } finally {
    loadingSlots.value = false;
  }
}

onMounted(() => {
  loadSchedulingData();
});

onBeforeUnmount(() => {
  if (toastTimer) {
    clearTimeout(toastTimer);
    toastTimer = null;
  }
});
</script>

<template>
  <div class="min-h-screen p-6">
    <Transition name="toast-slide">
      <div
        v-if="toast.show"
        class="fixed right-6 top-6 z-50 w-full max-w-sm rounded-2xl border p-4 shadow-2xl"
        :class="
          toast.type === 'success'
            ? 'border-green-200 bg-green-50 text-green-800 dark:border-green-800 dark:bg-green-950/50 dark:text-green-300'
            : 'border-red-200 bg-red-50 text-red-800 dark:border-red-800 dark:bg-red-950/50 dark:text-red-300'
        "
      >
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-sm font-bold">
              {{ toast.type === "success" ? "Success" : "Error" }}
            </p>
            <p class="mt-1 text-sm leading-6">
              {{ toast.message }}
            </p>
          </div>
          <button
            type="button"
            @click="closeToast"
            class="rounded-lg px-2 py-1 text-sm font-bold hover:bg-black/5"
          >
            ×
          </button>
        </div>
      </div>
    </Transition>

    <div class="mx-auto flex max-w-7xl flex-col gap-6">
      <PageHeader
        title="Scheduling Management"
        subtitle="Manage doctor weekly schedules, exceptions, slot generation, and available appointment slots."
        :badge="`${doctors.length} doctors`"
        badgeColor="blue"
      />

      <div class="grid gap-5 md:grid-cols-3">
        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <span class="text-sm font-semibold text-slate-500 dark:text-slate-400">Doctors</span>
          <strong class="mt-2 block text-3xl font-bold text-slate-900 dark:text-slate-100">{{ doctors.length }}</strong>
        </div>
        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <span class="text-sm font-semibold text-slate-500 dark:text-slate-400">Weekly Schedules</span>
          <strong class="mt-2 block text-3xl font-bold text-slate-900 dark:text-slate-100">{{ weeklySchedules.length }}</strong>
        </div>
        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <span class="text-sm font-semibold text-slate-500 dark:text-slate-400">Exceptions</span>
          <strong class="mt-2 block text-3xl font-bold text-slate-900 dark:text-slate-100">{{ exceptions.length }}</strong>
        </div>
      </div>

      <div class="grid gap-6 xl:grid-cols-2">
        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h3 class="text-xl font-bold text-slate-900 dark:text-slate-100">Create Weekly Schedule</h3>
          <form @submit.prevent="submitWeeklySchedule" class="mt-5 grid gap-4 md:grid-cols-2">
            <div class="md:col-span-2">
              <label class="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-300">Doctor *</label>
              <select v-model="scheduleForm.doctor" class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100">
                <option value="">Select doctor</option>
                <option v-if="doctors.length === 0" disabled>No doctors available</option>
                <option v-for="doctor in doctors" :key="doctor.profileId" :value="doctor.profileId">
                  Dr. {{ doctor.name }} — {{ doctor.specialization }}
                </option>
              </select>
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-300">Day *</label>
              <select v-model="scheduleForm.day_of_week" class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100">
                <option v-for="day in dayOptions" :key="day.value" :value="day.value">{{ day.label }}</option>
              </select>
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-300">Start Time *</label>
              <input v-model="scheduleForm.start_time" type="time" class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100" />
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-300">End Time *</label>
              <input v-model="scheduleForm.end_time" type="time" class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100" />
            </div>

            <label class="flex items-center gap-2 rounded-xl bg-slate-50 px-3 py-2.5 text-sm font-semibold text-slate-700 dark:bg-slate-800 dark:text-slate-300">
              <input v-model="scheduleForm.is_active" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500" />
              Active schedule
            </label>

            <div class="flex gap-3 md:col-span-2">
              <button type="submit" :disabled="savingSchedule" class="rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400">
                {{ savingSchedule ? "Saving..." : editingScheduleId ? "Update Schedule" : "Create Schedule" }}
              </button>
              <button type="button" @click="resetScheduleForm" class="rounded-xl bg-slate-100 px-4 py-2.5 text-sm font-bold text-slate-700 transition hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700">
                Reset
              </button>
            </div>
          </form>
        </div>

        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h3 class="text-xl font-bold text-slate-900 dark:text-slate-100">Create Schedule Exception</h3>
          <form @submit.prevent="submitScheduleException" class="mt-5 grid gap-4 md:grid-cols-2">
            <div class="md:col-span-2">
              <label class="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-300">Doctor *</label>
              <select v-model="exceptionForm.doctor" class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100">
                <option value="">Select doctor</option>
                <option v-if="doctors.length === 0" disabled>No doctors available</option>
                <option v-for="doctor in doctors" :key="doctor.profileId" :value="doctor.profileId">
                  Dr. {{ doctor.name }} — {{ doctor.specialization }}
                </option>
              </select>
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-300">Date *</label>
              <input v-model="exceptionForm.exception_date" type="date" class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100" />
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-300">Type *</label>
              <select v-model="exceptionForm.type" class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100">
                <option v-for="typeItem in exceptionTypes" :key="typeItem.value" :value="typeItem.value">{{ typeItem.label }}</option>
              </select>
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-300">Start Time</label>
              <input v-model="exceptionForm.start_time" type="time" :disabled="exceptionForm.type !== 'EXTRA_WORKING'" class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-400 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100" />
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-300">End Time</label>
              <input v-model="exceptionForm.end_time" type="time" :disabled="exceptionForm.type !== 'EXTRA_WORKING'" class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-400 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100" />
            </div>

            <div class="md:col-span-2">
              <label class="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-300">Note</label>
              <textarea v-model="exceptionForm.note" rows="3" class="w-full resize-y rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"></textarea>
            </div>

            <div class="flex gap-3 md:col-span-2">
              <button type="submit" :disabled="savingException" class="rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400">
                {{ savingException ? "Saving..." : editingExceptionId ? "Update Exception" : "Create Exception" }}
              </button>
              <button type="button" @click="resetExceptionForm" class="rounded-xl bg-slate-100 px-4 py-2.5 text-sm font-bold text-slate-700 transition hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700">
                Reset
              </button>
            </div>
          </form>
        </div>
      </div>

      <div class="grid gap-6 xl:grid-cols-2">
        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h3 class="text-xl font-bold text-slate-900 dark:text-slate-100">Generate Slots</h3>
          <form @submit.prevent="submitGenerateSlots" class="mt-5 grid gap-4 md:grid-cols-2">
            <div class="md:col-span-2">
              <label class="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-300">Doctor *</label>
              <select v-model="generateForm.doctor_id" class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100">
                <option value="">Select doctor</option>
                <option v-if="doctors.length === 0" disabled>No doctors available</option>
                <option v-for="doctor in doctors" :key="doctor.profileId" :value="doctor.profileId">
                  Dr. {{ doctor.name }} — {{ doctor.specialization }}
                </option>
              </select>
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-300">From Date *</label>
              <input v-model="generateForm.from_date" type="date" class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100" />
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-300">To Date *</label>
              <input v-model="generateForm.to_date" type="date" class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100" />
            </div>

            <div class="md:col-span-2">
              <button type="submit" :disabled="generating" class="rounded-xl bg-green-600 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-green-700 disabled:cursor-not-allowed disabled:bg-slate-400">
                {{ generating ? "Generating..." : "Generate Slots" }}
              </button>
            </div>
          </form>
        </div>

        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h3 class="text-xl font-bold text-slate-900 dark:text-slate-100">View Available Slots</h3>
          <form @submit.prevent="submitLoadSlots" class="mt-5 grid gap-4 md:grid-cols-2">
            <div class="md:col-span-2">
              <label class="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-300">Doctor *</label>
              <select v-model="slotsForm.doctor" class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100">
                <option value="">Select doctor</option>
                <option v-if="doctors.length === 0" disabled>No doctors available</option>
                <option v-for="doctor in doctors" :key="doctor.profileId" :value="doctor.profileId">
                  Dr. {{ doctor.name }} — {{ doctor.specialization }}
                </option>
              </select>
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-300">Date *</label>
              <input v-model="slotsForm.date" type="date" class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100" />
            </div>

            <div class="flex items-end">
              <button type="submit" :disabled="loadingSlots" class="rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400">
                {{ loadingSlots ? "Loading..." : "Load Slots" }}
              </button>
            </div>
          </form>

          <div class="mt-5 flex flex-col gap-2">
            <div v-if="availableSlots.length === 0" class="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-5 text-sm text-slate-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400">
              No slots loaded.
            </div>
            <div v-for="slot in availableSlots" :key="slot.id" class="flex items-center justify-between gap-4 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-slate-700 dark:bg-slate-800">
              <span class="text-sm text-slate-700 dark:text-slate-300">
                {{ formatDateTime(slot.start_datetime) }} → {{ formatDateTime(slot.end_datetime) }}
              </span>
              <strong class="rounded-full px-3 py-1 text-xs font-bold" :class="slot.is_available ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">
                {{ slot.is_available ? "Available" : "Unavailable" }}
              </strong>
            </div>
          </div>
        </div>
      </div>

      <BaseTable :items="weeklySchedules" :loading="loading" title="Weekly Schedules" table-class="min-w-[850px]">
        <template #toolbar>
          <span class="rounded-full bg-blue-100 px-4 py-2 text-sm font-bold text-blue-700">{{ weeklySchedules.length }} schedule(s)</span>
        </template>
        <template #thead>
          <th class="border-b border-slate-200 px-6 py-4 font-bold">Doctor</th>
          <th class="border-b border-slate-200 px-6 py-4 font-bold">Day</th>
          <th class="border-b border-slate-200 px-6 py-4 font-bold">Start</th>
          <th class="border-b border-slate-200 px-6 py-4 font-bold">End</th>
          <th class="border-b border-slate-200 px-6 py-4 font-bold">Status</th>
          <th class="w-32 border-b border-slate-200 px-6 py-4 font-bold">Action</th>
        </template>
        <template #tbody="{ items }">
          <tr v-for="schedule in items" :key="schedule.id" class="text-sm text-slate-900 transition hover:bg-blue-50/60 dark:text-slate-200 dark:hover:bg-slate-800/50">
            <td class="border-b border-slate-100 px-6 py-4">{{ getDoctorName(schedule.doctor) }}</td>
            <td class="border-b border-slate-100 px-6 py-4">{{ getDayLabel(schedule.day_of_week) }}</td>
            <td class="border-b border-slate-100 px-6 py-4">{{ schedule.start_time }}</td>
            <td class="border-b border-slate-100 px-6 py-4">{{ schedule.end_time }}</td>
            <td class="border-b border-slate-100 px-6 py-4"><span class="inline-flex rounded-full px-3 py-1 text-xs font-bold" :class="schedule.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">{{ schedule.is_active ? "Active" : "Inactive" }}</span></td>
            <td class="border-b border-slate-100 px-6 py-4">
              <div class="flex gap-2">
                <BaseButton size="sm" variant="secondary" @click="startEditSchedule(schedule)">Edit</BaseButton>
                <BaseButton size="sm" variant="danger" @click="handleDeleteWeeklySchedule(schedule)">Delete</BaseButton>
              </div>
            </td>
          </tr>
        </template>
        <template #pagination>
          <div class="text-sm font-semibold text-gray-700">Showing {{ weeklySchedules.length }} schedule(s)</div>
        </template>
      </BaseTable>

      <BaseTable :items="exceptions" :loading="loading" title="Schedule Exceptions" table-class="min-w-[950px]">
        <template #toolbar>
          <span class="rounded-full bg-amber-100 px-4 py-2 text-sm font-bold text-amber-700">{{ exceptions.length }} exception(s)</span>
        </template>
        <template #thead>
          <th class="border-b border-slate-200 px-6 py-4 font-bold">Doctor</th>
          <th class="border-b border-slate-200 px-6 py-4 font-bold">Date</th>
          <th class="border-b border-slate-200 px-6 py-4 font-bold">Type</th>
          <th class="border-b border-slate-200 px-6 py-4 font-bold">Start</th>
          <th class="border-b border-slate-200 px-6 py-4 font-bold">End</th>
          <th class="border-b border-slate-200 px-6 py-4 font-bold">Note</th>
          <th class="w-32 border-b border-slate-200 px-6 py-4 font-bold">Action</th>
        </template>
        <template #tbody="{ items }">
          <tr v-for="exceptionItem in items" :key="exceptionItem.id" class="text-sm text-slate-900 transition hover:bg-blue-50/60 dark:text-slate-200 dark:hover:bg-slate-800/50">
            <td class="border-b border-slate-100 px-6 py-4">{{ getDoctorName(exceptionItem.doctor) }}</td>
            <td class="border-b border-slate-100 px-6 py-4">{{ exceptionItem.exception_date }}</td>
            <td class="border-b border-slate-100 px-6 py-4">{{ getExceptionTypeLabel(exceptionItem.type) }}</td>
            <td class="border-b border-slate-100 px-6 py-4">{{ exceptionItem.start_time || "-" }}</td>
            <td class="border-b border-slate-100 px-6 py-4">{{ exceptionItem.end_time || "-" }}</td>
            <td class="border-b border-slate-100 px-6 py-4">{{ exceptionItem.note || "-" }}</td>
            <td class="border-b border-slate-100 px-6 py-4">
              <div class="flex gap-2">
                <BaseButton size="sm" variant="secondary" @click="startEditException(exceptionItem)">Edit</BaseButton>
                <BaseButton size="sm" variant="danger" @click="handleDeleteException(exceptionItem)">Delete</BaseButton>
              </div>
            </td>
          </tr>
        </template>
        <template #pagination>
          <div class="text-sm font-semibold text-gray-700">Showing {{ exceptions.length }} exception(s)</div>
        </template>
      </BaseTable>
    </div>
  </div>
</template>
