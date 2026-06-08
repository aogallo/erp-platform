export const invoiceQueryKeys = {
  all: ['sales', 'invoices'] as const,
  lists: () => [...invoiceQueryKeys.all, 'list'] as const,
  list: (params: unknown) => [...invoiceQueryKeys.lists(), params] as const,
  detail: (invoiceId: number) => [...invoiceQueryKeys.all, 'detail', invoiceId] as const,
}
