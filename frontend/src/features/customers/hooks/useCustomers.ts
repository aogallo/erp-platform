import { customerQueryKeys } from '../api'
import type { CustomerSearchParams } from '../types'

export function getCustomersQueryKey(params: CustomerSearchParams) {
  return customerQueryKeys.list(params)
}

// Future TanStack Query hook belongs here once frontend tooling is installed.
