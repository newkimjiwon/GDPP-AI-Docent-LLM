// File: frontend/src/store/chatStore.js
import { create } from 'zustand';
import api from '../services/api';

const useChatStore = create((set, get) => ({
    conversations: [],
    currentConversation: null,
    messages: [],
    isLoading: false,
    error: null,

    fetchConversations: async () => {
        set({ isLoading: true });
        try {
            const response = await api.get('/conversations/');
            set({ conversations: response.data, isLoading: false });
        } catch (error) {
            set({ error: error.message, isLoading: false });
        }
    },

    createConversation: async (title = 'New Chat', folderId = null) => {
        try {
            const response = await api.post('/conversations/', {
                title,
                folder_id: folderId,
            });
            set((state) => ({
                conversations: [response.data, ...state.conversations],
                currentConversation: response.data,
                messages: [],
            }));
            return response.data;
        } catch (error) {
            set({ error: error.message });
            return null;
        }
    },

    selectConversation: async (conversationId) => {
        set({ isLoading: true });
        try {
            const response = await api.get(`/conversations/${conversationId}`);
            set({
                currentConversation: response.data,
                messages: response.data.messages || [],
                isLoading: false,
            });
        } catch (error) {
            set({ error: error.message, isLoading: false });
        }
    },

    sendMessage: async (content) => {
        const { currentConversation } = get();

        // Add user message optimistically
        const userMessage = {
            role: 'user',
            content,
            created_at: new Date().toISOString(),
        };

        set((state) => ({
            messages: [...state.messages, userMessage],
        }));

        try {
            // Send to chat API
            const chatPayload = currentConversation
                ? { message: content, conversation_id: currentConversation.id }
                : { message: content }; // 게스트는 conversation_id 없이 전송

            const response = await api.post('/chat', chatPayload);

            // Add assistant message
            const assistantMessage = {
                role: 'assistant',
                content: response.data.response,
                sources: response.data.sources,
                created_at: new Date().toISOString(),
            };

            set((state) => ({
                messages: [...state.messages, assistantMessage],
            }));

            // 로그인 사용자의 경우 메시지가 백엔드에서 자동 저장됨
            // (chat.py에서 conversation_id가 있으면 자동으로 DB에 저장)
        } catch (error) {
            set({ error: error.message });
        }
    },

    updateConversation: async (conversationId, title) => {
        try {
            const response = await api.put(`/conversations/${conversationId}`, { title });
            
            set((state) => ({
                conversations: state.conversations.map((conv) =>
                    conv.id === conversationId ? { ...conv, title } : conv
                ),
                currentConversation:
                    state.currentConversation?.id === conversationId
                        ? { ...state.currentConversation, title }
                        : state.currentConversation,
            }));
            
            return response.data;
        } catch (error) {
            set({ error: error.message });
            return null;
        }
    },

    deleteConversation: async (conversationId) => {
        try {
            await api.delete(`/conversations/${conversationId}`);
            set((state) => ({
                conversations: state.conversations.filter((c) => c.id !== conversationId),
                currentConversation:
                    state.currentConversation?.id === conversationId
                        ? null
                        : state.currentConversation,
                messages: state.currentConversation?.id === conversationId ? [] : state.messages,
            }));
        } catch (error) {
            set({ error: error.message });
        }
    },

    clearError: () => set({ error: null }),
}));

export default useChatStore;
