<!--
 * @Author: Senthie seemoon2077@gmail.com
 * @Date: 2026-01-06 11:20:16
 * @LastEditors: Senthie seemoon2077@gmail.com
 * @LastEditTime: 2026-01-06 17:58:22
 * @FilePath: /web/src/pages/LoginPage.vue
 * @Description: 登录页面 - 现代化设计版本
 *
 * Copyright (c) 2026 by Senthie email: seemoon2077@gmail.com, All Rights Reserved.
-->

<script setup lang="ts">
import { Notify } from "quasar"
import type { user_login_schema, ILogin } from "src/interfaces/IAuth"
import { useUserStore } from "src/stores/user-store"
import { ref } from "vue"
import { useRouter } from "vue-router"

const user_store = useUserStore()
const router = useRouter()
const loading = ref(false)
const isPwd = ref(true)
const rememberMe = ref(false)
const formRef = ref<any>(null)

const login = ref<ILogin>({
  email: "",
  password: "",
})

// 表单验证规则
const emailRules = [
  (val: string) => !!val || "邮箱地址不能为空",
  (val: string) => /^\S+@\S+\.\S+$/.test(val) || "请输入有效的邮箱地址",
]

const passwordRules = [
  (val: string) => !!val || "密码不能为空",
  (val: string) => (val && val.length >= 6) || "密码长度至少为6位",
]

const loginHandle = async () => {
  // 表单验证
  const isValid = await formRef.value?.validate()
  if (!isValid) return

  loading.value = true
  try {
    const res = await user_store.login(login.value)
    if (res.code == 200) {
      Notify.create({
        message: `登录成功，欢迎 ${res.data.user.name} 回来！`,
        color: "positive",
        position: "top",
        icon: "check_circle",
        timeout: 2000,
      })
      // 跳转到首页
      await router.push("/main")
    } else {
      Notify.create({
        message: res.msg || "登录失败，请检查邮箱或密码",
        color: "negative",
        position: "top",
        icon: "error",
        timeout: 3000,
      })
    }
  } catch (error: any) {
    Notify.create({
      message: error?.message || "网络错误，请稍后重试",
      color: "negative",
      position: "top",
      icon: "error",
      timeout: 3000,
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <q-card class="login-card" flat :bordered="false">
      <div class="card-content">
        <!-- Logo / 品牌区域 -->
        <div class="brand-section">
          <div class="logo-wrapper">
            <q-icon name="auto_stories" size="48px" class="logo-icon" />
          </div>
          <h1 class="brand-title">Welcome OCTOPUS</h1>
          <p class="brand-subtitle">请登录您的账户继续探索</p>
        </div>

        <!-- 登录表单 -->
        <q-form ref="formRef" class="login-form" @submit="loginHandle">
          <q-input
            v-model="login.email"
            label="电子邮箱"
            outlined
            dense
            lazy-rules
            :rules="emailRules"
            class="form-input"
            placeholder="your@email.com"
          >
            <template v-slot:prepend>
              <q-icon name="email" color="primary" />
            </template>
          </q-input>

          <q-input
            v-model="login.password"
            :type="isPwd ? 'password' : 'text'"
            label="密码"
            outlined
            dense
            lazy-rules
            :rules="passwordRules"
            class="form-input"
            placeholder="请输入密码"
          >
            <template v-slot:prepend>
              <q-icon name="lock" color="primary" />
            </template>
            <template v-slot:append>
              <q-icon
                :name="isPwd ? 'visibility_off' : 'visibility'"
                class="cursor-pointer"
                @click="isPwd = !isPwd"
              />
            </template>
          </q-input>

          <div class="form-options">
            <q-checkbox
              v-model="rememberMe"
              label="记住我"
              color="primary"
              dense
            />
            <a
              href="#"
              class="forgot-link"
              @click.prevent="
                Notify.create({
                  message: '请联系管理员重置密码',
                  color: 'info',
                  position: 'top',
                })
              "
              >忘记密码？</a
            >
          </div>

          <q-btn
            label="登录"
            type="submit"
            color="primary"
            class="login-btn"
            :loading="loading"
            :disable="loading"
            no-caps
            rounded
          >
            <template v-slot:loading>
              <q-spinner-dots class="on-left" />
              登录中...
            </template>
          </q-btn>

          <div class="register-section">
            <span class="register-text">还没有账户？</span>
            <a
              href="#"
              class="register-link"
              @click.prevent="
                Notify.create({
                  message: '请联系管理员注册',
                  color: 'info',
                  position: 'top',
                })
              "
              >立即注册</a
            >
          </div>
        </q-form>

        <!-- 装饰分割线 -->
        <div class="divider-wrapper">
          <div class="divider-line"></div>
          <span class="divider-text">安全加密登录</span>
          <div class="divider-line"></div>
        </div>

        <!-- 其他登录方式 -->
        <div class="social-login">
          <q-btn
            round
            flat
            icon="fab fa-github"
            class="social-btn"
            @click="
              Notify.create({ message: '第三方登录功能开发中', color: 'info' })
            "
          />
          <q-btn
            round
            flat
            icon="fab fa-google"
            class="social-btn"
            @click="
              Notify.create({ message: '第三方登录功能开发中', color: 'info' })
            "
          />
          <q-btn
            round
            flat
            icon="fab fa-weixin"
            class="social-btn"
            @click="
              Notify.create({ message: '第三方登录功能开发中', color: 'info' })
            "
          />
        </div>
      </div>
    </q-card>
  </div>
</template>

<style lang="scss" scoped>
.login-container {
  min-height: 100vh;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  overflow: hidden;
}

/* 背景装饰元素 */
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 20s infinite ease-in-out;
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -150px;
  right: -150px;
  animation-delay: 0s;
}

.circle-2 {
  width: 200px;
  height: 200px;
  bottom: -100px;
  left: -100px;
  animation-delay: 5s;
  background: rgba(255, 255, 255, 0.08);
}

.circle-3 {
  width: 150px;
  height: 150px;
  top: 40%;
  left: 20%;
  animation-delay: 10s;
  background: rgba(255, 255, 255, 0.05);
}

@keyframes float {
  0% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(5deg);
  }
  100% {
    transform: translateY(0) rotate(0deg);
  }
}

/* 登录卡片 */
.login-card {
  width: 100%;
  max-width: 480px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 32px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
  z-index: 1;
  overflow: hidden;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 35px 60px -15px rgba(0, 0, 0, 0.3);
  }
}

.card-content {
  padding: 48px 40px;
}

/* 品牌区域 */
.brand-section {
  text-align: center;
  margin-bottom: 32px;
}

.logo-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin-bottom: 20px;
  box-shadow: 0 10px 20px -5px rgba(102, 126, 234, 0.4);
}

