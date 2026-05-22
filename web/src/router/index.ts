import { defineRouter } from '#q-app/wrappers';
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from 'vue-router';
import routes from './routes';
import { useUserStore } from 'src/stores/user-store'; // 导入你的 user store

export default defineRouter(function ({ store }) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : (process.env.VUE_ROUTER_MODE === 'history' ? createWebHistory : createWebHashHistory);

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,
    history: createHistory(process.env.VUE_ROUTER_BASE),
  });

  // 全局前置守卫：检查认证状态
  Router.beforeEach(async (to, from, next) => {
    // 获取 user store 实例（使用传入的 store 参数）
    const userStore = useUserStore(store);

    // 白名单：不需要登录就可以访问的路由
    const whiteList = ['/login']; // 可以继续添加 '/register' 等

    if (whiteList.includes(to.path)) {
      // 在白名单内，直接放行
      next();
      return;
    }

    // 检查是否已认证
    if (userStore.isAuthenticated) {
      // 认证通过，继续
      next();
    } else {
      // 未认证：尝试刷新 token（如果存在 refresh token）
      const refreshed = await userStore.refreshTokenIfNeeded();
      if (refreshed) {
        // 刷新成功，放行
        next();
      } else {
        // 刷新失败或无 token，跳转到登录页
        // 携带原本要访问的路径，方便登录后跳回（可选）
        next({ path: '/login', query: { redirect: to.fullPath } });
      }
    }
  });

  return Router;
});