<script setup lang="ts">
import { useImageFileStore } from "src/stores/file-store"

import { ref, computed, onBeforeUnmount, onMounted } from "vue"

const image_file_store = useImageFileStore()
// ---------- 响应式状态 ----------
const fileInputRef = ref<HTMLInputElement | null>(null)
const dropZoneRef = ref<HTMLElement | null>(null)

const isDragover = ref(false)

// ---------- 方法 ----------
const triggerUpload = () => {
  fileInputRef.value?.click()
}

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) image_file_store.processFile(file)
  // 重置 input 以允许重复选择同一文件
  target.value = ""
}

// 拖拽事件
const onDragOver = () => {
  isDragover.value = true
}

const onDragLeave = (event: DragEvent) => {
  // 仅当完全离开 dropZone 时取消高亮
  if (
    dropZoneRef.value &&
    !dropZoneRef.value.contains(event.relatedTarget as Node)
  ) {
    isDragover.value = false
  }
}

const onDrop = (event: DragEvent) => {
  isDragover.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file) image_file_store.processFile(file)
}

onMounted(() => {})

// 组件卸载时清理内存
onBeforeUnmount(() => {
  if (image_file_store.upload_file) {
    URL.revokeObjectURL(image_file_store.upload_file.preview_url)
  }
})
</script>

<template>
  <div class="upload-card">
    <div class="upload-card__header">
      <span class="dot"></span>
      上传图片
    </div>

    <!-- 上传区域 -->
    <div
      ref="dropZoneRef"
      class="upload-zone"
      :class="{
        'upload-zone--has-image': image_file_store.imagePreviewUrl,
        'upload-zone--dragover': isDragover,
      }"
      @click="triggerUpload"
      @dragover.prevent="onDragOver"
      @dragleave.prevent="onDragLeave"
      @drop.prevent="onDrop"
    >
      <!-- 占位符 -->
      <div v-if="!image_file_store.imagePreviewUrl" class="upload-placeholder">
        <div class="upload-placeholder__icon">
          <svg
            viewBox="0 0 80 80"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <rect
              x="6"
              y="12"
              width="60"
              height="56"
              rx="10"
              stroke="#4f6ef7"
              stroke-width="2.8"
              fill="none"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
            <path
              d="M30 6 L30 12 L42 12 L42 6"
              stroke="#4f6ef7"
              stroke-width="2.8"
              stroke-linecap="round"
              stroke-linejoin="round"
              fill="none"
            />
            <path
              d="M18 54 L30 38 L40 46 L50 30 L62 50 L62 58 L18 58 Z"
              fill="#e8efff"
              stroke="#4f6ef7"
              stroke-width="2"
              stroke-linejoin="round"
            />
            <circle
              cx="50"
              cy="26"
              r="6"
              fill="none"
              stroke="#4f6ef7"
              stroke-width="2.2"
            />
            <circle cx="36" cy="34" r="11" fill="#4f6ef7" opacity="0.9" />
            <path
              d="M32 34 L40 34 M36 30 L36 38"
              stroke="#fff"
              stroke-width="2.5"
              stroke-linecap="round"
            />
          </svg>
        </div>
        <span class="upload-placeholder__text">点击上传图片</span>
        <span class="upload-placeholder__hint">或拖拽文件到此处</span>
        <div class="upload-placeholder__formats">
          <span>JPG</span><span>PNG</span><span>GIF</span><span>WebP</span
          ><span>SVG</span>
        </div>
      </div>

      <!-- 预览图 -->
      <div v-else class="preview-wrapper">
        <img :src="image_file_store.imagePreviewUrl" alt="预览图片" />
        <div class="preview-overlay">
          <button
            class="btn btn--replace"
            title="更换图片"
            @click.stop="triggerUpload"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <polyline points="23 4 23 10 17 10" />
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
            </svg>
          </button>
          <button
            class="btn btn--delete"
            title="删除图片"
            @click.stop="image_file_store.removeImage"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <polyline points="3 6 5 6 21 6" />
              <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
              <path d="M10 11v6" />
              <path d="M14 11v6" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 隐藏的文件输入 -->
    <input
      ref="fileInputRef"
      type="file"
      accept="image/*"
      class="hidden-input"
      @change="handleFileChange"
    />

    <!-- 底部信息 -->
    <div class="upload-info">
      <span v-if="image_file_store.imagePreviewUrl" class="upload-info__status">
        <span class="status-dot"></span> 已上传
      </span>
      <span v-else class="upload-info__status upload-info__status--idle"
        >等待上传</span
      >
      <span class="upload-info__size">{{
        image_file_store.file_size_text || "最大 10MB"
      }}</span>
    </div>
  </div>
</template>

<style lang="sass" scoped>
// ========== 变量 ==========
$primary: #4f6ef7
$primary-hover: #3b54e0
$border: #dce1e8
$border-dashed: #c5cdd8
$bg: #f8f9fb
$bg-hover: #eef1f7
$text: #2c3e50
$text-light: #8b95a5
$radius: 16px
$radius-inner: 12px
$transition: 0.25s cubic-bezier(0.4, 0, 0.2, 1)

