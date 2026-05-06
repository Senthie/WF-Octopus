export interface IPageReq {
    total: number
    size: number
    current: number
    orders: string[]
    maxLimit: number
}

export interface IPageRes<T> {
    records: T[]
    total: number
    size: number
    current: number
    orders: string[]
    maxLimit: number
}
