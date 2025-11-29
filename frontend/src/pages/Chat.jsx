// File: frontend/src/pages/Chat.jsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import useChatStore from '../store/chatStore';
import Sidebar from '../components/Sidebar';
import ChatArea from '../components/ChatArea';
import ProductPanel from '../components/ProductPanel';

export default function Chat() {
    const { isAuthenticated, logout } = useAuthStore();
    const { fetchConversations, createConversation } = useChatStore();
    const navigate = useNavigate();
    const [sidebarOpen, setSidebarOpen] = useState(true);

    useEffect(() => {
        // 로그인한 사용자만 대화 목록 불러오기
        if (isAuthenticated) {
            fetchConversations();
        }
    }, [isAuthenticated, fetchConversations]);

    const handleNewChat = async () => {
        if (isAuthenticated) {
            await createConversation();
        } else {
            // 게스트는 임시 대화만 가능
            alert('로그인하지 않은 사용자는 대화가 저장되지 않습니다.');
        }
    };

    const handleLogin = () => {
        navigate('/login');
    };

    const handleLogout = () => {
        logout();
        window.location.reload(); // 페이지 새로고침
    };

    return (
        <div className="flex h-screen overflow-hidden bg-gray-50">
            {/* Sidebar */}
            <Sidebar
                isOpen={sidebarOpen}
                onToggle={() => setSidebarOpen(!sidebarOpen)}
                onNewChat={handleNewChat}
                onLogin={handleLogin}
                onLogout={handleLogout}
                isAuthenticated={isAuthenticated}
            />

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col min-w-0">
                <ChatArea />
            </div>

            {/* Product Panel */}
            <ProductPanel />
        </div>
    );
}
