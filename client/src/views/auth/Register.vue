
<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { registerUser } from "../../api/auth";

const router = useRouter();

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
  if (!form.first_name.trim()) {
    return "First name is required.";
  }

  if (!form.last_name.trim()) {
    return "Last name is required.";
  }

  if (!form.email.trim()) {
    return "Email is required.";
  }

  if (!form.phone.trim()) {
    return "Phone is required.";
  }

  if (!form.password) {
    return "Password is required.";
  }

  if (form.password.length < 8) {
    return "Password must be at least 8 characters.";
  }

  if (form.password !== form.password_confirm) {
    return "Passwords do not match.";
  }

  if (form.user_role === "doctor" && !form.specialization) {
    return "Please select a doctor specialization.";
  }

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
  <div class="min-h-screen flex items-center justify-center bg-bg px-6 py-8 text-text1 font-sans md:px-12">
    <div class="w-full max-w-xl rounded border border-border bg-surface p-8">
      <div class="mb-6 text-center">
        <h1 class="font-sans text-3xl font-bold leading-tight tracking-tight text-text1">
          Create Account
        </h1>
        <p class="mt-2 font-sans text-sm text-text2">
          Register as a patient or doctor
        </p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="mb-1.5 block font-mono text-[11px] uppercase tracking-mono text-text2">
              First Name
            </label>
            <input
              v-model="form.first_name"
              type="text"
              class="w-full rounded border border-border bg-surface px-3 py-2 font-mono text-sm text-text1 placeholder:text-text3 outline-none transition-all duration-150 focus:border-accent focus:ring-2 focus:ring-accent/10"
              placeholder="Mohamed"
            />
          </div>

          <div>
            <label class="mb-1.5 block font-mono text-[11px] uppercase tracking-mono text-text2">
              Last Name
            </label>
            <input
              v-model="form.last_name"
              type="text"
              class="w-full rounded border border-border bg-surface px-3 py-2 font-mono text-sm text-text1 placeholder:text-text3 outline-none transition-all duration-150 focus:border-accent focus:ring-2 focus:ring-accent/10"
              placeholder="Tarek"
            />
          </div>
        </div>

        <div>
          <label class="mb-1.5 block font-mono text-[11px] uppercase tracking-mono text-text2">
            Email
          </label>
          <input
            v-model="form.email"
            type="email"
            class="w-full rounded border border-border bg-surface px-3 py-2 font-mono text-sm text-text1 placeholder:text-text3 outline-none transition-all duration-150 focus:border-accent focus:ring-2 focus:ring-accent/10"
            placeholder="example@email.com"
          />
        </div>

        <div>
          <label class="mb-1.5 block font-mono text-[11px] uppercase tracking-mono text-text2">
            Phone
          </label>
          <input
            v-model="form.phone"
            type="text"
            class="w-full rounded border border-border bg-surface px-3 py-2 font-mono text-sm text-text1 placeholder:text-text3 outline-none transition-all duration-150 focus:border-accent focus:ring-2 focus:ring-accent/10"
            placeholder="01000000000"
          />
        </div>

        <div>
          <label class="mb-1.5 block font-mono text-[11px] uppercase tracking-mono text-text2">
            Register As
          </label>
          <select
            v-model="form.user_role"
            class="w-full rounded border border-border bg-surface px-3 py-2 font-mono text-sm text-text1 outline-none transition-all duration-150 focus:border-accent focus:ring-2 focus:ring-accent/10"
          >
            <option value="patient">Patient</option>
            <option value="doctor">Doctor</option>
          </select>
        </div>

        <div v-if="form.user_role === 'doctor'">
          <label class="mb-1.5 block font-mono text-[11px] uppercase tracking-mono text-text2">
            Specialization
          </label>
          <select
            v-model="form.specialization"
            class="w-full rounded border border-border bg-surface px-3 py-2 font-mono text-sm text-text1 outline-none transition-all duration-150 focus:border-accent focus:ring-2 focus:ring-accent/10"
          >
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
          <label class="mb-1.5 block font-mono text-[11px] uppercase tracking-mono text-text2">
            Password
          </label>
          <input
            v-model="form.password"
            type="password"
            class="w-full rounded border border-border bg-surface px-3 py-2 font-mono text-sm text-text1 placeholder:text-text3 outline-none transition-all duration-150 focus:border-accent focus:ring-2 focus:ring-accent/10"
            placeholder="Enter password"
          />
        </div>

        <div>
          <label class="mb-1.5 block font-mono text-[11px] uppercase tracking-mono text-text2">
            Confirm Password
          </label>
          <input
            v-model="form.password_confirm"
            type="password"
            class="w-full rounded border border-border bg-surface px-3 py-2 font-mono text-sm text-text1 placeholder:text-text3 outline-none transition-all duration-150 focus:border-accent focus:ring-2 focus:ring-accent/10"
            placeholder="Confirm password"
          />
        </div>

        <p
          v-if="errorMessage"
          class="rounded border border-danger/40 bg-surface px-4 py-3 font-sans text-sm text-danger"
        >
          {{ errorMessage }}
        </p>

        <p
          v-if="successMessage"
          class="rounded border border-accent/40 bg-surface px-4 py-3 font-sans text-sm text-accent"
        >
          {{ successMessage }}
        </p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full rounded bg-accent px-4 py-3 font-mono text-[11px] uppercase tracking-mono-wide text-black transition-all duration-150 cursor-pointer hover:bg-accent-dim hover:-translate-y-px disabled:cursor-not-allowed disabled:opacity-60"
        >
          {{ loading ? "Creating account..." : "Create Account" }}
        </button>
      </form>

      <div class="mt-6 text-center">
        <p class="font-sans text-sm text-text2">
          Already have an account?
          <RouterLink
            to="/login"
            class="font-mono text-[11px] uppercase tracking-mono-wide text-accent transition-all duration-150 cursor-pointer hover:text-accent-dim"
          >
            Login
          </RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>