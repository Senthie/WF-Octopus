<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import { useUserStore } from "src/stores/user-store"
import { Notify } from "quasar"

const router = useRouter()
const userStore = useUserStore()

// 用户信息
const userName = computed(() => userStore.user?.name || "访客用户")
const userAvatar = computed(() => userStore.user?.avatar_url || "")

// 当前日期时间
const currentDateTime = ref("")
const updateDateTime = () => {
  const now = new Date()
  const yyyy = now.getFullYear()
  const mm = String(now.getMonth() + 1).padStart(2, "0")
  const dd = String(now.getDate()).padStart(2, "0")
  const hh = String(now.getHours()).padStart(2, "0")
  const min = String(now.getMinutes()).padStart(2, "0")
  currentDateTime.value = `${yyyy}.${mm}.${dd} ${hh}:${min}`
}
onMounted(() => {
  updateDateTime()
  setInterval(updateDateTime, 60000)
})

// 统计卡片数据 (模拟数据，后续可对接真实API)
const statsCards = ref([
  {
    title: "巡检任务",
    value: 128,
    icon: "assignment",
    color: "primary",
    trend: "+12%",
  },
  {
    title: "设备总数",
    value: 342,
    icon: "devices",
    color: "secondary",
    trend: "+5%",
  },
  {
    title: "完成率",
    value: "94%",
    icon: "check_circle",
    color: "positive",
    trend: "+8%",
  },
  {
    title: "异常告警",
    value: 7,
    icon: "warning",
    color: "negative",
    trend: "-2%",
  },
])

// 功能模块列表 (未来可扩展)
const featureModules = ref([
  {
    title: "巡检管理",
    desc: "执行日常巡检任务",
    icon: "fact_check",
    route: "/inspection/",
    color: "primary",
    enabled: true,
  },
  {
    title: "ERP数据展示",
    desc: "ERP提取数据展示",
    icon: "analytics",
    route: "/erp",
    color: "warning",
    enabled: true,
  },
  {
    title: "设备监控",
    desc: "实时查看设备状态",
    icon: "monitor_heart",
    route: "/monitor",
    color: "info",
    enabled: false,
  },
  {
    title: "数据分析",
    desc: "巡检报告与统计",
    icon: "analytics",
    route: "/reports",
    color: "warning",
    enabled: false,
  },
  {
    title: "工单系统",
    desc: "处理异常报修",
    icon: "support_agent",
    route: "/workorders",
    color: "secondary",
    enabled: false,
  },
  {
    title: "系统设置",
    desc: "权限与配置管理",
    icon: "settings",
    route: "/settings",
    color: "grey-8",
    enabled: false,
  },
])

// 最近活动 (模拟数据)
const recentActivities = ref([
  {
    id: 1,
    action: "完成巡检任务",
    location: "A区配电房",
    time: "10分钟前",
    status: "success",
  },
  {
    id: 2,
    action: "发现设备异常",
    location: "B区水泵房",
    time: "1小时前",
    status: "warning",
  },
  {
    id: 3,
    action: "新建巡检计划",
    location: "C区空调机组",
    time: "3小时前",
    status: "info",
  },
  {
    id: 4,
    action: "导出巡检报告",
    location: "系统",
    time: "昨天",
    status: "success",
  },
])

// 功能卡片点击处理
const handleModuleClick = (module: any) => {
  if (module.enabled) {
    router.push(module.route)
  } else {
    Notify.create({
      message: `${module.title} 功能开发中，敬请期待！`,
      color: "info",
      position: "top",
      icon: "build",
      timeout: 2000,
    })
  }
}

// 退出登录
const logout = () => {
  // 调用 store 的登出方法（需确保 userStore 中有 logout 逻辑）
  userStore.logout?.()
  // 清除本地存储的 token 等（备用方案）
  localStorage.removeItem("token")
  localStorage.removeItem("user-info")
  Notify.create({
    message: "已安全退出登录",
    color: "positive",
    position: "top",
    icon: "logout",
    timeout: 1500,
  })
  router.push("/login")
}

// 跳转到个人资料（示例）
const goToProfile = () => {
  Notify.create({ message: "个人资料页面开发中", color: "info" })
}
</script>

