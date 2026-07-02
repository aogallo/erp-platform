import type { Auth0PkceConfig, PkceLoginDependencies, PkceLoginRequest } from '../types'

export const AUTH0_PKCE_RESPONSE_TYPE = 'code'

function normalizeAuth0Domain(domain: string): string {
  return domain.replace(/^https:\/\//, '').replace(/\/$/, '')
}

function base64UrlEncode(bytes: Uint8Array): string {
  const binary = String.fromCharCode(...bytes)
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}

export async function createPkceCodeChallenge(codeVerifier: string): Promise<string> {
  const encodedVerifier = new TextEncoder().encode(codeVerifier)
  const digest = await crypto.subtle.digest('SHA-256', encodedVerifier)

  return base64UrlEncode(new Uint8Array(digest))
}

export async function buildAuth0PkceLoginUrl(
  config: Auth0PkceConfig,
  dependencies: PkceLoginDependencies,
): Promise<PkceLoginRequest> {
  const codeVerifier = dependencies.createCodeVerifier()
  const codeChallenge = await dependencies.createCodeChallenge(codeVerifier)
  const state = dependencies.createState()
  const authorizationUrl = new URL(`https://${normalizeAuth0Domain(config.domain)}/authorize`)

  authorizationUrl.searchParams.set('response_type', AUTH0_PKCE_RESPONSE_TYPE)
  authorizationUrl.searchParams.set('client_id', config.clientId)
  authorizationUrl.searchParams.set('redirect_uri', config.redirectUri)
  authorizationUrl.searchParams.set('audience', config.audience)
  authorizationUrl.searchParams.set('scope', config.scopes.join(' '))
  authorizationUrl.searchParams.set('state', state)
  authorizationUrl.searchParams.set('code_challenge', codeChallenge)
  authorizationUrl.searchParams.set('code_challenge_method', 'S256')

  return {
    authorizationUrl,
    codeVerifier,
    state,
  }
}
