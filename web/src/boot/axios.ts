import { defineBoot } from '#q-app/wrappers'
import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from 'axios'
import { TokenManager } from 'src/utils/tokenManager'

declare module 'vue' {
  interface ComponentCustomProperties {
    $axios: AxiosInstance
    $api: AxiosInstance
  }
}

const baseURL = import.meta.env.VITE_API_WF_URL || '/api'

const api = axios.create({ baseURL })

// ---------- 请求拦截器：动态添加 token ----------
api.interceptors.request.use(
  (config) => {
    const token = TokenManager.getAccessToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ---------- 响应拦截器：处理 token 过期 + 请求锁 ----------
interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

// 等待队列中的请求结构
interface PendingRequest {
  resolve: (value: any) => void
  reject: (reason?: any) => void
  config: CustomAxiosRequestConfig
}

let isRefreshing = false
let pendingRequests: PendingRequest[] = []

// 刷新成功：用新 token 重试所有等待的请求
function onRefreshed(token: string) {
  pendingRequests.forEach(({ resolve, config }) => {
    config.headers.Authorization = `Bearer ${token}`
    resolve(api(config))
  })
  pendingRequests = []
}

// 刷新失败：拒绝所有等待的请求
function onRefreshFailed(error: any) {
  pendingRequests.forEach(({ reject }) => reject(error))
  pendingRequests = []
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as CustomAxiosRequestConfig
    // 只处理 401 且未重试过的请求
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = TokenManager.getRefreshToken()
      if (!refreshToken) {
        TokenManager.clearTokens()
        window.location.href = '/login'
        return Promise.reject(error)
      }

      if (!isRefreshing) {
        isRefreshing = true
        try {
          const refreshResponse = await axios.post(`${baseURL}/v1/auth/refresh`, {
            refresh_token: refreshToken,
          })
          const { access_token, refresh_token, expires_in } = refreshResponse.data.data
          TokenManager.updateTokens(access_token, refresh_token, expires_in)

          onRefreshed(access_token)

          // 重试当前请求
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        } catch (refreshError) {
          TokenManager.clearTokens()
          onRefreshFailed(refreshError)
          window.location.href = '/login'
          return Promise.reject(refreshError)
        } finally {
          isRefreshing = false
        }
      } else {
        // 已有刷新任务正在进行，将当前请求加入队列
        return new Promise((resolve, reject) => {
          pendingRequests.push({ resolve, reject, config: originalRequest })
        })
      }
    }
    return Promise.reject(error)
  }
)

export default defineBoot(({ app }) => {
  app.config.globalProperties.$axios = axios
  app.config.globalProperties.$api = api
})

export { api }