<template>
  <div class="dashboard-container">
    <!-- 顶部导航栏 -->
    <div class="app-header">
      <div class="header-left">
        <div class="logo-area">
          <q-icon name="auto_stories" size="32px" class="logo-icon" />
          <span class="logo-text">OCTOPUS 平台</span>
        </div>
      </div>
      <div class="header-right">
        <div class="datetime">{{ currentDateTime }}</div>
        <q-btn-dropdown
          flat
          round
          color="dark"
          :label="userName"
          :icon="userAvatar ? '' : 'account_circle'"
          no-caps
        >
          <q-list>
            <q-item clickable v-close-popup @click="goToProfile">
              <q-item-section avatar><q-icon name="person" /></q-item-section>
              <q-item-section>个人资料</q-item-section>
            </q-item>
            <q-item clickable v-close-popup @click="logout">
              <q-item-section avatar><q-icon name="logout" /></q-item-section>
              <q-item-section>退出登录</q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
      </div>
    </div>

    <!-- 主要内容区 -->
    <div class="main-content">
      <!-- 欢迎横幅 -->
      <div class="welcome-banner">
        <div class="welcome-text">
          <h2>欢迎回来，{{ userName }} 👋</h2>
          <p>今日巡检任务已就绪，请开始您的工作</p>
        </div>
        <div class="banner-decoration">
          <q-icon name="engineering" size="64px" color="white" opacity="0.2" />
        </div>
      </div>

      <!-- 统计卡片区 -->
      <div class="stats-grid">
        <q-card
          v-for="(stat, idx) in statsCards"
          :key="idx"
          class="stat-card"
          flat
          bordered
        >
          <q-card-section class="stat-content">
            <div class="stat-info">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">{{ stat.value }}</div>
              <div
                class="stat-trend"
                :class="stat.trend.includes('+') ? 'trend-up' : 'trend-down'"
              >
                <q-icon
                  :name="
                    stat.trend.includes('+') ? 'arrow_upward' : 'arrow_downward'
                  "
                  size="16px"
                />
                {{ stat.trend }}
              </div>
            </div>
            <q-avatar
              :color="stat.color"
              text-color="white"
              size="56px"
              class="stat-icon"
            >
              <q-icon :name="stat.icon" size="32px" />
            </q-avatar>
          </q-card-section>
        </q-card>
      </div>

      <!-- 功能模块网格 -->
      <div class="section-title">
        <span class="title-text">快速功能</span>
        <q-icon name="apps" color="primary" />
      </div>
      <div class="features-grid">
        <q-card
          v-for="(module, idx) in featureModules"
          :key="idx"
          class="feature-card"
          :class="{ 'card-disabled': !module.enabled }"
          flat
          bordered
          @click="handleModuleClick(module)"
        >
          <q-card-section class="feature-content">
            <q-avatar
              :color="module.enabled ? module.color : 'grey-5'"
              text-color="white"
              size="48px"
              class="feature-icon"
            >
              <q-icon :name="module.icon" size="28px" />
            </q-avatar>
            <div class="feature-info">
              <div class="feature-title">{{ module.title }}</div>
              <div class="feature-desc">{{ module.desc }}</div>
            </div>
            <q-icon
              name="chevron_right"
              size="24px"
              class="feature-arrow"
              :class="{ 'arrow-disabled': !module.enabled }"
            />
          </q-card-section>
        </q-card>
      </div>

      <!-- 最近活动 & 快捷操作 双栏布局 -->
      <div class="row q-col-gutter-md">
        <div class="col-12 col-md-7">
          <div class="section-title">
            <span class="title-text">最近活动</span>
            <q-icon name="history" color="primary" />
          </div>
          <q-card flat bordered class="activity-card">
            <q-list separator>
              <q-item
                v-for="activity in recentActivities"
                :key="activity.id"
                class="activity-item"
              >
                <q-item-section avatar>
                  <q-icon
                    :name="
                      activity.status === 'success'
                        ? 'check_circle'
                        : activity.status === 'warning'
                          ? 'error'
                          : 'info'
                    "
                    :color="
                      activity.status === 'success'
                        ? 'positive'
                        : activity.status === 'warning'
                          ? 'warning'
                          : 'primary'
                    "
                    size="28px"
                  />
                </q-item-section>
                <q-item-section>
                  <q-item-label lines="1">{{ activity.action }}</q-item-label>
                  <q-item-label caption>{{ activity.location }}</q-item-label>
                </q-item-section>
                <q-item-section side>{{ activity.time }}</q-item-section>
              </q-item>
            </q-list>
            <q-separator />
            <q-card-actions align="right" class="activity-more">
              <q-btn
                flat
                color="primary"
                label="查看全部"
                @click="
                  Notify.create({
                    message: '全部活动页面开发中',
                    color: 'info',
                  })
                "
              />
            </q-card-actions>
          </q-card>
        </div>
        <div class="col-12 col-md-5">
          <div class="section-title">
            <span class="title-text">快捷工具</span>
            <q-icon name="bolt" color="primary" />
          </div>
          <q-card flat bordered class="quick-tools-card">
            <q-card-section>
              <div class="tools-grid">
                <div
                  class="tool-item"
                  @click="handleModuleClick(featureModules[0])"
                >
                  <q-icon name="fact_check" size="32px" color="primary" />
                  <span>开始巡检</span>
                </div>
                <div
                  class="tool-item"
                  @click="
                    Notify.create({
                      message: '生成周报功能开发中',
                      color: 'info',
                    })
                  "
                >
                  <q-icon name="description" size="32px" color="secondary" />
                  <span>生成周报</span>
                </div>
                <div
                  class="tool-item"
                  @click="
                    Notify.create({
                      message: '扫码巡检功能开发中',
                      color: 'info',
                    })
                  "
                >
                  <q-icon name="qr_code_scanner" size="32px" color="warning" />
                  <span>扫码巡检</span>
                </div>
                <div
                  class="tool-item"
                  @click="
                    Notify.create({
                      message: '一键报修功能开发中',
                      color: 'info',
                    })
                  "
                >
                  <q-icon name="build" size="32px" color="negative" />
                  <span>一键报修</span>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.dashboard-container {
  min-height: 100vh;
  background: #f5f7fb;
  font-family:
    "Inter",
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    Roboto,
    Helvetica,
    Arial,
    sans-serif;
}

