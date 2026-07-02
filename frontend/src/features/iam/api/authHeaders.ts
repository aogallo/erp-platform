export function createAuthorizationHeader(accessToken: string): { Authorization: string } {
  return {
    Authorization: `Bearer ${accessToken}`,
  }
}

function normalizeHeaders(headers: HeadersInit | undefined): Record<string, string> {
  if (headers === undefined) {
    return {}
  }

  if (!(headers instanceof Headers) && !Array.isArray(headers)) {
    return headers
  }

  return Object.fromEntries(new Headers(headers).entries())
}

export function createAuthenticatedRequestInit(
  init: RequestInit,
  accessToken: string,
): RequestInit {
  return {
    ...init,
    headers: {
      ...normalizeHeaders(init.headers),
      ...createAuthorizationHeader(accessToken),
    },
  }
}
