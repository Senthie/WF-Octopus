<template>
  <q-page padding>
    <div class="erp-card">
      <!-- 头部区域 -->
      <div class="row items-center justify-between q-mb-md header-section">
        <div class="text-h5 text-weight-bold text-primary flex items-center">
          📘 客户报价需求
          <q-badge color="blue-2" text-color="primary" class="q-ml-sm">
            CPDL/CPLB…
          </q-badge>
        </div>
        <div class="row items-center q-gutter-sm">
          <q-btn
            outline
            color="primary"
            label="载入示例"
            icon="mdi-clipboard-text-outline"
            size="sm"
            @click="loadSampleData"
          />
          <q-btn
            color="primary"
            label="导入 JSON"
            icon="mdi-file-upload-outline"
            size="sm"
            @click="triggerFileInput"
          />
          <input
            ref="fileInput"
            type="file"
            accept=".json,application/json"
            style="display: none"
            @change="handleFileImport"
          />
        </div>
      </div>

      <!-- 表单区域，使用 q-form 包裹 -->
      <q-form @submit.prevent="handleSave" class="q-gutter-y-md">
        <!-- 第一行：只读任务信息 -->
        <div class="row q-col-gutter-md">
          <div class="col-12 col-sm-6">
            <q-input
              outlined
              dense
              readonly
              v-model="formData.id"
              label="任务ID"
              bg-color="grey-2"
            />
          </div>
          <div class="col-12 col-sm-6">
            <q-input
              outlined
              dense
              readonly
              v-model="formData.create_by"
              label="创建人"
              bg-color="grey-2"
            />
          </div>
        </div>

        <!-- 分组：产品大类 / 产品类别 / 书脊方向 / 装订方式 -->
        <q-separator spaced />
        <div class="text-subtitle2 text-grey-8">基础信息</div>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-sm-6 col-md-3">
            <q-input
              outlined
              dense
              v-model="formData.CPDL"
              label="产品大类 (CPDL)"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-select
              outlined
              dense
              v-model="formData.CPLB"
              :options="cplbOptions"
              label="产品类别 (CPLB)"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-input
              outlined
              dense
              v-model="formData.SJFX"
              label="书脊方向 (SJFX)"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-select
              outlined
              dense
              v-model="formData.ZDFS"
              :options="zdfsOptions"
              label="装订方式 (ZDFS)"
            />
          </div>
        </div>

        <!-- 分组：产品名称、款数、语言数、单位 -->
        <div class="row q-col-gutter-md">
          <div class="col-12 col-sm-6 col-md-3">
            <q-input
              outlined
              dense
              v-model="formData.CPMC"
              label="产品名称 (CPMC)"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-input
              outlined
              dense
              type="number"
              v-model.number="formData.TZS"
              label="款数 (TZS)"
              min="0"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-input
              outlined
              dense
              type="number"
              v-model.number="formData.YYS"
              label="语言数 (YYS)"
              min="0"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-select
              outlined
              dense
              v-model="formData.DWMC"
              :options="dwmcOptions"
              label="单位 (DWMC)"
            />
          </div>
        </div>

        <!-- 币种 / 目标价 / 规格 -->
        <div class="row q-col-gutter-md">
          <div class="col-12 col-sm-4">
            <q-select
              outlined
              dense
              v-model="formData.BZ"
              :options="bzOptions"
              label="客户币种 (BZ)"
            />
          </div>
          <div class="col-12 col-sm-4">
            <q-input
              outlined
              dense
              type="number"
              step="0.01"
              v-model.number="formData.KHMBJ"
              label="客户目标价 (KHMBJ)"
            />
          </div>
          <div class="col-12 col-sm-4">
            <div class="row q-col-gutter-xs items-center">
              <div class="col-auto">
                <span class="text-caption">规格(mm)</span>
              </div>
              <div class="col">
                <q-input
                  outlined
                  dense
                  type="number"
                  v-model.number="formData.GG_length"
                  label="长"
                  step="0.1"
                />
              </div>
              <div class="col-auto">×</div>
              <div class="col">
                <q-input
                  outlined
                  dense
                  type="number"
                  v-model.number="formData.GG_width"
                  label="宽"
                  step="0.1"
                />
              </div>
              <div class="col-auto">×</div>
              <div class="col">
                <q-input
                  outlined
                  dense
                  type="number"
                  v-model.number="formData.GG_height"
                  label="高"
                  step="0.1"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 包装/台板/送货/客户单号 -->
        <div class="row q-col-gutter-md">
          <div class="col-12 col-sm-6 col-md-3">
            <q-select
              outlined
              dense
              v-model="formData.BZFS"
              :options="bzfsOptions"
              label="包装方式 (BZFS)"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-select
              outlined
              dense
              v-model="formData.TBLX"
              :options="tblxOptions"
              label="台板类型 (TBLX)"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-select
              outlined
              dense
              v-model="formData.SHFS"
              :options="shfsOptions"
              label="送货方式 (SHFS)"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-input
              outlined
              dense
              v-model="formData.KHCPMC"
              label="客户单号 (KHCPMC)"
            />
          </div>
        </div>

        <!-- 交货日期 / 安全检查 / 年龄段 / 是否有配件 -->
        <div class="row q-col-gutter-md">
          <div class="col-12 col-sm-6 col-md-3">
            <q-input
              outlined
              dense
              v-model="jhrqDate"
              type="date"
              label="交货日期 (JHRQ)"
            >
              <template v-slot:append>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy
                    cover
                    transition-show="scale"
                    transition-hide="scale"
                  >
                    <q-date v-model="jhrqDate" mask="YYYY-MM-DD">
                      <div class="row items-center justify-end">
                        <q-btn
                          v-close-popup
                          label="关闭"
                          color="primary"
                          flat
                        />
                      </div>
                    </q-date>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
            <div class="text-caption text-grey-7 q-mt-xs">
              时间戳: {{ timestamp2data(formData.JHRQ) }}
            </div>
          </div>
          <div class="col-12 col-sm-6 col-md-3 flex items-center">
            <q-checkbox
              v-model="formData.has_safety_checks"
              label="需要安全检查"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-select
              outlined
              dense
              v-model="formData.target_age_group"
              :options="ageOptions"
              label="用户年龄段"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-select
              outlined
              dense
              v-model="formData.SFYPJ"
              :options="sfypjOptions"
              label="是否有配件 (SFYPJ)"
            />
          </div>
        </div>

        <!-- 配件描述 / 排序号 / 产品类型 / 预计下单日期 -->
        <div class="row q-col-gutter-md">
          <div class="col-12 col-sm-6 col-md-3">
            <q-input
              outlined
              dense
              v-model="formData.Remark1"
              label="配件描述 (Remark1)"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-input
              outlined
              dense
              type="number"
              v-model.number="formData.PXH"
              label="排序号 (PXH)"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-select
              outlined
              dense
              v-model="formData.CPLX"
              :options="cplxOptions"
              label="产品类型 (CPLX)"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-input
              outlined
              dense
              v-model="wcrqDate"
              type="date"
              label="预计下单日期 (WCRQ)"
            >
              <template v-slot:append>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy
                    cover
                    transition-show="scale"
                    transition-hide="scale"
                  >
                    <q-date v-model="wcrqDate" mask="YYYY-MM-DD" />
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
            <div class="text-caption text-grey-7 q-mt-xs">
              时间戳: {{ timestamp2data(formData.WCRQ) }}
            </div>
          </div>
        </div>

        <!-- 香港单号 / 英文名 / 不需报价 / 纸箱类别 -->
        <div class="row q-col-gutter-md">
          <div class="col-12 col-sm-6 col-md-3">
            <q-input
              outlined
              dense
              v-model="formData.KHDDH"
              label="香港单号 (KHDDH)"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-input
              outlined
              dense
              v-model="formData.ECPMC"
              label="产品英文名 (ECPMC)"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3 flex items-center">
            <q-checkbox v-model="formData.ZDBJF" label="不需报价" />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-select
              outlined
              dense
              v-model="formData.ZXLB"
              :options="zxlbOptions"
              label="纸箱类别 (ZXLB)"
            />
          </div>
        </div>

        <!-- 纸板类型 / 装箱方式 / 台板集装 / 底卡名称 -->
        <div class="row q-col-gutter-md">
          <div class="col-12 col-sm-6 col-md-3">
            <q-select
              outlined
              dense
              v-model="formData.ZBLX"
              :options="zblxOptions"
              label="纸板类型 (ZBLX)"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-input
              outlined
              dense
              v-model="formData.ZXFS"
              label="装箱方式 (ZXFS)"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-select
              outlined
              dense
              v-model="formData.BSYJZX"
              :options="bsyjzxOptions"
              label="台板/集装 (BSYJZX)"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-select
              outlined
              dense
              v-model="formData.DKMC"
              :options="dkmcOptions"
              label="底卡名称 (DKMC)"
            />
          </div>
        </div>

        <!-- 描述区域 -->
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-6">
            <q-input
              outlined
              type="textarea"
              v-model="formData.CPMS"
              label="产品描述 (CPMS)"
              rows="3"
            />
          </div>
          <div class="col-12 col-md-6">
            <q-input
              outlined
              type="textarea"
              v-model="formData.BCMS"
              label="补充描述 (BCMS)"
              rows="3"
            />
          </div>
        </div>

        <!-- 备注字段 -->
        <div class="row q-col-gutter-md">
          <div class="col-12 col-sm-6 col-md-3">
            <q-input
              outlined
              dense
              v-model="formData.CPBZ1"
              label="备注 (CPBZ1)"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-input
              outlined
              dense
              v-model="formData.Remark4"
              label="预留字段 Remark4"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-input
              outlined
              dense
              v-model="formData.Remark3"
              label="预留字段 Remark3"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3 flex items-center">
            <q-btn
              flat
              color="primary"
              label="列表设置关联"
              icon="mdi-link-variant"
              @click="handleListSettings"
            />
          </div>
        </div>

        <!-- 底部操作按钮 -->
        <q-separator spaced />
        <div class="row justify-between items-center">
          <div class="text-caption text-grey-8">列表设置</div>
          <div class="q-gutter-sm">
            <q-btn
              outline
              label="列表设置"
              icon="mdi-cog-outline"
              @click="handleListSettings"
            />
            <q-btn
              color="primary"
              label="保存"
              type="submit"
              icon="mdi-content-save-outline"
            />
            <q-btn flat label="关闭" icon="mdi-close" @click="handleClose" />
          </div>
        </div>
      </q-form>

      <div class="text-caption text-grey-6 q-mt-md text-right">
        ⚡ JSON 键名如 CPDL, CPLB, SJFX … 导入时自动映射填充
      </div>
    </div>
  </q-page>
