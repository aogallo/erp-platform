import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { customerQueryKeys } from '../api/queryKeys'
import { CustomerListPlaceholder } from './CustomerListPlaceholder'

describe('customer feature scaffold', () => {
  it('renders the CRM customer section with accessible labeling', () => {
    render(<CustomerListPlaceholder />)

    expect(screen.getByRole('region', { name: 'Customers' })).toHaveTextContent(
      'Customer list scaffold',
    )
  })

  it('uses bounded-context query keys for customer server state', () => {
    expect(customerQueryKeys.detail(7)).toEqual(['crm', 'customers', 'detail', 7])
  })
})
