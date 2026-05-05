import * as z from 'zod'

export const user_login_schema = z.object({
    email: z.string(),
    password: z.string().min(8).max(24)
})

export type ILogin = z.infer<typeof user_login_schema>

export const register_schema = z.object({
    email: z.string(),
    password: z.string().min(8).max(24),
    name: z.string()
})

export type IRegister = z.infer<typeof register_schema>

export const token_pair_schema = z.object({
    access_token: z.string(),
    refresh_token: z.string(),
    token_type: z.string(),
    expires_in: z.number()

})
export type ITokenPair = z.infer<typeof token_pair_schema>

export const user_res_schema = z.object({
    id: z.uuidv4(),
    email: z.email(),
    name: z.string(),
    avatar_url: z.url(),
    created_at: z.number(),
    updated_at: z.number()

})

export type IUserRes = z.infer<typeof user_res_schema>

export const register_res_schema = z.object({
    user: user_res_schema,
    tokens: token_pair_schema
})
export type IRegisterRes = z.infer<typeof register_res_schema>
export type ILoginRes = z.infer<typeof register_res_schema>
