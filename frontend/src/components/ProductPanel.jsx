// File: frontend/src/components/ProductPanel.jsx
import { useState } from 'react';

export default function ProductPanel() {
    const [products, setProducts] = useState([]);
    const [url, setUrl] = useState('');
    const [title, setTitle] = useState('');
    const [isOpen, setIsOpen] = useState(true);
    const [editingId, setEditingId] = useState(null);
    const [editTitle, setEditTitle] = useState('');
    const [editUrl, setEditUrl] = useState('');

    const addProduct = () => {
        if (!url.trim()) return;

        const newProduct = {
            id: Date.now(),
            title: title.trim() || '제목 없음',
            url: url.trim(),
            addedAt: new Date().toLocaleString(),
        };

        setProducts([newProduct, ...products]);
        setUrl('');
        setTitle('');
    };

    const removeProduct = (id) => {
        setProducts(products.filter(p => p.id !== id));
    };

    const startEdit = (product) => {
        setEditingId(product.id);
        setEditTitle(product.title);
        setEditUrl(product.url);
    };

    const saveEdit = (id) => {
        setProducts(products.map(p =>
            p.id === id
                ? { ...p, title: editTitle.trim() || '제목 없음', url: editUrl.trim() }
                : p
        ));
        setEditingId(null);
    };

    const cancelEdit = () => {
        setEditingId(null);
        setEditTitle('');
        setEditUrl('');
    };

    if (!isOpen) {
        return (
            <button
                onClick={() => setIsOpen(true)}
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
                        onClick={() => setIsOpen(false)}
                        className="p-2 hover:bg-white/50 rounded-lg transition"
                        title="닫기"
                    >
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <div className="space-y-2">
                    <input
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && addProduct()}
                        placeholder="상품 제목"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                    />
                    <div className="flex gap-2">
                        <input
                            type="url"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && addProduct()}
                            placeholder="상품 URL"
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                        />
                        <button
                            onClick={addProduct}
                            className="bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600 transition text-sm font-medium shadow-sm"
                        >
                            추가
                        </button>
                    </div>
                </div>
            </div>

            {/* Products List */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0 bg-gray-50">
                {products.length === 0 ? (
                    <div className="text-center text-gray-400 mt-8">
                        <svg className="w-16 h-16 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                        </svg>
                        <p className="text-sm">저장된 상품이 없습니다</p>
                        <p className="text-xs mt-1">제목과 URL을 추가해보세요</p>
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
                                    />
                                    <input
                                        type="url"
                                        value={editUrl}
                                        onChange={(e) => setEditUrl(e.target.value)}
                                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-purple-500 outline-none"
                                        placeholder="URL"
                                    />
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => saveEdit(product.id)}
                                            className="flex-1 bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
                                        >
                                            저장
                                        </button>
                                        <button
                                            onClick={cancelEdit}
                                            className="flex-1 bg-gray-300 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-400"
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
                                            {product.addedAt}
                                        </p>
                                    </div>
                                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition">
                                        <button
                                            onClick={() => startEdit(product)}
                                            className="p-1 hover:bg-blue-50 rounded transition"
                                            title="수정"
                                        >
                                            <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                            </svg>
                                        </button>
                                        <button
                                            onClick={() => removeProduct(product.id)}
                                            className="p-1 hover:bg-red-50 rounded transition"
                                            title="삭제"
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
                </p>
            </div>
        </div>
    );
}
