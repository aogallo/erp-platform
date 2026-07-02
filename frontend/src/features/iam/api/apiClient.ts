import type { AxiosAdapter, AxiosInstance } from 'axios'

import { createAxiosClient } from '../../../lib/axiosClient'
import { authTokenStorage } from './tokenStorage'
import type { TokenStorage } from '../types'

export type ApiClientOptions = {
  adapter?: AxiosAdapter
  baseURL?: string
  tokenStorage?: TokenStorage
}

export function createApiClient(options: ApiClientOptions = {}): AxiosInstance {
  const tokenStorage = options.tokenStorage ?? authTokenStorage
  const client = createAxiosClient({
    adapter: options.adapter,
    baseURL: options.baseURL,
  })

  client.interceptors.request.use((config) => {
    const token = tokenStorage.load()

    if (token !== null) {
      config.headers.set('Authorization', `Bearer ${token.accessToken}`)
    }

    return config
  })

  return client
}

export const apiClient = createApiClient()
