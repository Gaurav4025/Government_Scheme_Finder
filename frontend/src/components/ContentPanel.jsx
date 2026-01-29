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

  // Minimal Markdown -> HTML converter for basic MD/MDX-like content
  // Supports headings, bold, italics, inline code, fenced code blocks, and unordered lists.
  const mdToHtml = (markdown) => {
    if (!markdown) return "";

    let md = String(markdown);

    // Escape HTML special chars to avoid injection, then we'll re-insert allowed tags
    const escapeHtml = (str) =>
      str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

    md = escapeHtml(md);

    // Fenced code blocks ```lang\ncode\n```
    md = md.replace(/```([\s\S]*?)```/g, (m, code) => {
      return `<pre><code>${code.replace(/</g, "&lt;")}</code></pre>`;
    });

    // Inline code `code`
    md = md.replace(/`([^`]+)`/g, "<code>$1</code>");

    // Headings
    md = md.replace(/^###### (.*$)/gim, "<h6>$1</h6>");
    md = md.replace(/^##### (.*$)/gim, "<h5>$1</h5>");
    md = md.replace(/^#### (.*$)/gim, "<h4>$1</h4>");
    md = md.replace(/^### (.*$)/gim, "<h3>$1</h3>");
    md = md.replace(/^## (.*$)/gim, "<h2>$1</h2>");
    md = md.replace(/^# (.*$)/gim, "<h1>$1</h1>");

    // Bold **text** or __text__
    md = md.replace(/\*\*(.*?)\*\*/gim, "<strong>$1</strong>");
    md = md.replace(/__(.*?)__/gim, "<strong>$1</strong>");

    // Italic *text* or _text_
    md = md.replace(/\*(.*?)\*/gim, "<em>$1</em>");
    md = md.replace(/_(.*?)_/gim, "<em>$1</em>");

    // Unordered lists: lines starting with - or *
    // Convert consecutive list lines into a single <ul>
    md = md.replace(/(^|\n)([ \t]*[-*] .+(?:\n[ \t]*[-*] .+)*)/gim, (m, pre, listBlock) => {
      const items = listBlock
        .split(/\n/)
        .map((l) => l.replace(/^[ \t]*[-*] /, ""))
        .map((it) => `<li>${it}</li>`) 
        .join("");
      return `${pre}<ul>${items}</ul>`;
    });

    // Convert double newlines to paragraph breaks
    md = md.split(/\n\s*\n/).map((para) => {
      // If para already starts with a block tag, keep as-is
      if (/^<(h[1-6]|ul|pre|blockquote)/i.test(para.trim())) return para;
      return `<p>${para.replace(/\n/g, "<br />")}</p>`;
    }).join("");

    return md;
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
                    {/* Render assistant content as HTML when it contains markdown/MDX-like markup */}
                    <div
                      className="whitespace-pre-wrap text-sm"
                      dangerouslySetInnerHTML={{ __html: mdToHtml(msg.content) }}
                    />
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