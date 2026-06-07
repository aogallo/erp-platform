import type { Customer, CustomerSearchParams } from '../types'
import type { Page } from '../../../shared/pagination'

export const CUSTOMER_ROUTE_PREFIX = '/crm/customers'

export async function searchCustomers(_params: CustomerSearchParams): Promise<Page<Customer>> {
  throw new Error('HTTP client is not configured yet')
}

export async function getCustomer(_customerId: number): Promise<Customer> {
  throw new Error('HTTP client is not configured yet')
}
