import { APIClient } from './client';

// Types
interface Restaurant {
    id: string;
    name: string;
    cuisine: string;
    rating: number;
    // Add other restaurant fields
}

interface UserPreferences {
    dietary: string[];
    cuisinePreferences: string[];
    priceRange: string;
    // Add other preference fields
}

interface Review {
    id: string;
    restaurantId: string;
    userId: string;
    rating: number;
    comment: string;
    // Add other review fields
}

// Create API client instance
const apiClient = new APIClient({
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
});

// Restaurant Service
export const restaurantService = {
    getRecommendations: (preferences: UserPreferences) =>
        apiClient.post<Restaurant[]>('/api/v1/restaurants/recommendations', preferences),
    
    getRestaurant: (id: string) =>
        apiClient.get<Restaurant>(`/api/v1/restaurants/${id}`),
    
    searchRestaurants: (query: string) =>
        apiClient.get<Restaurant[]>('/api/v1/restaurants/search', {
            params: { q: query },
        }),
};

// User Preferences Service
export const preferencesService = {
    getUserPreferences: () =>
        apiClient.get<UserPreferences>('/api/v1/preferences'),
    
    updatePreferences: (preferences: UserPreferences) =>
        apiClient.put<UserPreferences>('/api/v1/preferences', preferences),
};

// Reviews Service
export const reviewsService = {
    getRestaurantReviews: (restaurantId: string) =>
        apiClient.get<Review[]>(`/api/v1/restaurants/${restaurantId}/reviews`),
    
    createReview: (restaurantId: string, review: Omit<Review, 'id' | 'restaurantId'>) =>
        apiClient.post<Review>(`/api/v1/restaurants/${restaurantId}/reviews`, review),
    
    updateReview: (reviewId: string, review: Partial<Review>) =>
        apiClient.put<Review>(`/api/v1/reviews/${reviewId}`, review),
    
    deleteReview: (reviewId: string) =>
        apiClient.delete<void>(`/api/v1/reviews/${reviewId}`),
};

// Authentication Service
export const authService = {
    login: (credentials: { email: string; password: string }) =>
        apiClient.post<{ token: string }>('/api/auth/login', credentials),
    
    register: (userData: { email: string; password: string; name: string }) =>
        apiClient.post<{ token: string }>('/api/auth/register', userData),
    
    logout: () => {
        localStorage.removeItem('auth_token');
        window.location.href = '/login';
    },
}; 