</template>

<script lang="ts" setup>
import { ref, reactive, computed } from "vue"
import { date } from "quasar"
import dayjs from "dayjs"

// ---------- 下拉选项定义 ----------
const cplbOptions = ["精装书", "平装书", "骑马钉", "儿童书"]
const zdfsOptions = ["胶装", "锁线胶装", "骑马钉", "精装"]
const dwmcOptions = ["本", "套", "册"]
const bzOptions = ["CNY", "USD", "HKD", "EUR"]
const bzfsOptions = ["纸箱", "木箱", "托盘"]
const tblxOptions = ["木质", "塑料", "纸质"]
const shfsOptions = ["陆运", "空运", "海运", "快递"]
const ageOptions = ["不限", "0-3岁", "4-8岁", "9-14岁", "青少年", "成人"]
const sfypjOptions = ["是", "否"]
const cplxOptions = ["常规", "定制", "加急"]
const zxlbOptions = ["普通瓦楞", "重型瓦楞"]
const zblxOptions = ["单粉", "双粉", "灰板"]
const bsyjzxOptions = ["不使用台板", "不使用集装", "正常使用"]
const dkmcOptions = ["灰板", "白卡"]

// ---------- 表单数据 ----------
const formData = reactive({
  id: "4a1c709ed3f44d0faa81b835ed99620d",
  create_by: "KM",
  CPDL: "书版",
  CPLB: "",
  SJFX: "长书脊",
  ZDFS: "",
  CPMC: "EUR追溯",
  TZS: 1,
  YYS: 1,
  DWMC: "本",
  BZ: "CNY",
  KHMBJ: null as number | null,
  GG_length: null as number | null,
  GG_width: null as number | null,
  GG_height: null as number | null,
  BZFS: "",
  TBLX: "",
  SHFS: "",
  KHCPMC: "",
  JHRQ: 0,
  has_safety_checks: false,
  target_age_group: "",
  SFYPJ: "",
  Remark1: "",
  PXH: 1,
  CPLX: "",
  WCRQ: 0,
  KHDDH: "",
  ECPMC: "",
  ZDBJF: false,
  ZXLB: "",
  ZBLX: "",
  ZXFS: "平装",
  BSYJZX: "不使用台板",
  DKMC: "",
  CPMS: "",
  BCMS: "",
  CPBZ1: "",
  Remark4: "",
  Remark3: "",
})

