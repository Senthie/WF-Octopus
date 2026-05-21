import { api } from 'src/boot/axios'
import type { IResponse } from 'src/interfaces/IResponse'
import { Notify } from 'quasar'
import { extractErrorMessage } from 'src/utils/errorHandler'
import { IFileReferenceOut } from 'src/interfaces/IFile'

/**
 * 用户注册
 * @param request 注册请求参数
 * @returns Promise<IResponse<IRegisterRes>> 注册响应数据
 */
export async function v1_file_upload(
    file: File
): Promise<IResponse<IFileReferenceOut>> {
    try {
        // 创建 FormData 对象
        const formData = new FormData()
        formData.append('file', file)
        const response = await api.post<IResponse<IFileReferenceOut>>(
            '/v1/file/upload',
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            }
        )

        // 无论成功还是失败都显示消息
        if (response.data.code !== 200) {
            Notify.create({
                type: 'negative',
                message: response.data.msg,
            })
        }

        return response.data
    } catch (error) {
        const errorMessage = extractErrorMessage(error)

        Notify.create({
            type: 'negative',
            message: errorMessage,
        })

        // 返回一个错误响应格式
        return {
            code: 500,
            msg: errorMessage,
            data: {} as IFileReferenceOut,
            timestamp: new Date().toISOString(),
        }
    }
}

// 获取图片 Blob URL
export async function getImageBlobUrl(fileId: string): Promise<string> {
    // 注意要指定 responseType 为 blob
    const res = await api.get(`/v1/file/${fileId}/url`, { responseType: 'blob' })
    // 从 blob 创建临时 URL
    return URL.createObjectURL(res.data)
}