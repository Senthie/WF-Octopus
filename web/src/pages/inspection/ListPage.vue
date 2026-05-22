<script lang="ts" setup>
import { useQuasar } from "quasar"
import { getImageBlobUrl } from "src/apis/file_api"
import {
  ai_inspection_v1_list,
  v1_update as inspection_v1_update,
  v1_delete as inspection_v1_delete,
} from "src/apis/inspection_record_api"

import type {
  IInspectionRecordOut,
  InspectionRecordUpdateIn,
} from "src/interfaces/IInspection"
import type { IPageRes } from "src/interfaces/Ipage"
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue"

const $q = useQuasar()

// 存储分页信息
const page = ref<IPageRes<IInspectionRecordOut>>({
  total: 0,
  size: 10,
  current: 1,
  orders: [],
  records: [],
  maxLimit: 0,
})
// 计算最大的页数
const MaxPage = computed(
  () => Math.ceil(page.value.total / page.value.size) || 1,
)
// 记录所有创建的 blob URL
const blobUrls = ref<string[]>([])

// 每页条数选项（用于 q-select）
const sizeOptions = [1, 3, 5, 10, 20, 50, 100]

// 获取执行详细的列表
const get_inspection_v1_list = async () => {
  blobUrls.value.forEach((url) => URL.revokeObjectURL(url))
  blobUrls.value = []

  const res = await ai_inspection_v1_list(page.value)
  const {
    records,
    total,
    current,
    size: backendSize,
    orders,
    maxLimit,
  } = res.data

  const recordsWithImage = await Promise.all(
    records.map(async (record: any) => {
      if (record.file_id) {
        try {
          const blobUrl = await getImageBlobUrl(record.file_id)
          blobUrls.value.push(blobUrl)
          return { ...record, imageBlobUrl: blobUrl }
        } catch (e) {
          return { ...record, imageBlobUrl: "" }
        }
      }
      return record
    }),
  )

  page.value.records = recordsWithImage
  page.value.total = total
  page.value.current = current
  if (backendSize && backendSize < page.value.size) {
    page.value.size = backendSize
    $q.notify({
      type: "warning",
      message: `当前每页最多显示 ${backendSize} 条`,
      position: "top",
      timeout: 2000,
    })
  }
}

const columns = [
  {
    name: "id",
    required: true,
    label: "标识",
    align: "left",
    field: "id",
    format: (val: string) => `${val}`,
    sortable: true,
  },
  {
    name: "status",
    align: "center",
    label: "巡检状态",
    field: "status",
    sortable: true,
  },
  {
    name: "file_id",
    label: "现场照片",
    field: "file_id",
    sortable: true,
  },
  {
    name: "ai_detection_execute",
    label: "AI 执行图片分析的结果",
    field: "ai_detection_execute",
  },
  {
    name: "ai_inspection_excute",
    label: "Ai 提取的特定巡检项目结果",
    field: "ai_inspection_excute",
  },
  {
    name: "responsible_person",
    label: "区域负责人",
    field: "responsible_person",
    sortable: true,
  },
  {
    name: "updated_by_user",
    label: "最后更新人",
    field: "updated_by_user",
  },
  { name: "updated_at", label: "最后更新日期", field: "updated_at" },
  {
    name: "actions",
    label: "操作",
    field: "actions",
    align: "center",
    sortable: false,
  },
]

const pagination = ref({
  sortBy: "desc",
  descending: false,
  page: 2,
  rowsPerPage: 1,
  rowsNumber: 2,
})

/**************修改记录**************** */
const showEditDialog = ref(false)

let inspection_result_status_options = ref([
  { label: "正常", value: "normal" },
  { label: "需要整改", value: "requires_correction" },
  { label: "整改进行中", value: "in_progress" },
  { label: "已经整改", value: "corrected" },
])

const currentEdit_id = ref<string>("")
const currentEditRow = ref<InspectionRecordUpdateIn>(
  null as unknown as InspectionRecordUpdateIn,
)

const editRow = (row: IInspectionRecordOut) => {
  currentEdit_id.value = row.id
  currentEditRow.value = {
    inspection_requirements_id: row.inspection_requirements_id,
    status: row.status,
    responsible_person: row.responsible_person,
    ai_detection_execute_result:
      row.ai_detection_execute?.result?.response ?? "",
    ai_inspection_excute_result: row.ai_inspection_excute?.result?.result ?? "",
  }
  showEditDialog.value = true
}