// ---------- 示例数据 ----------
const sampleData = {
  CPDL: "书版",
  CPLB: "精装书",
  SJFX: "长书脊",
  ZDFS: "锁线胶装",
  CPMC: "EUR追溯",
  TZS: 2,
  YYS: 3,
  DWMC: "本",
  BZ: "USD",
  KHMBJ: 12.5,
  GG_length: 210,
  GG_width: 285,
  GG_height: 15,
  BZFS: "纸箱",
  TBLX: "木质",
  SHFS: "陆运",
  KHCPMC: "PO-2409-01",
  JHRQ: 1775804694450,
  has_safety_checks: true,
  target_age_group: "4-8岁",
  SFYPJ: "是",
  Remark1: "丝带书签+贴纸",
  PXH: 1,
  CPLX: "定制",
  WCRQ: 1744243200000,
  KHDDH: "HK-8823",
  ECPMC: "EUR Traceability Edition",
  ZDBJF: false,
  ZXLB: "普通瓦楞",
  ZBLX: "双粉",
  ZXFS: "平装",
  BSYJZX: "不使用台板",
  DKMC: "灰板",
  CPMS: "EUR追溯系列，内文四色，封面烫金。",
  BCMS: "附赠电子追溯码",
  CPBZ1: "首批加急",
  Remark4: "",
  Remark3: "内部编码A01",
}

