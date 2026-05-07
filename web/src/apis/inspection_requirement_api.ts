import { api } from 'src/boot/axios'
import type { IResponse } from 'src/interfaces/IResponse'
import { Notify } from 'quasar'
import { extractErrorMessage } from 'src/utils/errorHandler'
import { inspection_requirement_add_schema, type IAddInspectionRequirement, type IInspectionRequirementRes } from 'src/interfaces/IInspection'
import type { IPageReq, IPageRes } from 'src/interfaces/Ipage'

export async function v1_add(
    request: IAddInspectionRequirement
): Promise<IResponse<IInspectionRequirementRes>> {
    try {
        const response = await api.post<IResponse<IInspectionRequirementRes>>(
            '/v1/inspection-requirement/',
            request
        )

        // 无论成功还是失败都显示消息
        if (response.data.code !== 200) {
            Notify.create({
                type: 'negative',
                message: response.data.msg || '新增检测要求失败',
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
            data: {} as IInspectionRequirementRes,
            timestamp: new Date().toISOString(),
        }
    }
}

export async function v1_delete(
    id: string
): Promise<IResponse<IInspectionRequirementRes>> {
    try {
        const response = await api.delete<IResponse<IInspectionRequirementRes>>(
            `/v1/inspection-requirement/${id}`,
        )

        // 无论成功还是失败都显示消息
        if (response.data.code !== 200) {
            Notify.create({
                type: 'negative',
                message: response.data.msg || '删除失败',
            })
        } else {
            Notify.create({
                type: 'positive',
                message: "删除成功",
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
            data: {} as IInspectionRequirementRes,
            timestamp: new Date().toISOString(),
        }
    }
}

export async function v1_update(id: string, request: IAddInspectionRequirement) {
    try {
        request = inspection_requirement_add_schema.parse(request)
        const response = await api.put<IResponse<IInspectionRequirementRes>>(
            `/v1/inspection-requirement/${id}`,
            request
        )

        // 无论成功还是失败都显示消息
        if (response.data.code !== 200) {
            Notify.create({
                type: 'negative',
                message: response.data.msg,
            })
        } else {
            Notify.create({
                type: 'positive',
                message: "更新成功",
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
            data: {} as IInspectionRequirementRes,
            timestamp: new Date().toISOString(),
        }
    }
}

export async function v1_list(
    request: IPageReq
): Promise<IResponse<IPageRes<IInspectionRequirementRes>>> {
    try {
        const response = await api.post<IResponse<IPageRes<IInspectionRequirementRes>>>(
            '/v1/inspection-requirement/list',
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
            data: {} as IPageRes<IInspectionRequirementRes>,
            timestamp: new Date().toISOString(),
        }
    }
}

