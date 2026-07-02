import axios from 'axios'
import type { AxiosAdapter, AxiosInstance } from 'axios'

export type AxiosClientOptions = {
  adapter?: AxiosAdapter
  baseURL?: string
}

export function createAxiosClient(options: AxiosClientOptions = {}): AxiosInstance {
  return axios.create({
    adapter: options.adapter,
    baseURL: options.baseURL,
  })
}

export const axiosClient = createAxiosClient()
