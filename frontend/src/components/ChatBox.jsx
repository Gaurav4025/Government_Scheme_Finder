import { useState } from "react";
import axios from "../lib/axios";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

export default function ChatBox({ sourceId }) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    if (!question.trim()) return;

    try {
      setLoading(true);
      setAnswer("");

      const res = await axios.post("/api/ask", {
        question,
        source_id: sourceId
      });

      setAnswer(res.data.answer || "No response received");
    } catch (err) {
      console.error(err);
      setAnswer("Error fetching response");
    } finally {
      setLoading(false);
    }
  };
  POST /api/ask
{
  question: userPrompt
}


  return (
    <div className="mt-6 space-y-4">
      <h2 className="text-lg font-semibold">Ask about this document</h2>

      <Textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask your question..."
      />

      <Button onClick={handleAsk} disabled={loading}>
        {loading ? "Thinking..." : "Ask"}
      </Button>

      {answer && (
        <div className="p-4 bg-muted rounded">
          {answer}
        </div>
      )}
    </div>
  );
}
