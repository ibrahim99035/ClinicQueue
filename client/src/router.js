import { createRouter, createWebHistory } from 'vue-router'
import ConsultationCreate from './views/emr/ConsultationCreate.vue'
import ConsultationDetails from './views/emr/ConsultationDetails.vue'
import ConsultationEdit from './views/emr/ConsultationEdit.vue'

const routes = [
  {
    path: '/emr/appointments/:appointmentId/consultation/create',
    name: 'ConsultationCreate',
    component: ConsultationCreate
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
})

export default router
