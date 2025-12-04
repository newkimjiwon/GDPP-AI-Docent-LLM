// File: frontend/src/components/ProductPanel.jsx
import { useState, useEffect } from 'react';
import useAuthStore from '../store/authStore';
import { getFavorites, addFavorite, updateFavorite, deleteFavorite } from '../services/favoriteService';

const GUEST_STORAGE_KEY = 'guest_favorite_products';

export default function ProductPanel({ isOpen = true, onToggle }) {
    const { isAuthenticated } = useAuthStore();
    const [products, setProducts] = useState([]);
    const [url, setUrl] = useState('');
    const [title, setTitle] = useState('');
    const [editingId, setEditingId] = useState(null);
    const [editTitle, setEditTitle] = useState('');
    const [editUrl, setEditUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [syncing, setSyncing] = useState(false);

    // 로컬 스토리지에서 게스트 관심상품 로드
    const loadGuestFavorites = () => {
        try {
            const stored = localStorage.getItem(GUEST_STORAGE_KEY);
            if (stored) {
                return JSON.parse(stored);
            }
        } catch (err) {
            console.error('Failed to load guest favorites:', err);
        }
        return [];
    };

    // 로컬 스토리지에 게스트 관심상품 저장
    const saveGuestFavorites = (favorites) => {
        try {
            localStorage.setItem(GUEST_STORAGE_KEY, JSON.stringify(favorites));
        } catch (err) {
            console.error('Failed to save guest favorites:', err);
        }
    };

    // 게스트 관심상품을 DB로 동기화
    const syncGuestFavoritesToDB = async () => {
        const guestFavorites = loadGuestFavorites();
        if (guestFavorites.length === 0) return;

        setSyncing(true);
        try {
            // 각 게스트 관심상품을 DB에 추가
            for (const favorite of guestFavorites) {
                await addFavorite(favorite.title, favorite.url);
            }
            // 동기화 완료 후 로컬 스토리지 삭제
            localStorage.removeItem(GUEST_STORAGE_KEY);
            console.log('Guest favorites synced to DB');
        } catch (err) {
            console.error('Failed to sync guest favorites:', err);
        } finally {
            setSyncing(false);
        }
    };

    // 컴포넌트 마운트 시 관심상품 로드
    useEffect(() => {
        if (isAuthenticated) {
            loadAuthenticatedFavorites();
        } else {
            // 게스트 모드: 로컬 스토리지에서 로드
            const guestFavorites = loadGuestFavorites();
            setProducts(guestFavorites);
        }
    }, [isAuthenticated]);

    const loadAuthenticatedFavorites = async () => {
        try {
            setLoading(true);
            setError(null);

            // 게스트 데이터가 있으면 먼저 동기화
            await syncGuestFavoritesToDB();

            // DB에서 관심상품 로드
            const data = await getFavorites();
            setProducts(data);
        } catch (err) {
            console.error('Failed to load favorites:', err);
            if (err.response?.status === 401) {
                setError('로그인이 필요합니다');
            } else {
                setError('관심상품을 불러오는데 실패했습니다');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleAddProduct = async () => {
        if (!url.trim()) return;

        const productData = {
            id: Date.now(),
            title: title.trim() || '제목 없음',
            url: url.trim(),
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
        };

        if (isAuthenticated) {
            // 로그인 사용자: DB에 저장
            try {
                setLoading(true);
                setError(null);
                const newProduct = await addFavorite(productData.title, productData.url);
                setProducts([newProduct, ...products]);
                setUrl('');
                setTitle('');
            } catch (err) {
                console.error('Failed to add favorite:', err);
                if (err.response?.status === 401) {
                    alert('로그인이 필요합니다');
                } else {
                    alert('관심상품 추가에 실패했습니다');
                }
            } finally {
                setLoading(false);
            }
        } else {
            // 게스트 사용자: 로컬 스토리지에 저장
            const newProducts = [productData, ...products];
            setProducts(newProducts);
            saveGuestFavorites(newProducts);
            setUrl('');
            setTitle('');
        }
    };

    const handleRemoveProduct = async (id) => {
        if (!confirm('이 관심상품을 삭제하시겠습니까?')) return;

        if (isAuthenticated) {
            // 로그인 사용자: DB에서 삭제
            try {
                setLoading(true);
                setError(null);
                await deleteFavorite(id);
                setProducts(products.filter(p => p.id !== id));
            } catch (err) {
                console.error('Failed to delete favorite:', err);
                alert('관심상품 삭제에 실패했습니다');
            } finally {
                setLoading(false);
            }
        } else {
            // 게스트 사용자: 로컬 스토리지에서 삭제
            const newProducts = products.filter(p => p.id !== id);
            setProducts(newProducts);
            saveGuestFavorites(newProducts);
        }
    };

    const startEdit = (product) => {
        setEditingId(product.id);
        setEditTitle(product.title);
        setEditUrl(product.url);
    };

    const handleSaveEdit = async (id) => {
        if (!editTitle.trim() || !editUrl.trim()) {
            alert('제목과 URL을 입력해주세요');
            return;
        }

        if (isAuthenticated) {
            // 로그인 사용자: DB 업데이트
            try {
                setLoading(true);
                setError(null);
                const updatedProduct = await updateFavorite(id, editTitle.trim(), editUrl.trim());
                setProducts(products.map(p => p.id === id ? updatedProduct : p));
                setEditingId(null);
            } catch (err) {
                console.error('Failed to update favorite:', err);
                alert('관심상품 수정에 실패했습니다');
            } finally {
                setLoading(false);
            }
        } else {
            // 게스트 사용자: 로컬 스토리지 업데이트
            const newProducts = products.map(p =>
                p.id === id
                    ? { ...p, title: editTitle.trim(), url: editUrl.trim(), updated_at: new Date().toISOString() }
                    : p
            );
            setProducts(newProducts);
            saveGuestFavorites(newProducts);
            setEditingId(null);
        }
    };

    const cancelEdit = () => {
        setEditingId(null);
        setEditTitle('');
        setEditUrl('');
    };

    if (!isOpen) {
        return (
            <button
                onClick={onToggle}
                className="fixed top-4 right-4 z-50 p-3 bg-white rounded-lg shadow-lg hover:bg-gray-50 border border-gray-200"
                title="관심 상품 열기"
            >
                <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                </svg>
            </button>
        );
    }

    return (
        <div className="w-96 h-full bg-white border-l border-gray-200 flex flex-col shadow-lg flex-shrink-0">
            {/* Header */}
            <div className="p-4 border-b border-gray-200 flex-shrink-0 bg-gradient-to-r from-purple-50 to-pink-50">
                <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-semibold text-gray-800">
                        🛍️ 관심 상품
                    </h3>
                    <button
                        onClick={onToggle}
                        className="p-2 hover:bg-white/50 rounded-lg transition"
                        title="닫기"
                    >
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* 동기화 중 표시 */}
                {syncing && (
                    <div className="mb-2 p-2 bg-blue-50 border border-blue-200 rounded-lg text-xs text-blue-700">
                        게스트 관심상품을 DB에 동기화 중...
                    </div>
                )}

                {/* 게스트 모드 안내 */}
                {!isAuthenticated && products.length > 0 && (
                    <div className="mb-2 p-2 bg-yellow-50 border border-yellow-200 rounded-lg text-xs text-yellow-700">
                        💡 로그인하면 관심상품이 영구 저장됩니다
                    </div>
                )}

                <div className="space-y-2">
                    <input
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleAddProduct()}
                        placeholder="상품 제목"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                        disabled={loading}
                    />
                    <div className="flex gap-2">
                        <input
                            type="url"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleAddProduct()}
                            placeholder="상품 URL"
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                            disabled={loading}
                        />
                        <button
                            onClick={handleAddProduct}
                            className="bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600 transition text-sm font-medium shadow-sm disabled:opacity-50"
                            disabled={loading}
                        >
                            추가
                        </button>
                    </div>
                </div>
            </div>

            {/* Products List */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0 bg-gray-50">
                {loading && products.length === 0 ? (
                    <div className="text-center text-gray-400 mt-8">
                        <p className="text-sm">로딩 중...</p>
                    </div>
                ) : error ? (
                    <div className="text-center text-red-500 mt-8">
                        <p className="text-sm">{error}</p>
                    </div>
                ) : products.length === 0 ? (
                    <div className="text-center text-gray-400 mt-8">
                        <svg className="w-16 h-16 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                        </svg>
                        <p className="text-sm">저장된 상품이 없습니다</p>
                        <p className="text-xs mt-1">제목과 URL을 추가해보세요</p>
                        {!isAuthenticated && (
                            <p className="text-xs mt-2 text-yellow-600">게스트 모드: 브라우저에 임시 저장됩니다</p>
                        )}
                    </div>
                ) : (
                    products.map((product) => (
                        <div
                            key={product.id}
                            className="bg-white p-3 rounded-lg border border-gray-200 hover:border-purple-300 transition group shadow-sm"
                        >
                            {editingId === product.id ? (
                                <div className="space-y-2">
                                    <input
                                        type="text"
                                        value={editTitle}
                                        onChange={(e) => setEditTitle(e.target.value)}
                                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-purple-500 outline-none"
                                        placeholder="제목"
                                        disabled={loading}
                                    />
                                    <input
                                        type="url"
                                        value={editUrl}
                                        onChange={(e) => setEditUrl(e.target.value)}
                                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-purple-500 outline-none"
                                        placeholder="URL"
                                        disabled={loading}
                                    />
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => handleSaveEdit(product.id)}
                                            className="flex-1 bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600 disabled:opacity-50"
                                            disabled={loading}
                                        >
                                            저장
                                        </button>
                                        <button
                                            onClick={cancelEdit}
                                            className="flex-1 bg-gray-300 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-400 disabled:opacity-50"
                                            disabled={loading}
                                        >
                                            취소
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                <div className="flex items-start justify-between gap-2">
                                    <div className="flex-1 min-w-0">
                                        <h4 className="font-medium text-gray-800 text-sm mb-1 truncate">
                                            {product.title}
                                        </h4>
                                        <a
                                            href={product.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-xs text-purple-600 hover:text-purple-700 break-all line-clamp-2"
                                        >
                                            {product.url}
                                        </a>
                                        <p className="text-xs text-gray-400 mt-1">
                                            {new Date(product.created_at).toLocaleString()}
                                        </p>
                                    </div>
                                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition">
                                        <button
                                            onClick={() => startEdit(product)}
                                            className="p-1 hover:bg-blue-50 rounded transition"
                                            title="수정"
                                            disabled={loading}
                                        >
                                            <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                            </svg>
                                        </button>
                                        <button
                                            onClick={() => handleRemoveProduct(product.id)}
                                            className="p-1 hover:bg-red-50 rounded transition"
                                            title="삭제"
                                            disabled={loading}
                                        >
                                            <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-gray-200 bg-gray-50 flex-shrink-0">
                <p className="text-xs text-gray-500 text-center">
                    총 {products.length}개의 상품
                    {!isAuthenticated && products.length > 0 && (
                        <span className="block mt-1 text-yellow-600">
                            (게스트 모드 - 브라우저에 저장됨)
                        </span>
                    )}
                </p>
            </div>
        </div>
    );
}
