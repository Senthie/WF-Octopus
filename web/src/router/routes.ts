import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/PortalLayout.vue'),
    children: [
      { path: '', component: () => import('pages/portal/LoginPage.vue') },
      { path: 'main', component: () => import('pages/portal/IndexPage.vue') },
    ],
  },
  {
    path: '/inspection',
    component: () => import('layouts/InspectionLayout.vue'),
    children: [
      { path: '', component: () => import('pages/inspection/ListPage.vue') },
      { path: 'record', component: () => import('pages/inspection/RecordPage.vue') },
      { path: 'requirement', component: () => import('pages/inspection/RequirementPage.vue') },
    ],
  },
  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;
