import { api } from 'src/boot/axios'
import type { IResponse } from 'src/interfaces/IResponse'
import { Notify } from 'quasar'
import { extractErrorMessage } from 'src/utils/errorHandler'
import { IInspectionRecordIn, InspectionRecordOut } from 'src/interfaces/IInspection'



export async function v1_add(
    request: IInspectionRecordIn
): Promise<IResponse<InspectionRecordOut>> {
    try {
        const response = await api.post<IResponse<InspectionRecordOut>>(
            '/v1/ai-inspection/',
            request
        )
        // 无论成功还是失败都显示消息
        if (response.data.code !== 200) {
            Notify.create({
                type: 'negative',
                message: response.data.msg || '新增检测要求失败',
            })
        } else {
            Notify.create({
                type: 'positive',
                message: '添加记录成功',
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
            data: {} as InspectionRecordOut,
            timestamp: new Date().toISOString(),
        }
    }
}