// Zod schemas belong here once frontend dependencies are installed.
// Keep validation aligned with openspec/specs/invoice/spec.md.
export const invoiceSchemaNames = {
  createDraft: 'InvoiceCreateDraftSchema',
  post: 'InvoicePostSchema',
  creditNote: 'InvoiceCreditNoteSchema',
  search: 'InvoiceSearchSchema',
} as const
