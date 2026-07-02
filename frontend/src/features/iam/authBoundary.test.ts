import { describe, expect, it } from 'vitest'

import {
  AUTH0_PKCE_RESPONSE_TYPE,
  axiosClient,
  buildAuth0PkceLoginUrl,
  createApiClient,
  createAxiosClient,
  createPkceCodeChallenge,
  createAuthorizationHeader,
  createAuthenticatedRequestInit,
  createMemoryTokenStorage,
  storedTokenSchema,
} from './index'

function getConfigHeader(headers: unknown, name: string): unknown {
  if (headers === null || typeof headers !== 'object') {
    return undefined
  }

  if ('get' in headers && typeof headers.get === 'function') {
    return headers.get(name)
  }

  return (headers as Record<string, unknown>)[name]
}

describe('IAM Auth0 PKCE boundary', () => {
  it('builds an Auth0 authorization URL for the ERP API audience with PKCE challenge', async () => {
    const url = await buildAuth0PkceLoginUrl(
      {
        audience: 'https://api.erp.test',
        clientId: 'erp-spa-client',
        domain: 'tenant.auth0.com',
        redirectUri: 'https://erp.test/auth/callback',
        scopes: ['openid', 'profile', 'email'],
      },
      {
        createCodeChallenge: async (verifier) => `challenge-for-${verifier}`,
        createCodeVerifier: () => 'verifier-123',
        createState: () => 'state-abc',
      },
    )

    expect(url.authorizationUrl.origin).toBe('https://tenant.auth0.com')
    expect(url.authorizationUrl.pathname).toBe('/authorize')
    expect(url.authorizationUrl.searchParams.get('audience')).toBe('https://api.erp.test')
    expect(url.authorizationUrl.searchParams.get('client_id')).toBe('erp-spa-client')
    expect(url.authorizationUrl.searchParams.get('code_challenge')).toBe(
      'challenge-for-verifier-123',
    )
    expect(url.authorizationUrl.searchParams.get('code_challenge_method')).toBe('S256')
    expect(url.authorizationUrl.searchParams.get('redirect_uri')).toBe(
      'https://erp.test/auth/callback',
    )
    expect(url.authorizationUrl.searchParams.get('response_type')).toBe(
      AUTH0_PKCE_RESPONSE_TYPE,
    )
    expect(url.authorizationUrl.searchParams.get('scope')).toBe('openid profile email')
    expect(url.authorizationUrl.searchParams.get('state')).toBe('state-abc')
    expect(url.codeVerifier).toBe('verifier-123')
    expect(url.state).toBe('state-abc')
  })

  it('normalizes Auth0 domains before building the hosted login URL', async () => {
    const url = await buildAuth0PkceLoginUrl(
      {
        audience: 'erp-api',
        clientId: 'client-1',
        domain: 'https://tenant.auth0.com/',
        redirectUri: 'https://erp.test/callback',
        scopes: ['openid'],
      },
      {
        createCodeChallenge: async () => 'challenge-1',
        createCodeVerifier: () => 'verifier-1',
        createState: () => 'state-1',
      },
    )

    expect(url.authorizationUrl.href).toBe(
      'https://tenant.auth0.com/authorize?response_type=code&client_id=client-1&redirect_uri=https%3A%2F%2Ferp.test%2Fcallback&audience=erp-api&scope=openid&state=state-1&code_challenge=challenge-1&code_challenge_method=S256',
    )
  })

  it('normalizes HTTP scheme and scheme casing before building the hosted login URL', async () => {
    const url = await buildAuth0PkceLoginUrl(
      {
        audience: 'erp-api',
        clientId: 'client-1',
        domain: 'HTTP://tenant.auth0.com/',
        redirectUri: 'https://erp.test/callback',
        scopes: ['openid'],
      },
      {
        createCodeChallenge: async () => 'challenge-1',
        createCodeVerifier: () => 'verifier-1',
        createState: () => 'state-1',
      },
    )

    expect(url.authorizationUrl.origin).toBe('https://tenant.auth0.com')
    expect(url.authorizationUrl.pathname).toBe('/authorize')
  })

  it('creates the RFC 7636 S256 code challenge from a verifier', async () => {
    const challenge = await createPkceCodeChallenge(
      'dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk',
    )

    expect(challenge).toBe('E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM')
  })
})

describe('IAM token storage boundary', () => {
  it('stores and loads a valid bearer access token through a replaceable storage adapter', () => {
    const storage = createMemoryTokenStorage()
    const token = {
      accessToken: 'access-token-123',
      expiresAt: '2026-07-01T18:00:00.000Z',
      scope: 'openid profile email',
      tokenType: 'Bearer',
    } as const

    storage.save(token)

    expect(storage.load()).toEqual(token)
  })

  it('rejects invalid token payloads instead of leaking malformed auth state', () => {
    const result = storedTokenSchema.safeParse({
      accessToken: '',
      expiresAt: 'not-a-date',
      tokenType: 'Basic',
    })

    expect(result.success).toBe(false)
  })
})

