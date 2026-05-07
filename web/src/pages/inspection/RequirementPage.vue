<script lang="ts" setup>
import { v1_list, v1_update } from "src/apis/inspection_requirement_api"
import { IInspectionRequirementRes } from "src/interfaces/IInspection"
import type { IPageRes } from "src/interfaces/Ipage"
import { computed, onMounted, ref, watch } from "vue"
import { useQuasar } from "quasar"
const $q = useQuasar()

const deleteRow = (row: IInspectionRequirementRes) => {
  $q.dialog({
    title: "确认删除",
    message: `真的要删除“${row.item_name}”吗？`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    // await 删除 API
    const res = await v1_list(page.value) // 刷新表格
    page.value = res.data
  })
}

// 控制编辑对话框的显示
const showEditDialog = ref(false)
// 存储当前正在编辑的行数据
const currentEditRow = ref<IInspectionRequirementRes>(
  null as unknown as IInspectionRequirementRes,
)
const editRow = (row: IInspectionRequirementRes) => {
  // 例如：打开对话框，传入当前行数据
  // 深拷贝一份，避免直接修改表格原数据
  currentEditRow.value = JSON.parse(JSON.stringify(row))
  showEditDialog.value = true
}

// 保存修改后的数据
const saveEdit = async () => {
  if (!currentEditRow.value) return

  // 调用你实际的更新 API（这里假设为 v1_update）
  // 注意：请根据你的后端接口调整参数
  const res1 = await v1_update(currentEditRow.value.id, currentEditRow.value)
  if (res1.code === 200) {
    // 示例：模拟更新成功
    // 更新成功后重新拉取列表
    const res2 = await v1_list(page.value)
    page.value = res2.data
  }

  // 关闭对话框
  showEditDialog.value = false
}

// 取消编辑
const cancelEdit = () => {
  showEditDialog.value = false
  currentEditRow.value = null as unknown as IInspectionRequirementRes
}

const page = ref<IPageRes<IInspectionRequirementRes>>({
  total: 0,
  size: 10,
  current: 1,
  orders: [],
  records: [],
  maxLimit: 0,
})
const MaxPage = computed(() => {
  return Math.ceil(page.value.total / page.value.size)
})
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
    name: "item_name",
    align: "center",
    label: "检测项目名称",
    field: "item_name",
    sortable: true,
  },
  {
    name: "safety_requirement",
    label: "检测描述",
    field: "safety_requirement",
    sortable: true,
  },
  { name: "created_by", label: "创建人", field: "created_by" },
  {
    name: "created_at",
    label: "创建日期",
    field: "created_at",
    sortable: true,
  },
  { name: "updated_by", label: "最后更新人", field: "created_by" },
  { name: "updated_at", label: "最后更新日期", field: "updated_at" },
  {
    name: "actions",
    label: "操作",
    field: "actions",
    align: "center",
    sortable: false, // 操作列通常不需要排序
  },
]

// 监听每页条数变化
watch(
  () => page.value.size,
  async (newSize, oldSize) => {
    if (newSize !== oldSize) {
      page.value.current = 1 // 重置到第一页
      const res = await v1_list(page.value)
      page.value = res.data
    }
  },
)

// 监听当前页码变化
watch(
  () => page.value.current,
  async (newCurrent, oldCurrent) => {
    if (newCurrent !== oldCurrent) {
      const res = await v1_list(page.value)
      page.value = res.data
    }
  },
)

onMounted(async () => {
  const res = await v1_list(page.value)
  page.value = res.data
})
</script>
<template>
  <div>
    <q-card class="my-card bg-secondary text-white">
      <q-card-section>
        <div class="text-h6">📋 巡检要求明细表</div>
        <div class="text-subtitle2">巡检要求的增删改查</div>
        <!-- <q-btn type="primary" @click="showAddDialog = true">新增要求</q-btn> -->
      </q-card-section>
      <q-card-section>
        <q-table
          title="Treats"
          :rows="page.records"
          :columns="columns"
          row-key="id"
          hide-pagination
        >
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
              <option v-for="n in [1, 2, 5, 10, 20, 50, 100]" :value="n">
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
      <div>
        {{ page }}
      </div>
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
              v-model="currentEditRow.item_name"
              label="检测项目名称 *"
              outlined
              dense
              :rules="[(val) => !!val || '项目名称不能为空']"
            />
            <q-input
              v-model="currentEditRow.safety_requirement"
              label="检测描述"
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
<style scoped></style>
