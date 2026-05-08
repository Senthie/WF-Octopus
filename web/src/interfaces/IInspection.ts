import * as z from 'zod'
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