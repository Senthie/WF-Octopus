<script lang="ts" setup>
import { useQuasar } from "quasar"
import ImageUploadComponent from "src/components/ImageUploadComponent.vue"
import {
  IInspectionRecordIn,
  IInspectionRequirementRes,
} from "src/interfaces/IInspection"
import { v1_all as inspection_requirement_v1_all } from "src/apis/inspection_requirement_api"
import { computed, onMounted, ref } from "vue"
import { useImageFileStore } from "src/stores/file-store"

const $q = useQuasar()
const image_file_store = useImageFileStore()
const record_data = ref<IInspectionRecordIn>({
  file_id: "",
  responsible_person: "",
  inspection_requirements_id: "",
})

let inspection_requirements = ref<IInspectionRequirementRes[]>([])
let inspection_requirement_options = ref<
  {
    label: string
    value: string
    description: string
    category: string
  }[]
>([])

// 获取执行详细的列表
const get_inspection_requirements_list = async () => {
  const res = await inspection_requirement_v1_all() // 刷新表格
  inspection_requirements.value = res.data
  for (const ir of res.data) {
    inspection_requirement_options.value.push({
      label: ir.item_name,
      value: ir.id,
      description: ir.safety_requirement,
      category: "1",
    })
  }
}

const get_safety_requirement_by_id = computed(() => {
  for (const ir of inspection_requirements.value) {
    if (record_data.value.inspection_requirements_id === ir.id) {
      return ir.safety_requirement
    }
  }
})

const onSubmit = async () => {
  // 先上传照片
  const file_id = await image_file_store.post_in_server()
  $q.notify({
    color: "green-4",
    textColor: "white",
    icon: "cloud_done",
    message: `${file_id}`,
  })
}

const onReset = () => {
  record_data.value = {
    file_id: "",
    responsible_person: "",
    inspection_requirements_id: "",
  }
}

onMounted(async () => {
  await get_inspection_requirements_list()
})
</script>
<template>
  <div style="margin-top: 2%">
    <div>
      <q-form @submit="onSubmit" @reset="onReset" class="q-gutter-md">
        <ImageUploadComponent></ImageUploadComponent>

        <q-select
          v-model="record_data.inspection_requirements_id"
          :options="inspection_requirement_options"
          label="请选择巡检类型"
          emit-value
          map-options
        />
        <q-input
          v-model="get_safety_requirement_by_id"
          label="检测描述"
          outlined
          dense
          :disable="true"
          type="textarea"
          rows="3"
        />
        <q-input
          v-model="record_data.responsible_person"
          label="区域负责人"
          outlined
          dense
        />
        <div>
          <q-btn label="提交" type="submit" color="primary" />
          <q-btn
            label="重置"
            type="reset"
            color="primary"
            flat
            class="q-ml-sm"
          />
        </div>
      </q-form>
    </div>
  </div>
</template>
