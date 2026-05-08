/*
 * @Author: Senthie seemoon2077@gmail.com
 * @Date: 2026-01-06 12:15:18
 * @LastEditors: Senthie seemoon2077@gmail.com
 * @LastEditTime: 2026-01-06 17:43:56
 * @FilePath: /web/src/stores/user-store.ts
 * @Description:
 *
 * Copyright (c) 2026 by Senthie email: seemoon2077@gmail.com, All Rights Reserved.
 */

import { defineStore } from 'pinia'
import { IUploadedImage } from 'src/interfaces/IFile'
import { computed, ref } from 'vue'
import { Notify } from "quasar"
import { v1_file_upload } from "src/apis/file_api"
export const useImageFileStore = defineStore('image_file', () => {
    const upload_file = ref<IUploadedImage | null>(null)


    const imagePreviewUrl = computed(
        () => upload_file.value?.preview_url ?? null,
    )
    const file_size_text = computed(() => {
        if (!upload_file.value?.file) return ""
        const bytes = upload_file.value.file.size
        if (bytes < 1024) return `${bytes} B`
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
        return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
    })

    /**
     * @ 上传文件到后端
     * @returns id 文件的id
     */
    async function post_in_server() {
        if (upload_file.value?.file) {
            const res = await v1_file_upload(upload_file.value?.file)
            return res.data.id
        } else {
            Notify.create({
                type: "negative",
                message: "请先上传文件",
            })
        }
    }

    // 设置文件
    function processFile(file: File) {
        const allowedTypes = [
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "image/svg+xml",
        ]
        if (!allowedTypes.includes(file.type)) {
            alert("请上传 JPG、PNG、GIF、WebP 或 SVG 格式的图片")
            return
        }
        if (file.size > 10 * 1024 * 1024) {
            alert("图片大小不能超过 10MB")
            return
        }

        // 释放旧的预览 URL
        if (upload_file.value) {
            URL.revokeObjectURL(upload_file.value.preview_url)
        }

        upload_file.value = {
            file,
            preview_url: URL.createObjectURL(file),
        }


    }

    // 移除文件
    const removeImage = () => {
        if (!upload_file.value) return
        URL.revokeObjectURL(upload_file.value.preview_url)
        upload_file.value = null
    }
    return { upload_file, post_in_server, processFile, removeImage, imagePreviewUrl, file_size_text }
})