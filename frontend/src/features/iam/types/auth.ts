export type Auth0PkceConfig = {
  audience: string
  clientId: string
  domain: string
  redirectUri: string
  scopes: readonly string[]
}

export type PkceLoginDependencies = {
  createCodeChallenge: (codeVerifier: string) => Promise<string>
  createCodeVerifier: () => string
  createState: () => string
}

export type PkceLoginRequest = {
  authorizationUrl: URL
  codeVerifier: string
  state: string
}

export type StoredToken = {
  accessToken: string
  expiresAt: string
  scope?: string
  tokenType: 'Bearer'
}

export type TokenStorage = {
  clear: () => void
  load: () => StoredToken | null
  save: (token: StoredToken) => void
}