describe('IAM API bearer token attachment', () => {
  it('creates an Authorization header for ERP API requests', () => {
    expect(createAuthorizationHeader('access-token-123')).toEqual({
      Authorization: 'Bearer access-token-123',
    })
  })

  it('preserves existing request headers while attaching the bearer token', () => {
    const request = createAuthenticatedRequestInit(
      {
        headers: {
          'Content-Type': 'application/json',
        },
        method: 'POST',
      },
      'access-token-123',
    )

    expect(request).toEqual({
      headers: {
        Authorization: 'Bearer access-token-123',
        'Content-Type': 'application/json',
      },
      method: 'POST',
    })
  })

  it('supports Fetch Headers objects when attaching the bearer token', () => {
    const request = createAuthenticatedRequestInit(
      {
        headers: new Headers({
          Accept: 'application/json',
        }),
        method: 'GET',
      },
      'access-token-456',
    )

    const headers = new Headers(request.headers)
    expect(headers.get('Accept')).toBe('application/json')
    expect(headers.get('Authorization')).toBe('Bearer access-token-456')
  })
})

describe('IAM Axios API client', () => {
  it('uses the shared Axios client factory from src/lib', () => {
    const client = createAxiosClient({ baseURL: 'https://api.erp.test' })

    expect(client.defaults.baseURL).toBe('https://api.erp.test')
    expect(axiosClient.defaults).toBeDefined()
  })

  it('attaches the current bearer token through a request interceptor', async () => {
    const tokenStorage = createMemoryTokenStorage()
    tokenStorage.save({
      accessToken: 'access-token-123',
      expiresAt: '2026-07-01T18:00:00.000Z',
      tokenType: 'Bearer',
    })
    const client = createApiClient({
      adapter: async (config) => ({
        config,
        data: { ok: true },
        headers: {},
        status: 200,
        statusText: 'OK',
      }),
      baseURL: 'https://api.erp.test',
      tokenStorage,
    })

    const response = await client.get('/crm/customers')

    expect(getConfigHeader(response.config.headers, 'Authorization')).toBe(
      'Bearer access-token-123',
    )
  })

  it('does not add an Authorization header when no token is stored', async () => {
    const client = createApiClient({
      adapter: async (config) => ({
        config,
        data: { ok: true },
        headers: {},
        status: 200,
        statusText: 'OK',
      }),
      baseURL: 'https://api.erp.test',
      tokenStorage: createMemoryTokenStorage(),
    })

    const response = await client.get('/crm/customers')

    expect(getConfigHeader(response.config.headers, 'Authorization')).toBeUndefined()
  })

  it('preserves existing Axios headers while attaching the bearer token', async () => {
    const tokenStorage = createMemoryTokenStorage()
    tokenStorage.save({
      accessToken: 'access-token-456',
      expiresAt: '2026-07-01T18:00:00.000Z',
      tokenType: 'Bearer',
    })
    const client = createApiClient({
      adapter: async (config) => ({
        config,
        data: { ok: true },
        headers: {},
        status: 200,
        statusText: 'OK',
      }),
      tokenStorage,
    })

    const response = await client.get('/sales/invoices', {
      headers: {
        'X-Trace-Id': 'trace-123',
      },
    })

    expect(getConfigHeader(response.config.headers, 'X-Trace-Id')).toBe('trace-123')
    expect(getConfigHeader(response.config.headers, 'Authorization')).toBe(
      'Bearer access-token-456',
    )
  })

  it('reads token updates dynamically for each request', async () => {
    const tokenStorage = createMemoryTokenStorage()
    const seenAuthorizationHeaders: unknown[] = []
    const client = createApiClient({
      adapter: async (config) => {
        seenAuthorizationHeaders.push(getConfigHeader(config.headers, 'Authorization'))

        return {
          config,
          data: { ok: true },
          headers: {},
          status: 200,
          statusText: 'OK',
        }
      },
      tokenStorage,
    })

    tokenStorage.save({
      accessToken: 'first-token',
      expiresAt: '2026-07-01T18:00:00.000Z',
      tokenType: 'Bearer',
    })
    await client.get('/crm/customers')
    tokenStorage.save({
      accessToken: 'second-token',
      expiresAt: '2026-07-01T18:00:00.000Z',
      tokenType: 'Bearer',
    })
    await client.get('/crm/customers')

    expect(seenAuthorizationHeaders).toEqual([
      'Bearer first-token',
      'Bearer second-token',
    ])
  })
})
