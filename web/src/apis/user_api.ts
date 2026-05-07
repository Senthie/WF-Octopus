/*
 * @Author: Senthie seemoon2077@gmail.com
 * @Date: 2026-01-06 14:30:33
 * @LastEditors: Senthie seemoon2077@gmail.com
 * @LastEditTime: 2026-01-09 15:29:05
 * @FilePath: /web/src/apis/auth_api.ts
 * @Description: Auth 的 api 请求
 *
 * Copyright (c) 2026 by Senthie email: seemoon2077@gmail.com, All Rights Reserved.
 */
import { api } from 'src/boot/axios'
import type {
    ILogin,
    ILoginRes,
    IRegister,
    IRegisterRes,
    ITokenPair,
} from 'src/interfaces/IAuth'
import type { IResponse } from 'src/interfaces/IResponse'
import { Notify } from 'quasar'
import { extractErrorMessage } from 'src/utils/errorHandler'
/**
 * 根据用户ids 获取对应的用户名
 * @param ids String[] 用户唯一标识列表
 * @returns Promise<IResponse<IRegisterRes>> 注册响应数据
 */
export async function v1_get_usernames_by_ids(
    ids: Set<String>
): Promise<IResponse<Record<string, string>>> {
    let ids_list = Array.from(ids);
    try {
        const response = await api.post<IResponse<Record<string, string>>>(
            '/v1/user/usernames',
            ids_list
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
            data: {},
            timestamp: new Date().toISOString(),
        }
    }
}

/**
 * 用户登录
 * @param request 登录请求参数
 * @returns Promise<IResponse<ILoginRes>> 登录响应数据
 */
export async function v1_auth_login(
    request: ILogin
): Promise<IResponse<ILoginRes>> {
    try {
        const response = await api.post<IResponse<ILoginRes>>(
            '/v1/auth/login',
            request
        )

        // 无论成功还是失败都显示消息
        if (response.data.code !== 200) {
            Notify.create({
                type: 'negative',
                message: response.data.msg || '登录失败',
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
            data: {} as ILoginRes,
            timestamp: new Date().toISOString(),
        }
    }
}

/**
 * 刷新访问令牌
 * @param request 刷新令牌请求参数
 * @returns Promise<IResponse<ITokenRefreshRes>> 刷新令牌响应数据
 */
export async function v1_auth_refresh(request: {
    refresh_token: string
}): Promise<IResponse<ITokenPair>> {
    try {
        const response = await api.post<IResponse<ITokenPair>>(
            '/v1/auth/refresh',
            request
        )

        if (response.data.code !== 200) {
            Notify.create({
                type: 'negative',
                message: response.data.msg || '刷新令牌失败',
            })
        }

        return response.data
    } catch (error) {
        const errorMessage = extractErrorMessage(error)

        Notify.create({
            type: 'negative',
            message: errorMessage,
        })

        return {
            code: 500,
            msg: errorMessage,
            data: {
                access_token: '',
                refresh_token: '',
                token_type: '',
                expires_in: 0,
            },
            timestamp: new Date().toISOString(),
        }
    }
}