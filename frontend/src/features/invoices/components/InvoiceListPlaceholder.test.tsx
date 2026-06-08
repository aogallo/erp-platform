import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { invoiceQueryKeys } from '../api/queryKeys'
import { InvoiceListPlaceholder } from './InvoiceListPlaceholder'

describe('invoice feature scaffold', () => {
  it('renders the Sales invoice section with accessible labeling', () => {
    render(<InvoiceListPlaceholder />)

    expect(screen.getByRole('region', { name: 'Invoices' })).toHaveTextContent(
      'Invoice list scaffold',
    )
  })

  it('uses bounded-context query keys for invoice server state', () => {
    expect(invoiceQueryKeys.detail(11)).toEqual(['sales', 'invoices', 'detail', 11])
  })
})
