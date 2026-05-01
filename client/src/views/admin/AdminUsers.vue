<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch } from "vue";
import api from "../../api/client";
import { createStaffUser, updateUser, deleteUser } from "../../api/admin";
import PageHeader from "../../components/PageHeader.vue";
import StatusBadge from "../../components/StatusBadge.vue";
import SkeletonCard from "../../components/SkeletonCard.vue";
import EmptyState from "../../components/EmptyState.vue";
import BaseButton from "../../components/ui/BaseButton.vue";
import BaseModal from "../../components/ui/BaseModal.vue";
import BasePagination from "../../components/ui/BasePagination.vue";
import BaseTable from "../../components/ui/BaseTable.vue";
import { normalizeApiError } from "../../composables/useApiError";

const currentUser = JSON.parse(localStorage.getItem("user") || "{}");
const users = ref([]);
const loading = ref(false);
const saving = ref(false);
const errorMessage = ref("");
const successMessage = ref("");
const deletingId = ref(null);
const totalUsers = ref(0);

const toast = ref({
  show: false,
  type: "success",
  message: "",
});

let toastTimer = null;

function showToast(message, type) {
  toast.value = {
    show: true,
    type: type,
    message: message,
  };

  if (toastTimer) {
    clearTimeout(toastTimer);
  }

  toastTimer = setTimeout(() => {
    toast.value.show = false;
  }, 30000);
}

function closeToast() {
  toast.value.show = false;

  if (toastTimer) {
    clearTimeout(toastTimer);
  }
}

onBeforeUnmount(() => {
  if (toastTimer) {
    clearTimeout(toastTimer);
  }
});
const searchFilter = ref("");
const roleFilter = ref("all");
const statusFilter = ref("all");
const showCreateForm = ref(false);
const editUserId = ref(null);
const currentPage = ref(1);
const itemsPerPage = 10;

const createForm = ref({
  email: "",
  password: "",
  first_name: "",
  last_name: "",
  phone: "",
  role: "receptionist",
});

const editForm = ref({
  email: "",
  first_name: "",
  last_name: "",
  phone: "",
});

function getUserGroup(user) {
  const g = user.groups;
  const r = user.roles;
  if (Array.isArray(g) && g.length) return g;
  if (Array.isArray(r) && r.length) return r;
  return [];
}

function getPrimaryRoleOfUser(user) {
  const group = getUserGroup(user); 
  if (group.includes("Admins")) return "Admin";
  if (group.includes("Receptionists")) return "Receptionist";
  if (group.includes("Doctors")) return "Doctor";
  if (group.includes("Patients")) return "Patient";

  return "No Role";
}

function getRoleValue(user) {
  const groups = getUserGroup(user);

  if (groups.includes("Admins")) return "admin";
  if (groups.includes("Receptionists")) return "receptionist";
  if (groups.includes("Doctors")) return "doctor";
  if (groups.includes("Patients")) return "patient";

  return "";
}

function getRoleBadgeClass(user) {
  const role = getPrimaryRoleOfUser(user);

  if (role === "Admin") return "bg-blue-100 text-blue-700";
  if (role === "Receptionist") return "bg-amber-100 text-amber-800";
  if (role === "Doctor") return "bg-green-100 text-green-700";
  if (role === "Patient") return "bg-purple-100 text-purple-700";

  return "bg-gray-100 text-gray-700";
}

function getStatusBadgeClass(user) {
  if (user.is_active) {
    return "bg-green-100 text-green-700";
  }

  return "bg-red-100 text-red-700";
}

function formatName(user) {
    const firstName = user.first_name || "";
    const lastName = user.last_name || "";

    const fullName = (firstName + " " + lastName).trim();
  return fullName || "No name";
}

async function loadUsers() {
  loading.value = true;
  errorMessage.value = "";

  try {
    const response = await api.get("/accounts/users/");
    const data = response.data;
    users.value = Array.isArray(data) ? data : data.results || [];
    totalUsers.value =
      typeof data.count === "number" ? data.count : users.value.length;
  } catch (error) {
    errorMessage.value = normalizeApiError(error);
  } finally {
    loading.value = false;
  }
}

