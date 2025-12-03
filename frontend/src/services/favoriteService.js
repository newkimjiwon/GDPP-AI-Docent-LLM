// File: frontend/src/services/favoriteService.js
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Axios 인스턴스 생성
const api = axios.create({
    baseURL: API_URL,
});

// 요청 인터셉터: 토큰 자동 추가
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

/**
 * 관심상품 목록 조회
 */
export const getFavorites = async () => {
    try {
        const response = await api.get('/api/favorites/');
        return response.data;
    } catch (error) {
        console.error('Failed to fetch favorites:', error);
        throw error;
    }
};

/**
 * 관심상품 추가
 */
export const addFavorite = async (title, url) => {
    try {
        const response = await api.post('/api/favorites/', {
            title: title || '제목 없음',
            url,
        });
        return response.data;
    } catch (error) {
        console.error('Failed to add favorite:', error);
        throw error;
    }
};

/**
 * 관심상품 수정
 */
export const updateFavorite = async (id, title, url) => {
    try {
        const response = await api.put(`/api/favorites/${id}`, {
            title,
            url,
        });
        return response.data;
    } catch (error) {
        console.error('Failed to update favorite:', error);
        throw error;
    }
};

/**
 * 관심상품 삭제
 */
export const deleteFavorite = async (id) => {
    try {
        await api.delete(`/api/favorites/${id}`);
    } catch (error) {
        console.error('Failed to delete favorite:', error);
        throw error;
    }
};
