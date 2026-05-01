
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
  <div class="min-h-screen flex items-center justify-center bg-slate-100 px-4">
    <div class="w-full max-w-xl bg-white rounded-2xl shadow-lg p-8">
      <div class="mb-6 text-center">
        <h1 class="text-3xl font-bold text-slate-800">
          Create Account
        </h1>
        <p class="text-slate-500 mt-2">
          Register as a patient or doctor
        </p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">
              First Name
            </label>
            <input
              v-model="form.first_name"
              type="text"
              class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Mohamed"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">
              Last Name
            </label>
            <input
              v-model="form.last_name"
              type="text"
              class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Tarek"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">
            Email
          </label>
          <input
            v-model="form.email"
            type="email"
            class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="example@email.com"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">
            Phone
          </label>
          <input
            v-model="form.phone"
            type="text"
            class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="01000000000"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">
            Register As
          </label>
          <select
            v-model="form.user_role"
            class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
          >
            <option value="patient">Patient</option>
            <option value="doctor">Doctor</option>
          </select>
        </div>

        <div v-if="form.user_role === 'doctor'">
          <label class="block text-sm font-medium text-slate-700 mb-1">
            Specialization
          </label>
          <select
            v-model="form.specialization"
            class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
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
          <label class="block text-sm font-medium text-slate-700 mb-1">
            Password
          </label>
          <input
            v-model="form.password"
            type="password"
            class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter password"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">
            Confirm Password
          </label>
          <input
            v-model="form.password_confirm"
            type="password"
            class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Confirm password"
          />
        </div>

        <p
          v-if="errorMessage"
          class="text-sm text-red-600 bg-red-50 p-3 rounded-lg"
        >
          {{ errorMessage }}
        </p>

        <p
          v-if="successMessage"
          class="text-sm text-green-600 bg-green-50 p-3 rounded-lg"
        >
          {{ successMessage }}
        </p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold py-3 rounded-lg transition"
        >
          {{ loading ? "Creating account..." : "Create Account" }}
        </button>
      </form>

      <div class="mt-6 text-center">
        <p class="text-sm text-slate-600">
          Already have an account?
          <RouterLink
            to="/login"
            class="text-blue-600 font-semibold hover:underline"
          >
            Login
          </RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>