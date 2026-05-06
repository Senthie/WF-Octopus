<script setup lang="ts">
import { ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const push_route = (path: string) => {
  router.push(path)
}
</script>
<template>
  <div>
    <div>
      <div class="row">
        <div class="col-2">
          <q-btn
            color="white"
            text-color="black"
            label="巡检"
            @click="push_route('/inspection/')"
          />
        </div>
      </div>
    </div>
  </div>
</template>
