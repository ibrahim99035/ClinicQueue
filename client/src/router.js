import { createRouter, createWebHistory } from "vue-router";

import Login from "./views/auth/Login.vue";
import AdminLayout from "./layouts/AdminLayout.vue";
import AdminHome from "./views/admin/AdminHome.vue";
import AdminUsers from "./views/admin/AdminUsers.vue";
import PendingDoctors from "./views/admin/PendingDoctors.vue";
import AdminScheduling from "./views/admin/AdminScheduling.vue";
import AdminAppointments from "./views/admin/AdminAppointments.vue";

import ConsultationCreate from "./views/emr/ConsultationCreate.vue";
import ConsultationDetails from "./views/emr/ConsultationDetails.vue";
import ConsultationEdit from "./views/emr/ConsultationEdit.vue";

import { isAdminUser, clearAuthData } from "./api/auth";

const routes = [
  {
    path: "/",
    redirect: "/login",
  },
  {
    path: "/login",
    name: "Login",
    component: Login,
  },
  {
    path: "/admin",
    name: "AdminLayout",
    component: AdminLayout,
    meta: {
      requireAdmin: true,
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
    ],
  },
  {
    path: "/emr/appointments/:appointmentId/consultation/create",
    name: "ConsultationCreate",
    component: ConsultationCreate,
  },
  {
    path: '/emr/appointments/:appointmentId/consultation',
    name: 'ConsultationDetails',
    component: ConsultationDetails
  },
  {
    path: '/emr/consultations/:consultationId/edit',
    name: 'ConsultationEdit',
    component: ConsultationEdit
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const accessToken =localStorage.getItem("access");
  const isAdminRoute = to.path.startsWith("/admin");

    if (isAdminRoute && (!accessToken || !isAdminUser())) {
    clearAuthData();
    next("/login");
    return;
  }

  if (to.path === "/login" && accessToken && isAdminUser()) {
    next("/admin");
    return;
  }


  next();
});
export default router
