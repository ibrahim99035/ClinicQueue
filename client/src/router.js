import { createRouter, createWebHistory } from "vue-router";

import Login from "./views/auth/Login.vue";
import AdminLayout from "./layouts/AdminLayout.vue";
import AdminHome from "./views/admin/AdminHome.vue";
import AdminUsers from "./views/admin/AdminUsers.vue";
import PendingDoctors from "./views/admin/PendingDoctors.vue";
import AdminScheduling from "./views/admin/AdminScheduling.vue";
import AdminAppointments from "./views/admin/AdminAppointments.vue";
import AdminAnalytics from "./views/admin/AdminAnalytics.vue";

import ConsultationCreate from "./views/emr/ConsultationCreate.vue";
import ConsultationDetails from "./views/emr/ConsultationDetails.vue";
import ConsultationEdit from "./views/emr/ConsultationEdit.vue";

import {
  getAccessToken,
  clearAuthData,
  hasAnyRole,
  getDefaultRouteByRole,
} from "./api/auth";

const routes = [
  {
    path: "/",
    redirect: "/login",
  },
  {
    path: "/login",
    name: "Login",
    component: Login,
    meta: {
      guestOnly: true,
    },
  },

  //Admin routes
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

  //EMR routes
  {
    path: "/emr/appointments/:appointmentId/consultation/create",
    name: "ConsultationCreate",
    component: ConsultationCreate,
    meta: {
      requiresAuth: true,
      roles: ["Doctors"],
    },
  },
  {
    path: "/emr/appointments/:appointmentId/consultation",
    name: "ConsultationDetails",
    component: ConsultationDetails,
    meta: {
      requiresAuth: true,
      roles: ["Doctors", "Patients"],
    },
  },
  {
    path: "/emr/consultations/:consultationId/edit",
    name: "ConsultationEdit",
    component: ConsultationEdit,
    meta: {
      requiresAuth: true,
      roles: ["Doctors"],
    },
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/login",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const accessToken = getAccessToken();

  const isGuestOnlyRoute = to.meta.guestOnly === true;
  const requiresAuth = to.meta.requiresAuth === true;

  let allowedRoles = [];

  if (to.meta.roles) {
    allowedRoles = to.meta.roles;
  }

  if (isGuestOnlyRoute && accessToken) {
    const defaultRoute = getDefaultRouteByRole();

    next(defaultRoute);
    return;
  }

  if (requiresAuth && !accessToken) {
    clearAuthData();

    next("/login");
    return;
  }

  if (requiresAuth && allowedRoles.length > 0) {
    const userCanEnterThisRoute = hasAnyRole(allowedRoles);

    if (!userCanEnterThisRoute) {
      const defaultRoute = getDefaultRouteByRole();

      if (defaultRoute === "/login") {
        clearAuthData();

        next("/login");
        return;
      }

      next(defaultRoute);
      return;
    }
  }

  next();
});
export default router
