import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react';
import { WS_BASE_URL } from '../config';

interface WebSocketContextType {
    connected: boolean;
    lastEvent: any | null;
    sendMessage: (data: any) => void;
    queueStatus: {
        current: any | null;
        size: number;
    };
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [connected, setConnected] = useState(false);
    const [lastEvent, setLastEvent] = useState<any | null>(null);
    const [queueStatus, setQueueStatus] = useState<{ current: any | null; size: number }>({
        current: null,
        size: 0
    });

    const socketRef = useRef<WebSocket | null>(null);

    const connect = useCallback(() => {
        if (socketRef.current?.readyState === WebSocket.OPEN) return;

        console.log("🔌 Connecting to WebSocket...");
        const ws = new WebSocket(`${WS_BASE_URL}/assistant/ws`);

        ws.onopen = () => {
            console.log("✅ WebSocket Connected");
            setConnected(true);
        };

        ws.onmessage = (event) => {
            try {
                const payload = JSON.parse(event.data);
                setLastEvent(payload);

                // Handle global queue status updates
                if (payload.type === "task_queued") {
                    setQueueStatus(prev => ({ ...prev, size: payload.data.queue_size }));
                } else if (payload.type === "task_started") {
                    setQueueStatus(prev => ({ ...prev, current: payload.data.task }));
                } else if (payload.type === "task_finished") {
                    setQueueStatus(prev => ({ ...prev, current: null }));
                }
            } catch (error) {
                console.error("Failed to parse WebSocket message:", error, event.data);
            }
        };

        ws.onclose = () => {
            console.log("❌ WebSocket Disconnected. Retrying in 3s...");
            setConnected(false);
            setTimeout(connect, 3000);
        };

        ws.onerror = (error) => {
            console.error("WebSocket Error:", error);
            ws.close();
        };

        socketRef.current = ws;
    }, []);

    useEffect(() => {
        connect();
        return () => {
            socketRef.current?.close();
        };
    }, [connect]);

    const sendMessage = useCallback((data: any) => {
        if (socketRef.current?.readyState === WebSocket.OPEN) {
            socketRef.current.send(JSON.stringify(data));
        } else {
            console.warn("WebSocket not connected. Message not sent:", data);
        }
    }, []);

    return (
        <WebSocketContext.Provider value={{ connected, lastEvent, sendMessage, queueStatus }}>
            {children}
        </WebSocketContext.Provider>
    );
};

export const useWebSocket = () => {
    const context = useContext(WebSocketContext);
    if (context === undefined) {
        throw new Error('useWebSocket must be used within a WebSocketProvider');
    }
    return context;
};
