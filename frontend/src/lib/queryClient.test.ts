import { describe, expect, it } from 'vitest'

import { createQueryClient, queryClient } from './queryClient'

describe('shared TanStack Query client', () => {
  it('creates an application-wide QueryClient with stable defaults', () => {
    const client = createQueryClient()
    const defaults = client.getDefaultOptions()

    expect(defaults.queries?.refetchOnWindowFocus).toBe(false)
    expect(defaults.queries?.retry).toBe(1)
    expect(defaults.queries?.staleTime).toBe(60_000)
  })

  it('exports a shared QueryClient instance for the future app entry point', () => {
    expect(queryClient.getDefaultOptions().queries?.staleTime).toBe(60_000)
  })
})
