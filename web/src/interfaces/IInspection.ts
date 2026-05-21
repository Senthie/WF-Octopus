import * as z from 'zod'
import { taskRecordBaseOutSchema } from './ITask'
import { InspectionResultEnumSchema } from 'src/enums/InspectionEnum'
export const inspection_requirement_add_schema = z.object({
    item_name: z.string(),
    safety_requirement: z.string()
})

export type IAddInspectionRequirement = z.infer<typeof inspection_requirement_add_schema>

export const inspection_requirement_res_schema = z.object({
    id: z.uuidv4(),
    created_by: z.uuidv4(),
    created_at: z.date(),

    updated_by: z.uuidv4(),
    updated_at: z.date(),

    item_name: z.string(),
    safety_requirement: z.string()
})

export type IInspectionRequirementRes = z.infer<typeof inspection_requirement_res_schema>



export const add_inspection_record_schema = z.object({
    // inspection_requirements_ids: z.array(z.uuidv4()),
    inspection_requirements_id: z.uuidv4(),
    file_id: z.uuid(),
    responsible_person: z.string()
})


export type IInspectionRecordIn = z.infer<typeof add_inspection_record_schema>

export const inspection_record_out_schema = z.object({
    id: z.uuidv4(),
    created_by: z.uuidv4(),
    created_at: z.date(),

    updated_by: z.uuidv4(),
    updated_at: z.date(),

    inspection_requirements_id: z.uuidv4(),
    status: z.enum(['normal', 'requires_correction', 'in_progress', 'corrected']),
    file_id: z.uuid(),
    ai_detection_execute_id: z.uuid(),
    ai_inspection_excute_id: z.uuid(),
    responsible_person: z.string(),

    ai_detection_execute: taskRecordBaseOutSchema,
    ai_inspection_excute: taskRecordBaseOutSchema,
    created_by_user: z.string(),
    updated_by_user: z.string(),
})

export type IInspectionRecordOut = z.infer<typeof inspection_record_out_schema>

/**
 * 巡检记录更新输入模型
 * 对应 Pydantic 的 InspectionRecordUpdateIn
 */
export const inspectionRecordUpdateInSchema = z.object({
    // 巡检要求明细表的唯一标识符
    inspection_requirements_id: z.uuidv4(),

    // 巡检的状态（必填，值限定为枚举选项）
    status: InspectionResultEnumSchema,

    // 区域负责人
    responsible_person: z.string(),

    // 人为修改 AI 执行图片分析的结果
    ai_detection_execute_result: z.string(),

    // 人为修改 AI 提取的特定巡检项目结果
    ai_inspection_excute_result: z.string(),
});

// 导出 TypeScript 类型
export type InspectionRecordUpdateIn = z.infer<typeof inspectionRecordUpdateInSchema>;