.logo-icon {
  color: white;
}

.brand-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 8px 0;
}

.brand-subtitle {
  color: #666;
  font-size: 14px;
  margin: 0;
}

/* 表单样式 */
.login-form {
  margin-bottom: 24px;
}

.form-input {
  margin-bottom: 20px;

  :deep(.q-field__control) {
    border-radius: 12px;
    transition: all 0.2s ease;
  }

  :deep(.q-field__control:focus-within) {
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
  }

  :deep(.q-field__label) {
    font-size: 14px;
  }
}

/* 表单选项 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;

  :deep(.q-checkbox) {
    font-size: 13px;
  }
}

.forgot-link {
  color: #667eea;
  text-decoration: none;
  font-size: 13px;
  transition: color 0.2s;

  &:hover {
    color: #764ba2;
    text-decoration: underline;
  }
}

/* 登录按钮 */
.login-btn {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transition:
    transform 0.2s,
    box-shadow 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px -5px rgba(102, 126, 234, 0.5);
  }

  &:active {
    transform: translateY(0);
  }
}

/* 注册区域 */
.register-section {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
}

.register-text {
  color: #666;
}

.register-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  margin-left: 5px;
  transition: color 0.2s;

  &:hover {
    color: #764ba2;
    text-decoration: underline;
  }
}

/* 装饰分割线 */
.divider-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 28px 0 20px;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, #e0e0e0, transparent);
}

.divider-text {
  padding: 0 16px;
  font-size: 12px;
  color: #999;
  letter-spacing: 1px;
}

/* 社交登录 */
.social-login {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 8px;
}

.social-btn {
  width: 44px;
  height: 44px;
  background: rgba(0, 0, 0, 0.03);
  transition: all 0.2s;
  color: #666;

  &:hover {
    background: rgba(102, 126, 234, 0.1);
    color: #667eea;
    transform: translateY(-2px);
  }
}

/* 响应式调整 */
@media (max-width: 600px) {
  .card-content {
    padding: 32px 24px;
  }

  .brand-title {
    font-size: 24px;
  }

  .logo-wrapper {
    width: 64px;
    height: 64px;

    .logo-icon {
      font-size: 36px;
    }
  }

  .social-btn {
    width: 40px;
    height: 40px;
  }
}
</style>
