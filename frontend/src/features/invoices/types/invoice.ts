export type InvoiceStatus = 'draft' | 'posted_pending_fel' | 'fel_authorized' | 'fel_failed' | 'credited'

export type InvoiceLine = {
  productId: number
  quantity: string
  unitPrice: string
}

export type Invoice = {
  id: number
  customerId: number
  status: InvoiceStatus
  lines: InvoiceLine[]
  felUuid: string | null
  felDocumentNumber: string | null
}

export type InvoiceSearchParams = {
  customerId?: number
  status?: InvoiceStatus
  dateFrom?: string
  dateTo?: string
  page?: number
  pageSize?: number
}
