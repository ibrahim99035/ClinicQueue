
<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { registerUser } from "../../api/auth";
import useTheme from "../../composables/useTheme";
import { Sun, Moon } from "lucide-vue-next";

const router = useRouter();
const { isDark, toggleTheme } = useTheme();

const loading = ref(false);
const errorMessage = ref("");
const successMessage = ref("");

const form = reactive({
  first_name: "",
  last_name: "",
  email: "",
  phone: "",
  user_role: "patient",
  specialization: "",
  password: "",
  password_confirm: "",
});

function validateForm() {
  if (!form.first_name.trim()) return "First name is required.";
  if (!form.last_name.trim()) return "Last name is required.";
  if (!form.email.trim()) return "Email is required.";
  if (!form.phone.trim()) return "Phone is required.";
  if (!form.password) return "Password is required.";
  if (form.password.length < 8) return "Password must be at least 8 characters.";
  if (form.password !== form.password_confirm) return "Passwords do not match.";
  if (form.user_role === "doctor" && !form.specialization) return "Please select a doctor specialization.";
  return "";
}

async function handleRegister() {
  errorMessage.value = "";
  successMessage.value = "";

  const validationError = validateForm();
  if (validationError) {
    errorMessage.value = validationError;
    return;
  }

  loading.value = true;

  try {
    const payload = {
      first_name: form.first_name,
      last_name: form.last_name,
      email: form.email,
      phone: form.phone,
      user_role: form.user_role,
      password: form.password,
      password_confirm: form.password_confirm,
    };

    if (form.user_role === "doctor") {
      payload.specialization = form.specialization;
    }

    await registerUser(payload);

    successMessage.value = "Account created successfully. Please login.";

    setTimeout(() => {
      router.push("/login");
    }, 1000);
  } catch (error) {
  const data = error.response?.data;

  if (data) {
    let messages = [];

    for (const fieldName in data) {
      const fieldErrors = data[fieldName];

      if (Array.isArray(fieldErrors)) {
        messages = messages.concat(fieldErrors);
      } else {
        messages.push(fieldErrors);
      }
    }

    errorMessage.value = messages.join(" ");
  } else {
    errorMessage.value = "Registration failed. Please try again.";
  }
} finally {
  loading.value = false;
}
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-50 px-6 py-8 text-slate-900 dark:bg-slate-950 dark:text-slate-100 md:px-12">
    <!-- Theme toggle -->
    <button
      @click="toggleTheme"
      class="fixed right-6 top-6 z-10 flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-500 shadow-sm transition hover:bg-slate-100 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400 dark:hover:bg-slate-800"
    >
      <Moon v-if="!isDark" class="h-5 w-5" />
      <Sun v-else class="h-5 w-5" />
    </button>

    <div class="w-full max-w-xl rounded-2xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="mb-6 text-center">
        <h1 class="text-3xl font-bold leading-tight tracking-tight text-slate-900 dark:text-slate-100">
          Create Account
        </h1>
        <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">
          Register as a patient or doctor
        </p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="mb-1.5 block text-xs font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">First Name</label>
            <input v-model="form.first_name" type="text" class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100" placeholder="Mohamed" />
          </div>
          <div>
            <label class="mb-1.5 block text-xs font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">Last Name</label>
            <input v-model="form.last_name" type="text" class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100" placeholder="Tarek" />
          </div>
        </div>

        <div>
          <label class="mb-1.5 block text-xs font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">Email</label>
          <input v-model="form.email" type="email" class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100" placeholder="example@email.com" />
        </div>

        <div>
          <label class="mb-1.5 block text-xs font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">Phone</label>
          <input v-model="form.phone" type="text" class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100" placeholder="01000000000" />
        </div>

        <div>
          <label class="mb-1.5 block text-xs font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">Register As</label>
          <select v-model="form.user_role" class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100">
            <option value="patient">Patient</option>
            <option value="doctor">Doctor</option>
          </select>
        </div>

        <div v-if="form.user_role === 'doctor'">
          <label class="mb-1.5 block text-xs font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">Specialization</label>
          <select v-model="form.specialization" class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100">
            <option value="">Select specialization</option>
            <option value="General Medicine">General Medicine</option>
            <option value="Cardiology">Cardiology</option>
            <option value="Dermatology">Dermatology</option>
            <option value="ENT">ENT</option>
            <option value="Pediatrics">Pediatrics</option>
            <option value="Orthopedics">Orthopedics</option>
            <option value="Neurology">Neurology</option>
            <option value="Ophthalmology">Ophthalmology</option>
            <option value="Dentistry">Dentistry</option>
          </select>
        </div>

        <div>
          <label class="mb-1.5 block text-xs font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">Password</label>
          <input v-model="form.password" type="password" class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100" placeholder="Enter password" />
        </div>

        <div>
          <label class="mb-1.5 block text-xs font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">Confirm Password</label>
          <input v-model="form.password_confirm" type="password" class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100" placeholder="Confirm password" />
        </div>

        <p v-if="errorMessage" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-950/50 dark:text-red-300">
          {{ errorMessage }}
        </p>

        <p v-if="successMessage" class="rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700 dark:border-green-800 dark:bg-green-950/50 dark:text-green-300">
          {{ successMessage }}
        </p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full rounded-xl bg-blue-600 px-4 py-3 text-sm font-bold text-white transition-all duration-150 cursor-pointer hover:bg-blue-700 hover:-translate-y-px disabled:cursor-not-allowed disabled:opacity-60"
        >
          {{ loading ? "Creating account..." : "Create Account" }}
        </button>
      </form>

      <div class="mt-6 text-center">
        <p class="text-sm text-slate-500 dark:text-slate-400">
          Already have an account?
          <RouterLink to="/login" class="font-semibold text-blue-600 transition hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">
            Login
          </RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>