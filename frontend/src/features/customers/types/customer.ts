export type CustomerStatus = 'active' | 'disabled'

export type Customer = {
  id: number
  name: string
  taxId: string
  email: string | null
  phone: string | null
  status: CustomerStatus
}

export type CustomerSearchParams = {
  name?: string
  taxId?: string
  email?: string
  page?: number
  pageSize?: number
}
