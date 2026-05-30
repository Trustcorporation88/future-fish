import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Process from '../views/MainView.vue'
import SimulationView from '../views/SimulationView.vue'
import SimulationRunView from '../views/SimulationRunView.vue'
import ReportView from '../views/ReportView.vue'
import InteractionView from '../views/InteractionView.vue'
import FutureFishHome from '../views/FutureFishHome.vue'
import FutureFishInput from '../views/FutureFishInput.vue'
import FutureFishResult from '../views/FutureFishResult.vue'

const routes = [
  {
    path: '/',
    redirect: '/future-fish'
  },
  {
    path: '/future-fish',
    name: 'FutureFishHome',
    component: FutureFishHome
  },
  {
    path: '/future-fish/input',
    name: 'FutureFishInput',
    component: FutureFishInput
  },
  {
    path: '/future-fish/result/:forecastId',
    name: 'FutureFishResult',
    component: FutureFishResult,
    props: true
  },
  {
    path: '/legacy',
    name: 'Home',
    component: Home
  },
  {
    path: '/process/:projectId',
    name: 'Process',
    component: Process,
    props: true
  },
  {
    path: '/simulation/:simulationId',
    name: 'Simulation',
    component: SimulationView,
    props: true
  },
  {
    path: '/simulation/:simulationId/start',
    name: 'SimulationRun',
    component: SimulationRunView,
    props: true
  },
  {
    path: '/report/:reportId',
    name: 'Report',
    component: ReportView,
    props: true
  },
  {
    path: '/interaction/:reportId',
    name: 'Interaction',
    component: InteractionView,
    props: true
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
