// Zod schemas belong here once frontend dependencies are installed.
// Keep request/response validation aligned with openspec/specs/customer/spec.md.
export const customerSchemaNames = {
  create: 'CustomerCreateSchema',
  update: 'CustomerUpdateSchema',
  search: 'CustomerSearchSchema',
} as const