// ========== 卡片容器 ==========
.upload-card
  background: #fff
  border-radius: 20px
  padding: 28px 24px
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.05), 0 1px 4px rgba(0, 0, 0, 0.04)
  max-width: 420px
  margin: 0 auto

  &__header
    font-size: 15px
    font-weight: 600
    color: $text
    margin-bottom: 20px
    letter-spacing: -0.01em
    display: flex
    align-items: center
    gap: 8px

    .dot
      width: 8px
      height: 8px
      border-radius: 50%
      background: $primary
      display: inline-block

// ========== 上传区域 ==========
.upload-zone
  position: relative
  border: 2px dashed $border-dashed
  border-radius: $radius
  background: $bg
  cursor: pointer
  transition: all $transition
  overflow: hidden
  min-height: 220px
  display: flex
  align-items: center
  justify-content: center
  user-select: none
  -webkit-tap-highlight-color: transparent

  &:hover
    border-color: $primary
    background: $bg-hover
    transform: translateY(-1px)
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06)

  &:active
    transform: scale(0.985)
    transition: transform 0.1s ease

  &--dragover
    border-color: $primary !important
    background: #eef3ff !important
    box-shadow: 0 0 0 6px rgba($primary, 0.08)
    transform: translateY(-1px)

  &--has-image
    border-style: solid
    border-color: transparent
    background: transparent
    cursor: default
    min-height: auto
    border-radius: $radius

    &:hover
      transform: none
      box-shadow: none
      background: transparent
      border-color: transparent

// ========== 占位内容 ==========
.upload-placeholder
  display: flex
  flex-direction: column
  align-items: center
  gap: 14px
  padding: 20px
  pointer-events: none

  &__icon
    svg
      width: 72px
      height: 72px
      transition: transform $transition

    .upload-zone:hover &
      svg
        transform: translateY(-4px)

  &__text
    font-size: 15px
    font-weight: 500
    color: $text
    letter-spacing: -0.01em

  &__hint
    font-size: 12px
    color: $text-light

  &__formats
    display: flex
    gap: 6px
    flex-wrap: wrap
    justify-content: center

    span
      font-size: 11px
      padding: 4px 10px
      border-radius: 20px
      background: #e8ecf4
      color: #5a6476
      font-weight: 500

// ========== 预览图 ==========
.preview-wrapper
  width: 100%
  position: relative
  border-radius: $radius-inner
  overflow: hidden
  line-height: 0
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1)

  img
    width: 100%
    height: auto
    display: block
    max-height: 400px
    object-fit: contain
    background: #fafbfc

// ========== 悬浮操作层 ==========
.preview-overlay
  position: absolute
  inset: 0
  background: linear-gradient(to top, rgba(0, 0, 0, 0.55) 0%, rgba(0, 0, 0, 0.08) 45%, transparent 100%)
  display: flex
  align-items: flex-end
  justify-content: flex-end
  padding: 14px 16px
  gap: 10px
  opacity: 0
  transition: opacity $transition
  pointer-events: none

  .preview-wrapper:hover &
    opacity: 1
    pointer-events: auto

  // 移动端始终显示
  @media (hover: none) and (pointer: coarse)
    opacity: 1
    pointer-events: auto
    background: linear-gradient(to top, rgba(0, 0, 0, 0.45) 0%, transparent 55%)

.btn
  width: 38px
  height: 38px
  border-radius: 50%
  border: none
  cursor: pointer
  display: flex
  align-items: center
  justify-content: center
  transition: all $transition
  backdrop-filter: blur(8px)
  -webkit-backdrop-filter: blur(8px)

  &--replace
    background: rgba(255, 255, 255, 0.85)
    color: #2c3e50

    &:hover
      background: #fff
      transform: scale(1.08)
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.18)

  &--delete
    background: rgba(255, 255, 255, 0.75)
    color: #e74c3c

    &:hover
      background: #ffeaea
      color: #c0392b
      transform: scale(1.08)
      box-shadow: 0 4px 14px rgba(231, 76, 60, 0.25)

// ========== 隐藏的 input ==========
.hidden-input
  display: none

// ========== 底部信息 ==========
.upload-info
  display: flex
  align-items: center
  justify-content: space-between
  margin-top: 16px
  padding: 0 4px

  &__status
    font-size: 12px
    color: $text-light
    display: flex
    align-items: center
    gap: 6px

    .status-dot
      width: 7px
      height: 7px
      border-radius: 50%
      background: #27ae60
      animation: blink 2s ease-in-out infinite

    &--idle
      color: #b0b9c4

  &__size
    font-size: 11px
    color: $text-light
    background: #f1f3f7
    padding: 5px 10px
    border-radius: 14px

@keyframes blink
  0%, 100%
    opacity: 1
  50%
    opacity: 0.35

// ========== 响应式 ==========
@media (max-width: 480px)
  .upload-card
    padding: 20px 16px
    border-radius: 16px

  .upload-zone
    min-height: 180px
    border-radius: 14px

  .upload-placeholder__icon svg
    width: 56px
    height: 56px

  .upload-placeholder__text
    font-size: 14px

  .btn
    width: 34px
    height: 34px
</style>
