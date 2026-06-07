import { invoiceQueryKeys } from '../api'
import type { InvoiceSearchParams } from '../types'

export function getInvoicesQueryKey(params: InvoiceSearchParams) {
  return invoiceQueryKeys.list(params)
}

// Future TanStack Query hook belongs here once frontend tooling is installed.
