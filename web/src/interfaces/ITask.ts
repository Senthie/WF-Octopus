import * as z from 'zod'

const DramatiqTaskStatusEnum = z.enum([
    'pending',
    'started',
    'success',
    'failure',
    'retry',
    'revoked',
]);

export const taskRecordBaseOutSchema = z.object({
    task_id: z.string(),
    task_name: z.string(),
    args: z.array(z.any()).optional(),        // Optional[list] -> 任意数组
    kwargs: z.record(z.any(), z.any()).optional(),     // Optional[dict] -> 任意键值对象
    status: DramatiqTaskStatusEnum.default('pending'),
    result: z.record(z.any(), z.any()).optional(),     // Optional[dict]
    error: z.string().optional().nullable(),  // Optional[str], 允许 null
    worker_hostname: z.string().optional().nullable(),
    started_at: z.string().datetime().optional(),
    ended_at: z.string().datetime().optional().nullable(),
    related_record_id: z.string().uuid().optional().nullable(),
});

// 导出 TypeScript 类型
export type TaskRecordBaseOut = z.infer<typeof taskRecordBaseOutSchema>;

