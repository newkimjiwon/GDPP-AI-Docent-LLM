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
        } catch (error) {
            set({ error: error.message });
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
