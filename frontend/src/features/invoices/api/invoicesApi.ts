import type { Invoice, InvoiceSearchParams } from '../types'
import type { Page } from '../../../shared/pagination'

export const INVOICE_ROUTE_PREFIX = '/sales/invoices'

export async function searchInvoices(_params: InvoiceSearchParams): Promise<Page<Invoice>> {
  throw new Error('HTTP client is not configured yet')
}

export async function getInvoice(_invoiceId: number): Promise<Invoice> {
  throw new Error('HTTP client is not configured yet')
}
