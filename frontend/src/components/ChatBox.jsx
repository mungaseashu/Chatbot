import { useState, useEffect, useRef } from "react";

export default function ChatBox({ messages, onSend }) {
  const [input, setInput] = useState("");
  const [displayedMessages, setDisplayedMessages] = useState([]);
  const bottomRef = useRef(null);

  useEffect(() => {
    setDisplayedMessages(messages);
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="h-screen bg-[#343541] flex flex-col text-white">

      <div className="p-4 border-b border-gray-700 text-center text-lg font-semibold">
        YouTube Chatbot
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">

        {displayedMessages.map((msg, i) => (
          <div key={i}>
            <div className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[70%] px-4 py-3 rounded-lg text-sm ${
                msg.role === "user"
                  ? "bg-[#19c37d] text-black"
                  : "bg-[#444654]"
              }`}>
                {msg.text}
              </div>
            </div>

            {/* 🔥 SOURCES */}
            {/* {msg.sources && (
              <div className="text-xs text-gray-400 mt-2 ml-2">
                Sources:
                {msg.sources.map((s, idx) => (
                  <div key={idx}>• {s}</div>
                ))}
              </div>
            )} */}
          </div>
        ))}

        <div ref={bottomRef} />
      </div>

      <div className="p-4 border-t border-gray-700 bg-[#343541]">
        <div className="flex items-center bg-[#40414f] rounded-lg px-3 py-2">

          <input
            className="flex-1 bg-transparent outline-none text-sm"
            placeholder="Ask about the video..."
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