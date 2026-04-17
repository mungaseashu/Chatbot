import { useState } from "react";

export default function InputBar({ onSend }) {
  const [videoId, setVideoId] = useState("");
  const [question, setQuestion] = useState("");

  return (
    <div className="p-4 flex gap-2 bg-gray-800">
      <input
        className="p-2 rounded bg-gray-700 w-1/4"
        placeholder="Video ID"
        value={videoId}
        onChange={(e) => setVideoId(e.target.value)}
      />
      <input
        className="p-2 rounded bg-gray-700 flex-1"
        placeholder="Ask a question..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />
      <button
        onClick={() => onSend(videoId, question)}
        className="bg-blue-600 px-4 rounded"
      >
        Send
      </button>
    </div>
  );
}