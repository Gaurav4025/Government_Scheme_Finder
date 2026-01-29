import { Card } from "@/components/ui/card";
import { FileText, Link, Calendar, Sparkles } from "lucide-react";
import { useSourceStore } from "../stores/sourceStore";
import { useState } from "react";
import axios from "@/lib/axios";

export default function ContentPanel() {
  const { selectedSource } = useSourceStore();
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
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

    try {
      setAsking(true);
      setAnswer("");

      const res = await axios.post("/api/ask", {
        question,
        source_id: selectedSource._id,
      });

      setAnswer(res.data.response || "No response received");
    } catch (err) {
      console.error(err);
      setAnswer("Failed to get response");
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
    <div className="flex-1 bg-background p-6 overflow-y-auto">
      <div className="max-w-4xl mx-auto">
        {/* Source Header */}
        <Card className="p-6 mb-6">
          <div className="flex items-start space-x-4">
            <div className="p-3 bg-accent rounded-lg">
              {getSourceIcon(selectedSource.type)}
            </div>
            <div className="flex-1">
              <h1 className="text-2xl font-bold mb-2">
                {selectedSource.title}
              </h1>
              <div className="text-sm text-muted-foreground flex gap-4">
                <span>{formatDate(selectedSource.createdAt)}</span>
                <span className="capitalize">{selectedSource.type}</span>
              </div>
            </div>
          </div>
        </Card>

        {/* Processing */}
        {!selectedSource.summary && (
          <Card className="p-6 mb-6 text-center text-muted-foreground">
            <div className="flex items-center justify-center gap-2">
              <div className="w-4 h-4 border-2 border-t-transparent rounded-full animate-spin" />
              Processing source...
            </div>
          </Card>
        )}

        {/* Ask Section */}
        <Card className="p-6 mb-6">
          <h2 className="text-lg font-semibold mb-3">
            Ask about this document
          </h2>

          <textarea
            className="w-full border rounded p-3 mb-3"
            rows={3}
            placeholder="Ask a question about this document..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />

          <button
            onClick={handleAsk}
            disabled={asking}
            className="px-6 py-2 bg-black text-white rounded"
          >
            {asking ? "Asking..." : "Ask"}
          </button>
        </Card>

        {/* Answer */}
        <Card className="p-6">
          <h3 className="font-semibold mb-2">Response</h3>
          <p className="text-muted-foreground whitespace-pre-wrap">
            {answer || "No response received"}
          </p>
        </Card>
      </div>
    </div>
  );
}
