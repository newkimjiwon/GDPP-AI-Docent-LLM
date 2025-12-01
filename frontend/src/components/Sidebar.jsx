// File: frontend/src/components/Sidebar.jsx
import { useState } from 'react';
import useChatStore from '../store/chatStore';

export default function Sidebar({ isOpen, onToggle, onNewChat, onLogin, onLogout, isAuthenticated }) {
    const { conversations, currentConversation, selectConversation, deleteConversation, updateConversation } =
        useChatStore();
    const [editingId, setEditingId] = useState(null);
    const [editingTitle, setEditingTitle] = useState('');

    if (!isOpen) {
        return (
            <button
                onClick={onToggle}
                className="fixed top-4 left-4 z-50 p-3 bg-white rounded-lg shadow-lg hover:bg-gray-50 border border-gray-200"
                title="메뉴 열기"
            >
                <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
            </button>
        );
    }

    return (
        <div className="w-80 bg-white text-gray-800 flex flex-col border-r border-gray-200 shadow-lg flex-shrink-0">
            {/* Header */}
            <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-purple-50">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-bold text-gray-800">🐱 궁디팡팡 AI</h2>
                    <button
                        onClick={onToggle}
                        className="p-2 hover:bg-white/50 rounded-lg transition"
                    >
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <button
                    onClick={onNewChat}
                    className="w-full bg-indigo-500 hover:bg-indigo-600 text-white py-2 px-4 rounded-lg transition flex items-center justify-center gap-2 shadow-sm"
                >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    새 대화
                </button>

                {!isAuthenticated && (
                    <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm">
                        <p className="text-yellow-800 mb-2 font-medium">게스트 모드</p>
                        <p className="text-yellow-700 text-xs mb-2">대화가 저장되지 않습니다</p>
                        <button
                            onClick={onLogin}
                            className="w-full bg-yellow-500 hover:bg-yellow-600 text-white py-1.5 px-3 rounded text-sm transition shadow-sm"
                        >
                            로그인하여 저장
                        </button>
                    </div>
                )}
            </div>

            {/* Conversations List */}
            <div className="flex-1 overflow-y-auto p-2 min-h-0 bg-gray-50">
                {isAuthenticated ? (
                    conversations.length > 0 ? (
                        conversations.map((conv) => (
                            <div
                                key={conv.id}
                                className={`p-3 rounded-lg mb-2 cursor-pointer transition group ${currentConversation?.id === conv.id
                                    ? 'bg-indigo-50 border border-indigo-200'
                                    : 'bg-white hover:bg-gray-100 border border-gray-200'
                                    }`}
                                onClick={() => selectConversation(conv.id)}
                            >
                                <div className="flex items-center justify-between">
                                    {editingId === conv.id ? (
                                        <input
                                            type="text"
                                            value={editingTitle}
                                            onChange={(e) => setEditingTitle(e.target.value)}
                                            onKeyDown={(e) => {
                                                if (e.key === 'Enter') {
                                                    updateConversation(conv.id, editingTitle);
                                                    setEditingId(null);
                                                } else if (e.key === 'Escape') {
                                                    setEditingId(null);
                                                }
                                            }}
                                            onBlur={() => setEditingId(null)}
                                            onClick={(e) => e.stopPropagation()}
                                            className="flex-1 px-2 py-1 border border-indigo-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                            autoFocus
                                        />
                                    ) : (
                                        <span
                                            className="truncate flex-1 text-gray-700"
                                            onDoubleClick={(e) => {
                                                e.stopPropagation();
                                                setEditingId(conv.id);
                                                setEditingTitle(conv.title);
                                            }}
                                        >
                                            {conv.title}
                                        </span>
                                    )}
                                    <div className="flex gap-1">
                                        {editingId !== conv.id && (
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    setEditingId(conv.id);
                                                    setEditingTitle(conv.title);
                                                }}
                                                className="opacity-0 group-hover:opacity-100 p-1 hover:bg-indigo-50 rounded transition"
                                                title="제목 수정"
                                            >
                                                <svg className="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                                                </svg>
                                            </button>
                                        )}
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                if (confirm('이 대화를 삭제하시겠습니까?')) {
                                                    deleteConversation(conv.id);
                                                }
                                            }}
                                            className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-50 rounded transition"
                                            title="대화 삭제"
                                        >
                                            <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                                <div className="text-xs text-gray-400 mt-1">
                                    {new Date(conv.updated_at).toLocaleDateString()}
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="text-center text-gray-400 mt-8 px-4">
                            <p className="text-sm">저장된 대화가 없습니다</p>
                            <p className="text-xs mt-2">새 대화를 시작하세요</p>
                        </div>
                    )
                ) : (
                    <div className="text-center text-gray-400 mt-8 px-4">
                        <p className="text-sm">로그인하면</p>
                        <p className="text-sm">대화 기록을 저장할 수 있습니다</p>
                    </div>
                )}
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-gray-200 bg-gray-50">
                {isAuthenticated ? (
                    <button
                        onClick={onLogout}
                        className="w-full text-left p-2 hover:bg-gray-100 rounded-lg transition flex items-center gap-2 text-gray-700"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                        </svg>
                        로그아웃
                    </button>
                ) : (
                    <button
                        onClick={onLogin}
                        className="w-full text-left p-2 hover:bg-gray-100 rounded-lg transition flex items-center gap-2 text-gray-700"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                        </svg>
                        로그인
                    </button>
                )}
            </div>
        </div>
    );
}
