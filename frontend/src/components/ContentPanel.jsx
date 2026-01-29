import { Card } from "@/components/ui/card";
import { FileText, Link, Bot, Sparkles } from "lucide-react";
import { useSourceStore } from "../stores/sourceStore";
import { useState } from "react";
import axios from "@/lib/axios";

export default function ContentPanel() {
  const { selectedSource } = useSourceStore();
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [asking, setAsking] = useState(false);

  if (!selectedSource) {
    return (
      <div className="flex-1 max-w-2xl bg-background flex items-center justify-center">
        <div className="text-center">
          <Sparkles className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
          <h2 className="text-2xl font-semibold text-foreground mb-2">
            Add a source to get started
          </h2>
          <p className="text-muted-foreground max-w-md">
            Upload documents to begin analyzing and chatting with your content.
          </p>
        </div>
      </div>
    );
  }

  const handleAsk = async () => {
    if (!question.trim()) return;

    const userQuestion = question;
    setQuestion(""); // Clear input immediately

    // Add user message to chat
    setMessages((prev) => [...prev, { type: "user", content: userQuestion }]);

    try {
      setAsking(true);

      const res = await axios.post("/api/ask", {
        question: userQuestion,
        source_id: selectedSource._id,
      });

      const response = res.data.response || "No response received";
      
      // Add assistant message to chat
      setMessages((prev) => [...prev, { type: "assistant", content: response }]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [...prev, { type: "assistant", content: "Failed to get response" }]);
    } finally {
      setAsking(false);
    }
  };

  const getSourceIcon = (type) => {
    switch (type) {
      case "link":
        return <Link className="w-5 h-5" />;
      default:
        return <FileText className="w-5 h-5" />;
    }
  };

  const formatDate = (dateString) =>
    new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });

  return (
    <div className="flex-1 bg-background h-full flex flex-col m-4 pb-4">
      <div className="max-w-4xl mx-auto w-full flex flex-col h-full">

        {/* Source Header */}
        <Card className="p-6 mb-4">
          <div className="flex items-start space-x-4">
            <div className="p-3 bg-accent rounded-lg">
              {getSourceIcon(selectedSource.type)}
            </div>
            <div className="flex-1">
              <h1 className="text-2xl font-bold mb-1">
                {selectedSource.title}
              </h1>
              <div className="text-sm text-muted-foreground flex gap-4">
                <span>{formatDate(selectedSource.createdAt)}</span>
                <span className="capitalize">{selectedSource.type}</span>
              </div>
            </div>
          </div>
        </Card>

        {/* Chat Messages */}
        <Card className="flex-1 p-4 overflow-y-auto space-y-4">
          
          {/* Initial Message */}
          {messages.length === 0 && !asking && (
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center">
                <Bot className="w-6 h-6 text-primary" />
              </div>
              <div className="bg-muted p-3 rounded-lg max-w-[80%]">
                <p className="text-sm">
                  Hi! I'm ready to answer questions about this document. What would you like to know?
                </p>
              </div>
            </div>
          )}

          {/* Message History */}
          {messages.map((msg, index) => (
            <div key={index}>
              {msg.type === "user" ? (
                <div className="flex justify-end">
                  <div className="bg-black text-white p-3 rounded-lg max-w-[80%]">
                    <p className="text-sm">{msg.content}</p>
                  </div>
                </div>
              ) : (
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center">
                    <Bot className="w-6 h-6 text-primary" />
                  </div>
                  <div className="bg-muted p-3 rounded-lg max-w-[80%]">
                    <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
                  </div>
                </div>
              )}
            </div>
          ))}

          {/* Loading State */}
          {asking && (
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center">
                <Bot className="w-6 h-6 text-primary" />
              </div>
              <div className="bg-muted p-3 rounded-lg">
                <p className="text-sm text-muted-foreground">Thinking...</p>
              </div>
            </div>
          )}
        </Card>

        {/* Input Box */}
        <div className=" p-3 bg-background">
          <div className="flex gap-3">
            <textarea
              className="flex-1 align-center border rounded-lg p-2 w-full h-15 resize-none"
              rows={2}
              placeholder="Ask a question about this document..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleAsk();
                }
              }}
            />

            <button
              onClick={handleAsk}
              disabled={asking || !question.trim()}
              className="px-6 py-2 bg-black text-white rounded-lg disabled:opacity-50"
            >
              {asking ? "Asking..." : "Send"}
            
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}