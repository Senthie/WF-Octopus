import { z } from 'zod';

export const InspectionResultEnumSchema = z.enum([
    'normal',
    'requires_correction',
    'in_progress',
    'corrected',
]);

// 导出类型
export type InspectionResultEnumType = z.infer<typeof InspectionResultEnumSchema>;