import { useState, useRef, useEffect } from "react";

export default function ChatBox({ messages, onSend }) {
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);

  // Auto scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="h-screen bg-[#343541] flex flex-col text-white">

      {/* Header */}
      <div className="p-4 border-b border-gray-700 text-center text-lg font-semibold">
        YouTube Chatbot
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[70%] px-4 py-3 rounded-lg text-sm ${
                msg.role === "user"
                  ? "bg-[#19c37d] text-black"
                  : "bg-[#444654]"
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-700 bg-[#343541]">

        <div className="flex items-center bg-[#40414f] rounded-lg px-3 py-2">

          <input
            className="flex-1 bg-transparent outline-none text-sm"
            placeholder="Send a message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />

          <button
            onClick={() => {
              if (!input.trim()) return;
              onSend(input);
              setInput("");
            }}
            className="ml-2 bg-[#19c37d] text-black px-3 py-1 rounded-md"
          >
            Send
          </button>

        </div>

      </div>
    </div>
  );
}