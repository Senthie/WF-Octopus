import { api } from 'src/boot/axios'
import type { IResponse } from 'src/interfaces/IResponse'
import { Notify } from 'quasar'
import { extractErrorMessage } from 'src/utils/errorHandler'
import { IInspectionRecordIn, IInspectionRecordOut, InspectionRecordUpdateIn } from 'src/interfaces/IInspection'
import { IPageReq, IPageRes } from 'src/interfaces/Ipage'



export async function v1_add(
    request: IInspectionRecordIn
): Promise<IResponse<IInspectionRecordOut>> {
    try {
        const response = await api.post<IResponse<IInspectionRecordOut>>(
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
            data: {} as IInspectionRecordOut,
            timestamp: new Date().toISOString(),
        }
    }
}

export async function ai_inspection_v1_list(
    request: IPageReq
): Promise<IResponse<IPageRes<IInspectionRecordOut>>> {
    try {
        const response = await api.post<IResponse<IPageRes<IInspectionRecordOut>>>(
            '/v1/ai-inspection/list',
            request
        )

        // 无论成功还是失败都显示消息
        if (response.data.code !== 200) {
            Notify.create({
                type: 'negative',
                message: response.data.msg || '获取数据失败',
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
            data: {} as IPageRes<IInspectionRecordOut>,
            timestamp: new Date().toISOString(),
        }
    }
}

export async function v1_update(id: string,
    request: InspectionRecordUpdateIn
): Promise<IResponse<IInspectionRecordOut>> {
    try {
        const response = await api.put<IResponse<IInspectionRecordOut>>(
            `/v1/ai-inspection/${id}`,
            request
        )
        // 无论成功还是失败都显示消息
        if (response.data.code !== 200) {
            Notify.create({
                type: 'negative',
                message: response.data.msg || '修改检测要求失败',
            })
        } else {
            Notify.create({
                type: 'positive',
                message: '修改记录成功',
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
            data: {} as IInspectionRecordOut,
            timestamp: new Date().toISOString(),
        }
    }
}
export async function v1_delete(id: string,
): Promise<IResponse<IInspectionRecordOut>> {
    try {
        const response = await api.delete<IResponse<IInspectionRecordOut>>(
            `/v1/ai-inspection/${id}`,
        )
        // 无论成功还是失败都显示消息
        if (response.data.code !== 200) {
            Notify.create({
                type: 'negative',
                message: response.data.msg || '删除检测要求失败',
            })
        } else {
            Notify.create({
                type: 'positive',
                message: '删除记录成功',
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
            data: {} as IInspectionRecordOut,
            timestamp: new Date().toISOString(),
        }
    }
}
