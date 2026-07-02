import { z } from 'zod'

export const storedTokenSchema = z.object({
  accessToken: z.string().min(1),
  expiresAt: z.string().datetime({ offset: true }),
  scope: z.string().min(1).optional(),
  tokenType: z.literal('Bearer'),
})
