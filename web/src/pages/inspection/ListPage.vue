<script lang="ts" setup>
import { useQuasar } from "quasar"
import { getImageBlobUrl } from "src/apis/file_api"
import { ai_inspection_v1_list } from "src/apis/inspection_record_api"

import type { IInspectionRecordOut } from "src/interfaces/IInspection"
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

// 获取执行详细的列表
const get_inspection_v1_list = async () => {
  blobUrls.value.forEach((url) => URL.revokeObjectURL(url))
  blobUrls.value = []

  const res = await ai_inspection_v1_list(page.value) // 刷新表格
  const {
    records,
    total,
    current,
    size: backendSize,
    orders,
    maxLimit,
  } = res.data

  // 为每条记录的图片生成临时 Blob URL
  const recordsWithImage = await Promise.all(
    records.map(async (record: any) => {
      if (record.file_id) {
        try {
          const blobUrl = await getImageBlobUrl(record.file_id)
          blobUrls.value.push(blobUrl) // 记录生成的 Blob URL
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
  // 如果后端实际返回的条数与用户选择的不一致，修正并提示
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
    sortable: false, // 操作列通常不需要排序
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
// 控制编辑对话框的显示
const showEditDialog = ref(false)

const editRow = (row: IInspectionRecordOut) => {
  // 例如：打开对话框，传入当前行数据
  // 深拷贝一份，避免直接修改表格原数据
  currentEditRow.value = JSON.parse(JSON.stringify(row))
  showEditDialog.value = true
}

// 存储当前正在编辑的行数据
const currentEditRow = ref<IInspectionRecordOut>(
  null as unknown as IInspectionRecordOut,
)
// 保存修改后的数据
const saveEdit = async () => {
  if (!currentEditRow.value) return

  // 调用你实际的更新 API（这里假设为 v1_update）
  // 注意：请根据你的后端接口调整参数
  //   const res1 = await v1_update(currentEditRow.value.id, currentEditRow.value)
  //   if (res1.code === 200) {
  //     // 示例：模拟更新成功
  //     // 更新成功后重新拉取列表
  //     await get_requirement_list()
  //   }

  // 关闭对话框
  showEditDialog.value = false
}
// 取消编辑
const cancelEdit = () => {
  showEditDialog.value = false
  currentEditRow.value = null as unknown as IInspectionRecordOut
}

/**************删除记录**************** */
const deleteRow = (row: IInspectionRecordOut) => {
  $q.dialog({
    title: "确认删除",
    message: `真的要删除“${row.item_name}”吗？`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    // await 删除 API
    // await v1_delete(row.id)
    // await get_requirement_list()
  })
}

onMounted(async () => {
  await get_inspection_v1_list()
})

// 监听每页条数变化
watch(
  () => page.value.size,
  async (newSize, oldSize) => {
    if (newSize !== oldSize) {
      page.value.current = 1 // 重置到第一页
      await get_inspection_v1_list()
    }
  },
)

// 监听当前页码变化
watch(
  () => page.value.current,
  async (newCurrent, oldCurrent) => {
    if (newCurrent !== oldCurrent) {
      await get_inspection_v1_list()
    }
  },
)
// 组件卸载时清理
onBeforeUnmount(() => {
  blobUrls.value.forEach((url) => URL.revokeObjectURL(url))
})
</script>

<template>
  <div>
    <q-card class="my-card bg-secondary text-white">
      <q-card-section></q-card-section>
      <q-card-section>
        <q-table
          title="📋 巡检列表"
          :rows="page.records"
          :columns="columns"
          row-key="id"
          hide-pagination
          v-model:pagination="pagination"
          :rows-per-page="0"
        >
          <template v-slot:body-cell-file_id="props">
            <q-td :props="props">
              <q-img
                v-if="props.row.imageBlobUrl"
                :src="props.row.imageBlobUrl"
                :ratio="16 / 9"
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
          <!-- AI 执行图片分析的结果 -->
          <template v-slot:body-cell-ai_detection_execute="props">
            <q-td :props="props" class="text-wrap-cell">
              {{
                props.row.ai_detection_execute?.result?.response ??
                "AI 思考中..."
              }}
            </q-td>
          </template>

          <!-- AI 提取的特定巡检项目结果 -->
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
        <div
          class="row justify-center q-mt-md bg-white text-black"
          style="padding: 0.2%; margin-top: 0; align-items: center"
        >
          <div class="text-subtitle2" style="margin: 0 0.5%">
            总条数为: {{ page.total }}
          </div>
          <div class="text-subtitle2" style="margin: 0 0.5%">
            <div>每页记录:</div>
          </div>
          <div class="text-subtitle2" style="margin: 0 0.5%">
            <select v-model="page.size" class="transparent-select-native">
              <option v-for="n in [1, 3, 5, 10, 20, 50, 100]" :value="n">
                {{ n }}
              </option>
            </select>
          </div>
          <div style="margin: 0 0.5%">
            <q-pagination
              v-model="page.current"
              :max="MaxPage"
              :max-pages="6"
              boundary-numbers
            />
          </div>
        </div>
      </q-card-section>
      <q-separator dark />
    </q-card>
    <!-- 编辑对话框 -->
    <q-dialog v-model="showEditDialog" :persistent="false">
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">修改巡检要求</div>
        </q-card-section>

        <q-card-section>
          <q-form @submit="saveEdit">
            <q-input
              v-model="currentEditRow.ai_detection_execute_id"
              label="AI 执行图片分析的结果"
              outlined
              dense
              :rules="[(val) => !!val || '项目名称不能为空']"
            />
            <q-input
              v-model="currentEditRow.ai_inspection_excute_id"
              label="Ai 提取的特定巡检项目结果的"
              outlined
              dense
              type="textarea"
              rows="3"
            />
            <!-- 如果还需要编辑其他字段，继续添加 -->
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
  white-space: normal !important;   /* 允许换行 */
  word-break: break-word;           /* 长单词/URL 强制换行 */
  max-width: 300px;                 /* 限制最大宽度，促使换行 */
</style>