/* 顶部导航栏 */
.app-header {
  background: white;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  padding: 0 32px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;

  .logo-icon {
    color: #4f46e5;
  }

  .logo-text {
    font-size: 20px;
    font-weight: 600;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;

  .datetime {
    color: #6b7280;
    font-size: 14px;
    font-weight: 500;
  }
}

/* 主要内容区 */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 28px 32px;
}

/* 欢迎横幅 */
.welcome-banner {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  border-radius: 28px;
  padding: 28px 32px;
  margin-bottom: 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
  box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.2);

  .welcome-text {
    h2 {
      font-size: 26px;
      font-weight: 700;
      margin: 0 0 8px 0;
    }
    p {
      font-size: 14px;
      opacity: 0.9;
      margin: 0;
    }
  }
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  border-radius: 24px;
  transition: all 0.25s ease;
  cursor: default;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 25px -12px rgba(0, 0, 0, 0.1);
  }
}

.stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
}

.stat-info {
  .stat-title {
    font-size: 14px;
    color: #6b7280;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
  }
  .stat-value {
    font-size: 32px;
    font-weight: 700;
    color: #1f2937;
    line-height: 1.2;
    margin-bottom: 8px;
  }
  .stat-trend {
    font-size: 12px;
    display: inline-flex;
    align-items: center;
    gap: 2px;
    background: #f3f4f6;
    padding: 2px 8px;
    border-radius: 20px;
  }
  .trend-up {
    color: #10b981;
  }
  .trend-down {
    color: #ef4444;
  }
}

.stat-icon {
  background: linear-gradient(135deg, #eef2ff, #e0e7ff);
  color: #4f46e5;
}

/* 功能模块网格 */
.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 24px 0 18px 0;

  .title-text {
    font-size: 18px;
    font-weight: 600;
    color: #1f2937;
    position: relative;
    padding-left: 12px;

    &::before {
      content: "";
      position: absolute;
      left: 0;
      top: 50%;
      transform: translateY(-50%);
      width: 4px;
      height: 20px;
      background: #4f46e5;
      border-radius: 2px;
    }
  }
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.feature-card {
  border-radius: 20px;
  transition: all 0.2s;
  cursor: pointer;

  &:hover:not(.card-disabled) {
    transform: translateY(-3px);
    box-shadow: 0 12px 20px -8px rgba(0, 0, 0, 0.12);
    border-color: transparent;
  }

  &.card-disabled {
    opacity: 0.6;
    cursor: not-allowed;
    filter: grayscale(0.1);
  }
}

.feature-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.feature-info {
  flex: 1;
  .feature-title {
    font-weight: 600;
    font-size: 16px;
    color: #1f2937;
    margin-bottom: 4px;
  }
  .feature-desc {
    font-size: 13px;
    color: #6b7280;
  }
}

.feature-arrow {
  color: #9ca3af;
  transition: transform 0.2s;
}

.feature-card:hover:not(.card-disabled) .feature-arrow {
  transform: translateX(4px);
  color: #4f46e5;
}

.arrow-disabled {
  opacity: 0.4;
}

/* 最近活动卡片 */
.activity-card {
  border-radius: 24px;
  overflow: hidden;
}

.activity-item {
  padding: 12px 16px;
}

.activity-more {
  padding: 8px 12px;
}

/* 快捷工具卡片 */
.quick-tools-card {
  border-radius: 24px;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  padding: 8px 0;

  .tool-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: 18px 12px;
    background: #f9fafb;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.2s;

    span {
      font-size: 13px;
      font-weight: 500;
      color: #374151;
    }

    &:hover {
      background: #eef2ff;
      transform: translateY(-2px);
    }
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .app-header {
    padding: 0 16px;
    height: 60px;
  }
  .main-content {
    padding: 20px 16px;
  }
  .welcome-banner .welcome-text h2 {
    font-size: 20px;
  }
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  .features-grid {
    grid-template-columns: 1fr;
  }
  .tools-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
