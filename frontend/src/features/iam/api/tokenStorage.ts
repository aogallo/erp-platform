import { storedTokenSchema } from '../schemas'
import type { StoredToken, TokenStorage } from '../types'

export function createMemoryTokenStorage(): TokenStorage {
  let currentToken: StoredToken | null = null

  return {
    clear: () => {
      currentToken = null
    },
    load: () => currentToken,
    save: (token) => {
      currentToken = storedTokenSchema.parse(token)
    },
  }
}

export const authTokenStorage = createMemoryTokenStorage()
