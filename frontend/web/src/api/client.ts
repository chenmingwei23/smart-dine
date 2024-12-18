import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

interface APIClientConfig {
    baseURL: string;
    timeout?: number;
}

interface RequestConfig extends AxiosRequestConfig {
    skipAuth?: boolean;
    skipCache?: boolean;
}

class APIClient {
    private client: AxiosInstance;
    private cache: Map<string, { data: any; timestamp: number }>;
    private readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

    constructor(config: APIClientConfig) {
        this.client = axios.create({
            baseURL: config.baseURL,
            timeout: config.timeout || 10000,
            headers: {
                'Content-Type': 'application/json',
            },
        });
        this.cache = new Map();
        this.setupInterceptors();
    }

    private setupInterceptors() {
        // Request interceptor
        this.client.interceptors.request.use(
            async (config) => {
                if (!(config as RequestConfig).skipAuth) {
                    const token = localStorage.getItem('auth_token');
                    if (token) {
                        config.headers.Authorization = `Bearer ${token}`;
                    }
                }
                return config;
            },
            (error) => Promise.reject(error)
        );

        // Response interceptor
        this.client.interceptors.response.use(
            (response) => response,
            async (error) => {
                if (error.response?.status === 401) {
                    // Handle token refresh or logout
                    localStorage.removeItem('auth_token');
                    window.location.href = '/login';
                }
                return Promise.reject(error);
            }
        );
    }

    private getCacheKey(config: RequestConfig): string {
        return `${config.method}-${config.url}-${JSON.stringify(config.params || {})}-${JSON.stringify(config.data || {})}`;
    }

    private isCacheValid(timestamp: number): boolean {
        return Date.now() - timestamp < this.CACHE_DURATION;
    }

    async request<T>(config: RequestConfig): Promise<T> {
        const cacheKey = this.getCacheKey(config);

        // Check cache for GET requests
        if (config.method === 'get' && !config.skipCache) {
            const cached = this.cache.get(cacheKey);
            if (cached && this.isCacheValid(cached.timestamp)) {
                return cached.data;
            }
        }

        try {
            const response: AxiosResponse<T> = await this.client.request(config);
            
            // Cache GET responses
            if (config.method === 'get' && !config.skipCache) {
                this.cache.set(cacheKey, {
                    data: response.data,
                    timestamp: Date.now(),
                });
            }

            return response.data;
        } catch (error) {
            // Handle errors and potentially retry requests
            if (axios.isAxiosError(error) && error.response) {
                throw new Error(error.response.data.detail || 'An error occurred');
            }
            throw error;
        }
    }

    // Convenience methods
    async get<T>(url: string, config: Omit<RequestConfig, 'method' | 'url'> = {}): Promise<T> {
        return this.request<T>({ ...config, method: 'get', url });
    }

    async post<T>(url: string, data?: any, config: Omit<RequestConfig, 'method' | 'url' | 'data'> = {}): Promise<T> {
        return this.request<T>({ ...config, method: 'post', url, data });
    }

    async put<T>(url: string, data?: any, config: Omit<RequestConfig, 'method' | 'url' | 'data'> = {}): Promise<T> {
        return this.request<T>({ ...config, method: 'put', url, data });
    }

    async delete<T>(url: string, config: Omit<RequestConfig, 'method' | 'url'> = {}): Promise<T> {
        return this.request<T>({ ...config, method: 'delete', url });
    }
} 