import { z } from 'zod';

/**
 * 执行记录输出模型
 */
export const fileReferenceOutSchema = z.object({
    // 唯一标识符，默认由服务端生成（UUID v4）
    id: z.uuidv4(),

    // 创建时间，ISO 8601 格式字符串
    created_at: z.iso.datetime(),

    // 更新时间，ISO 8601 格式字符串
    updated_at: z.iso.datetime(),

    // 逻辑外键 -> users 表
    created_by: z.uuidv4(),

    // 逻辑外键 -> users 表
    updated_by: z.uuidv4(),

    // GridFS 文件 ID
    gridfs_id: z.uuidv4(),

    // 文件名，最大长度 255
    filename: z.string().max(255),

    // 文件 MIME 类型，最大长度 100
    content_type: z.string().max(100),

    // 文件大小（字节）
    size_bytes: z.number().int().nonnegative(),

    // 存储类型：MONGODB（小文件）或 GRIDFS（大文件）
    storage_type: z.enum(['MONGODB', 'GRIDFS']),
});

// 导出 TypeScript 类型（等价于原 Python 模型的类型）
export type IFileReferenceOut = z.infer<typeof fileReferenceOutSchema>;

export const uploaded_image_schema = z.object({
    file: z.file(),
    preview_url: z.url()
})
export type IUploadedImage = z.infer<typeof uploaded_image_schema>;