const filteredUsers = computed(()=>{
    const searchText = searchFilter.value.trim().toLowerCase();
    return users.value.filter((user)=> {
    const fullName = `${user.first_name || ""} ${user.last_name || ""}`.toLowerCase();
    const email = (user.email || "").toLowerCase();
    const phone = (user.phone || "").toLowerCase();

    if (searchText) {
        const foundBySearch = 
        fullName.includes(searchText) ||
        email.includes(searchText) ||
        phone.includes(searchText);

      if (!foundBySearch) {
        return false;
      }
    }
    if (roleFilter.value !== "all") {
      const groups = getUserGroup(user);

      if (!groups.includes(roleFilter.value)) {
        return false;
      }
    }
    if (statusFilter.value === "active" && !user.is_active) {
      return false;
    }
    if (statusFilter.value === "inactive" && user.is_active) {
      return false;
    }
    return true;
    })
})

const totalPages = computed(() => {
  return Math.ceil(filteredUsers.value.length / itemsPerPage) || 1;
});

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return filteredUsers.value.slice(start, end);
});

watch([searchFilter, roleFilter, statusFilter], () => {
  currentPage.value = 1;
});

function resetCreateForm() {
    createForm.value = {
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    phone: "",
    role: "receptionist",
  };
}

async function submitCreateUser() {
  errorMessage.value = "";
  successMessage.value = "";

  if (
    !createForm.value.email ||
    !createForm.value.password ||
    !createForm.value.first_name ||
    !createForm.value.last_name ||
    !createForm.value.role
  ) {
    errorMessage.value = "Please fill all required fields.";
    showToast(errorMessage.value, "error");
    return;
  }

  saving.value = true;

  try {
    await createStaffUser({
      email: createForm.value.email,
      password: createForm.value.password,
      first_name: createForm.value.first_name,
      last_name: createForm.value.last_name,
      phone: createForm.value.phone,
      role: createForm.value.role,
    });

    await loadUsers();
    resetCreateForm();
    showCreateForm.value = false;
    successMessage.value = "Staff user created successfully.";
    showToast(successMessage.value, "success");
  } catch (error) {
    errorMessage.value = normalizeApiError(error);
    showToast(errorMessage.value, "error");
  } finally {
    saving.value = false;
  }
}

function startEdit(user) {
  editUserId.value = user.id;

  editForm.value = {
    email: user.email || "",
    first_name: user.first_name || "",
    last_name: user.last_name || "",
    phone: user.phone || "",
  };
}

function cancelEdit() {
  editUserId.value = null;

  editForm.value = {
    email: "",
    first_name: "",
    last_name: "",
    phone: "",
  };
}

async function submitEditUser(user) {
  errorMessage.value = "";
  successMessage.value = "";

  if (!editForm.value.email) {
    errorMessage.value = "Email is required.";
    showToast(errorMessage.value, "error");
    return;
  }

  saving.value = true;

  try {
await updateUser(user.id, {
  email: editForm.value.email,
  first_name: editForm.value.first_name,
  last_name: editForm.value.last_name,
  phone: editForm.value.phone,
});

    successMessage.value = "User updated successfully.";
    showToast(successMessage.value, "success");
    cancelEdit();
    await loadUsers();
  } catch (error) {
    errorMessage.value = normalizeApiError(error);
    showToast(errorMessage.value, "error");
  } finally {
    saving.value = false;
  }
}

async function handleDeleteUser(user) {
  errorMessage.value = "";
  successMessage.value = "";

  if (user.id === currentUser.id) {
    errorMessage.value = "You cannot delete your own logged-in admin account from here.";
    showToast(errorMessage.value, "error");
    return;
  }

  const confirmed = window.confirm(
    `Are you sure you want to delete ${user.email}?`
  );

  if (!confirmed) {
    return;
  }

  deletingId.value = user.id;

  try {
    await deleteUser(user.id);
    successMessage.value = "User deleted successfully.";
    showToast(successMessage.value, "success");
    await loadUsers();
  } catch (error) {
    errorMessage.value = normalizeApiError(error);
    showToast(errorMessage.value, "error");
  } finally {
    deletingId.value = null;
  }
}

onMounted(() => {
  loadUsers();
});

</script>

