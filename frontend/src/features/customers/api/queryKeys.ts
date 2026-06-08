export const customerQueryKeys = {
  all: ['crm', 'customers'] as const,
  lists: () => [...customerQueryKeys.all, 'list'] as const,
  list: (params: unknown) => [...customerQueryKeys.lists(), params] as const,
  detail: (customerId: number) => [...customerQueryKeys.all, 'detail', customerId] as const,
}