const loadSampleData = () => {
  Object.assign(formData, sampleData)
}

// ---------- 文件导入 ----------
const fileInput = ref<HTMLInputElement | null>(null)

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileImport = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const json = JSON.parse(e.target?.result as string)
      Object.keys(formData).forEach((key) => {
        if (json.hasOwnProperty(key) && key in formData) {
          ;(formData as any)[key] = json[key]
        }
      })
      alert("✅ JSON 数据已导入")
    } catch (err: any) {
      alert("❌ JSON解析失败: " + err.message)
    } finally {
      target.value = "" // 清空input，允许重复导入同一文件
    }
  }
  reader.readAsText(file, "UTF-8")
}

// ---------- 时间戳与日期互转 ----------
const timestamp2data = (ts: number, format = "YYYY-MM-DD HH:mm:ss") => {
  if (!ts) return ""
  const d = dayjs(ts)
  return d.isValid() ? d.format(format) : ""
}

// 计算属性处理双向转换
const jhrqDate = computed<string>({
  get: () => (formData.JHRQ ? dayjs(formData.JHRQ).format("YYYY-MM-DD") : ""),
  set: (val) => {
    formData.JHRQ = val ? dayjs(val).valueOf() : 0
  },
})

const wcrqDate = computed<string>({
  get: () => (formData.WCRQ ? dayjs(formData.WCRQ).format("YYYY-MM-DD") : ""),
  set: (val) => {
    formData.WCRQ = val ? dayjs(val).valueOf() : 0
  },
})

// ---------- 操作事件 ----------
const handleListSettings = () => {
  alert("列表设置：可配置显示列 (演示)")
}

const handleSave = () => {
  console.log("📦 保存的表单数据:", { ...formData })
  alert("数据已保存至控制台，可查看详情。")
}

const handleClose = () => {
  if (confirm("关闭面板？")) {
    alert("面板关闭 (演示)")
  }
}

// 页面加载时自动填充示例数据
loadSampleData()
</script>

<style lang="scss" scoped>
.erp-card {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
  padding: 24px;
  border: 1px solid #e2e8f0;
}

.header-section {
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 16px;
  flex-wrap: wrap;
}

// 让 Quasar 输入框在网格中表现一致
.q-field {
  margin-bottom: 0;
}
</style>
