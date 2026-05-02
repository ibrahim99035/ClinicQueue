import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "./stores/auth";

// Auth
import Login from "./views/auth/Login.vue";
import Unauthorized from "./views/Unauthorized.vue";
import Register from "./views/auth/Register.vue";

// Patient
import PatientLayout from "./layouts/PatientLayout.vue";
import PatientDashboard from "./views/patient/PatientDashboard.vue";
import BookAppointment from "./views/patient/BookAppointment.vue";
import MyAppointments from "./views/patient/MyAppointments.vue";
import MyWaitingList from "./views/patient/MyWaitingList.vue";
import MyConsultations from "./views/patient/MyConsultations.vue";

// Doctor
import DoctorLayout from "./layouts/DoctorLayout.vue";
import DoctorDashboard from "./views/doctor/DoctorDashboard.vue";
import AppointmentQueue from "./views/doctor/AppointmentQueue.vue";
import MySchedule from "./views/doctor/MySchedule.vue";

// Receptionist
import ReceptionistLayout from "./layouts/ReceptionistLayout.vue";
import ReceptionDashboard from "./views/reception/ReceptionDashboard.vue";
import CheckInDesk from "./views/reception/CheckInDesk.vue";
import SlotGenerator from "./views/reception/SlotGenerator.vue";

// Admin
import AdminLayout from "./layouts/AdminLayout.vue";
import AdminHome from "./views/admin/AdminHome.vue";
import AdminUsers from "./views/admin/AdminUsers.vue";
import PendingDoctors from "./views/admin/PendingDoctors.vue";
import AdminScheduling from "./views/admin/AdminScheduling.vue";
import AdminAppointments from "./views/admin/AdminAppointments.vue";
import AdminAnalytics from "./views/admin/AdminAnalytics.vue";

// EMR
import ConsultationCreate from "./views/emr/ConsultationCreate.vue";
import ConsultationDetails from "./views/emr/ConsultationDetails.vue";
import ConsultationEdit from "./views/emr/ConsultationEdit.vue";

function getStoredRoles() {
  try {
    return JSON.parse(localStorage.getItem("roles")) || [];
  } catch {
    return [];
  }
}

const routes = [
  {
    path: "/",
    redirect: (to) => {
      const roles = getStoredRoles();

      if (roles.includes("Admins")) return "/admin";
      if (roles.includes("Doctors")) return "/doctor";
      if (roles.includes("Receptionists")) return "/reception";
      if (roles.includes("Patients")) return "/patient";
      return "/login";
    },
  },
  {
    path: "/login",
    name: "Login",
    component: Login,
    meta: { guest: true },
  },
  {
  path: "/register",
  name: "Register",
  component: Register,
  meta: {
    guest: true,
  },
},

  //Admin routes
  {
    path: "/unauthorized",
    name: "Unauthorized",
    component: Unauthorized,
  },

  // Patient Routes
  {
    path: "/patient",
    name: "PatientLayout",
    component: PatientLayout,
    meta: {
      requiresAuth: true,
      roles: ["Patients"],
    },
    children: [
      {
        path: "",
        name: "PatientDashboard",
        component: PatientDashboard,
      },
      {
        path: "book",
        name: "BookAppointment",
        component: BookAppointment,
      },
      {
        path: "appointments",
        name: "MyAppointments",
        component: MyAppointments,
      },
      {
        path: "waiting-list",
        name: "MyWaitingList",
        component: MyWaitingList,
      },
      {
        path: "consultations",
        name: "MyConsultations",
        component: MyConsultations,
      },
    ],
  },

  // Doctor Routes
  {
    path: "/doctor",
    name: "DoctorLayout",
    component: DoctorLayout,
    meta: {
      requiresAuth: true,
      roles: ["Doctors"],
    },
    children: [
      {
        path: "",
        name: "DoctorDashboard",
        component: DoctorDashboard,
      },
      {
        path: "queue",
        name: "AppointmentQueue",
        component: AppointmentQueue,
      },
      {
        path: "schedule",
        name: "MySchedule",
        component: MySchedule,
      },
    ],
  },

  // Receptionist Routes
  {
    path: "/reception",
    name: "ReceptionistLayout",
    component: ReceptionistLayout,
    meta: {
      requiresAuth: true,
      roles: ["Receptionists"],
    },
    children: [
      {
        path: "",
        name: "ReceptionDashboard",
        component: ReceptionDashboard,
      },
      {
        path: "check-in",
        name: "CheckInDesk",
        component: CheckInDesk,
      },
      {
        path: "slots",
        name: "SlotGenerator",
        component: SlotGenerator,
      },
    ],
  },

  // Admin Routes
  {
    path: "/admin",
    name: "AdminLayout",
    component: AdminLayout,
    meta: {
      requiresAuth: true,
      roles: ["Admins"],
    },
    children: [
      {
        path: "",
        name: "AdminHome",
        component: AdminHome,
      },
      {
        path: "users",
        name: "AdminUsers",
        component: AdminUsers,
      },
      {
        path: "pending-doctors",
        name: "PendingDoctors",
        component: PendingDoctors,
      },
      {
        path: "scheduling",
        name: "AdminScheduling",
        component: AdminScheduling,
      },
      {
        path: "appointments",
        name: "AdminAppointments",
        component: AdminAppointments,
      },
      {
        path: "analytics",
        name: "AdminAnalytics",
        component: AdminAnalytics,
      },
    ],
  },

  // EMR Routes
  {
    path: "/emr/appointments/:appointmentId/consultation/create",
    name: "ConsultationCreate",
    component: ConsultationCreate,
    meta: { requiresAuth: true },
  },
  {
    path: "/emr/appointments/:appointmentId/consultation",
    name: "ConsultationDetails",
    component: ConsultationDetails,
    meta: { requiresAuth: true },
  },
  {
    path: "/emr/consultations/:consultationId/edit",
    name: "ConsultationEdit",
    component: ConsultationEdit,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from) => {
  const accessToken = localStorage.getItem("access");
  const auth = useAuthStore();

  if (!auth.isAuthenticated && accessToken) {
    auth.access = accessToken;

    try {
      await auth.getMe();
    } catch (e) {
      // ignore
    }
  }

  const userRoles = getStoredRoles();

  if (to.meta && to.meta.requiresAuth && !accessToken) {
    return { path: "/login", query: { redirect: to.fullPath } };
  }

  if (to.meta && to.meta.roles) {
    const allowedRoles = to.meta.roles;
    const hasAllowedRole = allowedRoles.some((role) =>
      userRoles.includes(role)
    );

    if (!hasAllowedRole) {
      return { path: "/unauthorized" };
    }
  }

  if (to.meta && to.meta.guest && accessToken) {
    if (userRoles.includes("Admins")) return { path: "/admin" };
    if (userRoles.includes("Doctors")) return { path: "/doctor" };
    if (userRoles.includes("Receptionists")) return { path: "/reception" };
    if (userRoles.includes("Patients")) return { path: "/patient" };
  }

  return true;
});

export default router;