<template>
  <div class="space-y-6">
    <!-- Toast Notification -->
    <Transition name="toast-slide">
      <div
        v-if="toast.show"
        class="fixed right-6 top-6 z-50 w-full max-w-sm rounded-2xl border p-4 shadow-2xl"
        :class="
          toast.type === 'success'
            ? 'border-green-200 bg-green-50 text-green-800'
            : 'border-red-200 bg-red-50 text-red-800'
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

    <!-- Header -->
    <PageHeader 
      title="Users Management"
      subtitle="View system users, create staff accounts, and update basic user information."
      :badge="`${filteredUsers.length} result(s) · ${totalUsers} total loaded`"
      badgeColor="blue"
    />

    <!-- Error Message -->
    <transition name="fade">
      <div
        v-if="errorMessage"
        class="rounded-2xl border border-red-200 bg-red-50/80 px-6 py-4 text-sm font-semibold text-red-700 shadow-sm backdrop-blur"
      >
        ⚠️ {{ errorMessage }}
      </div>
    </transition>

    <!-- Success Message -->
    <transition name="fade">
      <div
        v-if="successMessage"
        class="rounded-2xl border border-green-200 bg-green-50/80 px-6 py-4 text-sm font-semibold text-green-700 shadow-sm backdrop-blur"
      >
        ✅ {{ successMessage }}
      </div>
    </transition>

    <BaseModal v-model="showCreateForm" title="Create New Staff User">
      <form class="grid gap-4 md:grid-cols-2" @submit.prevent="submitCreateUser">
        <div class="flex flex-col gap-2">
          <label class="text-sm font-semibold text-gray-700">First Name *</label>
          <input
            v-model="createForm.first_name"
            type="text"
            class="rounded-lg border border-gray-300 px-3 py-2.5 text-sm outline-none transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            placeholder="First name"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-semibold text-gray-700">Last Name *</label>
          <input
            v-model="createForm.last_name"
            type="text"
            class="rounded-lg border border-gray-300 px-3 py-2.5 text-sm outline-none transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            placeholder="Last name"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-semibold text-gray-700">Email *</label>
          <input
            v-model="createForm.email"
            type="email"
            class="rounded-lg border border-gray-300 px-3 py-2.5 text-sm outline-none transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            placeholder="user@email.com"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-semibold text-gray-700">Phone</label>
          <input
            v-model="createForm.phone"
            type="text"
            class="rounded-lg border border-gray-300 px-3 py-2.5 text-sm outline-none transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            placeholder="Phone number"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-semibold text-gray-700">Password *</label>
          <input
            v-model="createForm.password"
            type="password"
            class="rounded-lg border border-gray-300 px-3 py-2.5 text-sm outline-none transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            placeholder="Password"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-semibold text-gray-700">Role *</label>
          <select
            v-model="createForm.role"
            class="rounded-lg border border-gray-300 px-3 py-2.5 text-sm outline-none transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
          >
            <option value="">Select role</option>
            <option value="receptionist">Receptionist</option>
            <option value="admin">Admin</option>
          </select>
        </div>

        <div class="md:col-span-2 flex items-center justify-end gap-3 pt-2">
          <BaseButton variant="secondary" @click="resetCreateForm">Reset</BaseButton>
          <BaseButton type="submit" variant="success" :loading="saving">Create User</BaseButton>
        </div>
      </form>
    </BaseModal>

    <!-- Filters -->
    <div class="grid items-end gap-4 rounded-2xl border border-white/50 bg-white/80 p-5 shadow-sm backdrop-blur md:grid-cols-2 lg:grid-cols-[2fr_1fr_1fr_auto]">
      <div class="flex flex-col gap-2">
        <label class="text-sm font-semibold text-gray-700">
          Search
        </label>
        <input
          v-model="searchFilter"
          type="text"
          class="rounded-lg border border-gray-300 px-3 py-2.5 text-sm outline-none transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
          placeholder="Search by name, email, or phone"
        />
      </div>

      <div class="flex flex-col gap-2">
        <label class="text-sm font-semibold text-gray-700">
          Role
        </label>
        <select
          v-model="roleFilter"
          class="rounded-lg border border-gray-300 px-3 py-2.5 text-sm outline-none transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
        >
          <option value="all">All Roles</option>
          <option value="Admins">Admins</option>
          <option value="Receptionists">Receptionists</option>
          <option value="Doctors">Doctors</option>
          <option value="Patients">Patients</option>
        </select>
      </div>

      <div class="flex flex-col gap-2">
        <label class="text-sm font-semibold text-gray-700">
          Status
        </label>
        <select
          v-model="statusFilter"
          class="rounded-lg border border-gray-300 px-3 py-2.5 text-sm outline-none transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
        >
          <option value="all">All Statuses</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>

      <div class="flex gap-2">
        <BaseButton variant="primary" :loading="loading" @click="loadUsers">Refresh</BaseButton>

        <BaseButton variant="success" @click="showCreateForm = true">Add User</BaseButton>
      </div>
    </div>

    <!-- Table -->
    <div class="overflow-hidden rounded-2xl border border-white/50 bg-white/80 shadow-sm backdrop-blur">
      <div class="flex items-center justify-between border-b border-gray-200 px-6 py-5">
        <h3 class="text-lg font-bold text-gray-900">
          Users List
        </h3>
        <span class="rounded-full bg-blue-100 px-3 py-1 text-sm font-semibold text-blue-700">
          {{ filteredUsers.length }} user(s)
        </span>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="p-6">
        <SkeletonCard type="row" :count="3" />
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredUsers.length === 0" class="p-6">
        <EmptyState 
          icon="🔍"
          title="No users found"
          description="Try adjusting your search filters or create a new user."
          actionLabel="Create New User"
          @action="showCreateForm = true"
        />
      </div>

      <!-- Table -->
      <div v-else>
        <BaseTable :items="paginatedUsers" :loading="loading" title="Users List" table-class="min-w-[950px]">
          <template #thead>
            <th class="px-6 py-4 font-bold text-gray-700">User</th>
            <th class="px-6 py-4 font-bold text-gray-700">Phone</th>
            <th class="px-6 py-4 font-bold text-gray-700">Role</th>
            <th class="px-6 py-4 font-bold text-gray-700">Status</th>
            <th class="w-52 px-6 py-4 font-bold text-gray-700">Actions</th>
          </template>

          <template #tbody="{ items }">
            <tr
              v-for="(user, index) in items"
              :key="user.id"
              class="group border-b border-gray-100 transition-all duration-200 hover:bg-blue-50/50"
              :style="{ animationDelay: `${index * 50}ms` }"
            >
              <template v-if="editUserId === user.id">
                <td class="px-6 py-4">
                  <div class="space-y-2">
                    <input v-model="editForm.first_name" type="text" class="w-full rounded-lg border border-blue-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-100" placeholder="First name" />
                    <input v-model="editForm.last_name" type="text" class="w-full rounded-lg border border-blue-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-100" placeholder="Last name" />
                    <input v-model="editForm.email" type="email" class="w-full rounded-lg border border-blue-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-100" placeholder="Email" />
                  </div>
                </td>

                <td class="px-6 py-4">
                  <input v-model="editForm.phone" type="text" class="rounded-lg border border-blue-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-100" placeholder="Phone" />
                </td>

                <td class="px-6 py-4">
                  <span class="inline-flex rounded-full px-3 py-1 text-sm font-semibold" :class="getRoleBadgeClass(user)">{{ getPrimaryRoleOfUser(user) }}</span>
                </td>

                <td class="px-6 py-4">
                  <StatusBadge :status="user.is_active ? 'active' : 'inactive'" />
                </td>

                <td class="px-6 py-4">
                  <div class="flex gap-2">
                    <BaseButton size="sm" variant="primary" :loading="saving" @click="submitEditUser(user)">Save</BaseButton>
                    <BaseButton size="sm" variant="secondary" @click="cancelEdit">Cancel</BaseButton>
                  </div>
                </td>
              </template>

              <template v-else>
                <td class="px-6 py-4">
                  <div class="flex flex-col gap-1">
                    <strong class="font-bold text-gray-900">{{ formatName(user) }}</strong>
                    <span class="text-sm text-gray-600">{{ user.email }}</span>
                  </div>
                </td>

                <td class="px-6 py-4 text-gray-700">{{ user.phone || "—" }}</td>

                <td class="px-6 py-4">
                  <span class="inline-flex items-center rounded-full px-3 py-1 text-xs font-bold" :class="getRoleBadgeClass(user)">{{ getPrimaryRoleOfUser(user) }}</span>
                </td>

                <td class="px-6 py-4">
                  <span class="inline-flex items-center rounded-full px-3 py-1 text-xs font-bold" :class="getStatusBadgeClass(user)">{{ user.is_active ? "Active" : "Inactive" }}</span>
                </td>

                <td class="px-6 py-4">
                  <div class="flex gap-2">
                    <BaseButton size="sm" variant="primary" @click="startEdit(user)">Edit</BaseButton>
                    <BaseButton size="sm" variant="danger" :loading="deletingId === user.id" :disabled="user.id === currentUser.id" @click="handleDeleteUser(user)">Delete</BaseButton>
                  </div>
                </td>
              </template>
            </tr>
          </template>

          <template #pagination>
            <BasePagination v-if="filteredUsers.length > 0" v-model:currentPage="currentPage" :items-per-page="itemsPerPage" :total-items="filteredUsers.length" />
          </template>
        </BaseTable>
      </div>

    </div>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: all 0.25s ease;
}

.toast-slide-enter-from,
.toast-slide-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