const saveEdit = async () => {
  if (!currentEditRow.value) return
  const res1 = await inspection_v1_update(
    currentEdit_id.value,
    currentEditRow.value,
  )
  if (res1.code === 200) {
    await get_inspection_v1_list()
  }
  showEditDialog.value = false
}

const cancelEdit = () => {
  showEditDialog.value = false
  currentEditRow.value = null as unknown as InspectionRecordUpdateIn
}

/**************删除记录**************** */
const deleteRow = (row: IInspectionRecordOut) => {
  $q.dialog({
    title: "确认删除",
    message: `真的要删除“${row.id}”吗？`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    await inspection_v1_delete(row.id)
    await get_inspection_v1_list()
  })
}

onMounted(async () => {
  await get_inspection_v1_list()
})

watch(
  () => page.value.size,
  async (newSize, oldSize) => {
    if (newSize !== oldSize) {
      page.value.current = 1
      await get_inspection_v1_list()
    }
  },
)

watch(
  () => page.value.current,
  async (newCurrent, oldCurrent) => {
    if (newCurrent !== oldCurrent) {
      await get_inspection_v1_list()
    }
  },
)

onBeforeUnmount(() => {
  blobUrls.value.forEach((url) => URL.revokeObjectURL(url))
})
</script>

<template>
  <div>
    <q-card class="my-card bg-secondary text-white">
      <q-card-section></q-card-section>
      <q-card-section>
        <!-- 表格区域：桌面端表格，移动端自动切换为卡片网格 -->
        <q-table
          title="📋 巡检列表"
          :rows="page.records"
          :columns="columns"
          row-key="id"
          hide-pagination
          v-model:pagination="pagination"
          :rows-per-page="0"
          :grid="$q.screen.lt.sm"
        >
          <!-- 移动端卡片布局 -->
          <template v-slot:item="props">
            <div class="q-pa-xs col-12">
              <q-card class="full-width">
                <q-card-section horizontal>
                  <q-card-section class="col-5 flex flex-center">
                    <q-img
                      v-if="props.row.imageBlobUrl"
                      :src="props.row.imageBlobUrl"
                      :ratio="4 / 3"
                      style="max-height: 140px"
                    />
                    <span v-else class="text-grey">无图片</span>
                  </q-card-section>
                  <q-card-section class="col-7 q-pl-sm">
                    <div class="text-subtitle2 text-weight-bold">
                      {{ props.row.responsible_person || "--" }}
                    </div>
                    <div class="q-mt-xs">
                      状态:
                      <q-chip
                        v-if="props.row.status === 'normal'"
                        color="primary"
                        text-color="white"
                        dense
                        size="sm"
                        label="正常"
                      />
                      <q-chip
                        v-else-if="props.row.status === 'requires_correction'"
                        color="orange"
                        text-color="white"
                        dense
                        size="sm"
                        label="需要整改"
                      />
                      <q-chip
                        v-else-if="props.row.status === 'in_progress'"
                        color="teal"
                        text-color="white"
                        dense
                        size="sm"
                        label="整改中"
                      />
                      <q-chip
                        v-else-if="props.row.status === 'corrected'"
                        color="green"
                        text-color="white"
                        dense
                        size="sm"
                        label="已整改"
                      />
                      <q-chip v-else color="red" dense size="sm" label="未知" />
                    </div>
                    <div class="text-caption text-wrap text-grey-4 q-mt-xs">
                      AI分析:
                      {{
                        props.row.ai_detection_execute?.result?.response ??
                        "AI 思考中..."
                      }}
                    </div>
                    <div class="text-caption text-wrap text-grey-4">
                      巡检项:
                      {{
                        props.row.ai_inspection_excute?.result?.result ??
                        "AI 思考中..."
                      }}
                    </div>
                  </q-card-section>
                </q-card-section>
                <q-separator />
                <q-card-actions align="right">
                  <q-btn
                    size="sm"
                    color="primary"
                    label="修改"
                    @click="editRow(props.row)"
                  />
                  <q-btn
                    size="sm"
                    color="negative"
                    label="删除"
                    @click="deleteRow(props.row)"
                    class="q-ml-sm"
                  />
                </q-card-actions>
              </q-card>
            </div>
          </template>

          <!-- 桌面端列插槽（grid=false 时生效） -->
          <template v-slot:body-cell-file_id="props">
            <q-td :props="props">
              <q-img
                v-if="props.row.imageBlobUrl"
                :src="props.row.imageBlobUrl"
                :ratio="16 / 9"
                style="max-width: 160px"
              />
              <span v-else>-</span>
            </q-td>
          </template>
          <template v-slot:body-cell-actions="props">
            <q-td :props="props">
              <q-btn
                size="sm"
                color="primary"
                label="修改"
                @click="editRow(props.row)"
              />
              <q-btn
                size="sm"
                color="negative"
                label="删除"
                @click="deleteRow(props.row)"
                class="q-ml-sm"
              />
            </q-td>
          </template>
          <template v-slot:body-cell-ai_detection_execute="props">
            <q-td :props="props" class="text-wrap-cell">
              {{
                props.row.ai_detection_execute?.result?.response ??
                "AI 思考中..."
              }}
            </q-td>
          </template>
          <template v-slot:body-cell-ai_inspection_excute="props">
            <q-td :props="props" class="text-wrap-cell">
              {{
                props.row.ai_inspection_excute?.result?.result ?? "AI 思考中..."
              }}
            </q-td>
          </template>
          <template v-slot:body-cell-status="props">
            <q-td :props="props">
              <template v-if="props.row.status === 'normal'">
                <q-chip color="primary" label="正常" />
              </template>
              <template v-else-if="props.row.status === 'requires_correction'">
                <q-chip color="orange" label="需要整改" />
              </template>
              <template v-else-if="props.row.status === 'in_progress'">
                <q-chip color="teal" label="整改进行中" />
              </template>
              <template v-else-if="props.row.status === 'corrected'">
                <q-chip color="green" label="已经整改" />
              </template>
              <template v-else>
                <q-chip color="red" label="未知错误" />
              </template>
            </q-td>
          </template>
        </q-table>

        <!-- 响应式分页条 -->
        <div
          class="row justify-center items-center q-mt-md q-gutter-sm bg-white text-black q-pa-sm rounded-borders"
        >
          <div class="text-subtitle2">总条数: {{ page.total }}</div>
          <div class="row items-center q-gutter-x-xs">
            <span class="text-subtitle2">每页</span>
            <q-select
              v-model="page.size"
              :options="sizeOptions"
              dense
              outlined
              style="width: 80px"
              emit-value
              map-options
            />
          </div>
          <q-pagination
            v-model="page.current"
            :max="MaxPage"
            :max-pages="5"
            boundary-numbers
            direction-links
          />
        </div>
      </q-card-section>
      <q-separator dark />
    </q-card>

    <!-- 编辑对话框：移动端全屏，桌面端自适应宽度 -->
    <q-dialog
      v-model="showEditDialog"
      :persistent="false"
      :maximized="$q.screen.lt.sm"
    >
      <q-card
        :style="
          $q.screen.lt.sm
            ? ''
            : 'min-width: 500px; max-width: 90vw; max-height: 80vh'
        "
      >
        <q-card-section>
          <div class="text-h6">修改巡检要求</div>
        </q-card-section>

        <q-card-section class="scroll" style="max-height: calc(80vh - 120px)">
          <q-form @submit="saveEdit">
            <q-select
              v-model="currentEditRow.status"
              :options="inspection_result_status_options"
              option-value="value"
              option-label="label"
              label="巡检状态"
              emit-value
              map-options
              :rules="[(val) => (val && val.length > 0) || '请选择巡检状态']"
            />
            <q-input
              v-model="currentEditRow.ai_detection_execute_result"
              label="AI 执行图片分析的结果"
              outlined
              dense
              type="textarea"
              rows="4"
            />
            <q-input
              v-model="currentEditRow.ai_inspection_excute_result"
              label="AI 提取的特定巡检项目结果"
              outlined
              dense
              type="textarea"
              rows="5"
            />
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="取消" v-close-popup @click="cancelEdit" />
          <q-btn
            flat
            label="保存"
            type="submit"
            color="primary"
            @click="saveEdit"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<style lang="sass" scoped>
.text-wrap-cell
  white-space: normal !important
  word-break: break-word
  max-width: 300px

// 移动端卡片内文本强制换行
.text-wrap
  white-space: normal
  word-break: break-word
</style>
