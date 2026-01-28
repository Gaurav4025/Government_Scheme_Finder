// src/components/ChatPanel.jsx
import { useState, useRef, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Send, Bot, User, MessageSquare, Loader2 } from "lucide-react";
import { useChatStore } from '../stores/chatStore';
import MessageContent from './MessageContent';

export default function ChatPanel() {
  const { messages, isLoading, sendMessage } = useChatStore();
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef(null);

  // 🔹 TEMPORARY USER DATA (replace later with real profile)
  const userData = {
    marks_12: 90,
    income: 250000,
    state: "Bihar",
    category: "SC"
  };

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const question = inputMessage.trim();
    setInputMessage('');

  await sendMessage(
  {
    marks_12: 90,
    income: 250000,
    state: "Bihar",
    category: "SC"
  },
  message
);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="w-[500px] bg-chat-bg border-l border-border h-full flex flex-col">
      
      {/* Header */}
      <div className="p-4 border-b border-border">
        <h2 className="text-lg font-semibold text-foreground">
          Eligibility Chat
        </h2>
        <p className="text-sm text-muted-foreground">
          Ask questions about government schemes
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <Bot className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
            <p className="text-sm text-muted-foreground mb-2">
              Start by asking about your eligibility
            </p>
            <p className="text-xs text-muted-foreground">
              Example: "Which scholarships can I apply for?"
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`flex items-start space-x-2 max-w-[85%] ${
                message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}
            >
              <div
                className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-accent text-accent-foreground'
                }`}
              >
                {message.role === 'user'
                  ? <User className="w-4 h-4" />
                  : <Bot className="w-4 h-4" />
                }
              </div>

              <Card
                className={`p-3 ${
                  message.role === 'user'
                    ? 'bg-chat-user border-border'
                    : 'bg-chat-assistant border-border'
                }`}
              >
                <MessageContent content={message.content} />
              </Card>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-start space-x-2 max-w-[85%]">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-accent text-accent-foreground flex items-center justify-center">
                <Bot className="w-4 h-4" />
              </div>
              <Card className="p-3 bg-chat-assistant border-border">
                <div className="flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-sm text-muted-foreground">
                    Thinking...
                  </span>
                </div>
              </Card>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-border">
        <div className="flex space-x-2">
          <Input
            placeholder="Ask about your eligibility..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            className="bg-input border-border"
          />
          <Button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            size="icon"
            className="bg-primary hover:bg-primary/80"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
  }
}
