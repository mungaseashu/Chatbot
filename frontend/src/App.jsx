import { useState } from "react";
import ChatBox from "./components/ChatBox";

export default function App() {
  const [videoUrl, setVideoUrl] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "bot",
      text: "👋 Paste a YouTube link to get started."
    }
  ]);

  const [loaded, setLoaded] = useState(false);
  const [loading, setLoading] = useState(false);

  // ---------------- LOAD VIDEO ----------------
  const loadVideo = async () => {
    if (!videoUrl.trim()) return;

    setLoading(true);

    try {
      // 🔥 Just preload backend (no summary shown)
      await fetch(import.meta.env.VITE_API_URL + "/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          video_url: videoUrl,
          question: "hello", // dummy (not shown)
        }),
      });

      // ✅ Only show ready message
      setMessages([
        {
          role: "bot",
          text: "🎉 Video loaded! Ask me anything about it."
        }
      ]);

      setLoaded(true);
    } catch (err) {
      console.error(err);
      alert("Failed to load video");
    }

    setLoading(false);
  };

  // ---------------- SEND MESSAGE ----------------
  const sendMessage = async (question) => {
    if (!question.trim()) return;

    const newMessages = [...messages, { role: "user", text: question }];
    setMessages(newMessages);

    try {
      const res = await fetch(import.meta.env.VITE_API_URL + "/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          video_url: videoUrl,
          question,
        }),
      });

      const data = await res.json();

      setMessages([
        ...newMessages,
        { role: "bot", text: data.answer }
      ]);
    } catch (err) {
      console.error(err);
    }
  };

  // ---------------- UI ----------------

  // 🔹 Input + Loading Screen
  if (!loaded) {
  return (
    <div className="h-screen flex items-center justify-center relative overflow-hidden">

      {/* Background */}
      <div className="absolute inset-0">
        <img
          src="advanced_AI_system_202604180019.png"   
          alt="bg"
          className="w-full h-full object-cover"
        />
      </div>

      {/* Overlay (improves readability) */}
      <div className="absolute inset-0 bg-black/75 backdrop-blur-sm"></div>

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center gap-10 text-center">

        {/* 🔥 TITLE */}
        <h1 className="text-5xl md:text-6xl font-extrabold text-white tracking-wide drop-shadow-lg">
          <span className="bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
            YouTube Chatbot
          </span>
        </h1>

        {/* 💎 CARD */}
        <div className="bg-white/10 backdrop-blur-2xl border border-white/20 p-8 rounded-3xl shadow-2xl flex flex-col gap-5 w-[420px]">

          {/* INPUT */}
          <input
            className="p-4 rounded-xl bg-white/90 text-black outline-none text-base placeholder-gray-500"
            placeholder="Paste YouTube URL..."
            value={videoUrl}
            onChange={(e) => setVideoUrl(e.target.value)}
          />

          {/* BUTTON */}
          <button
            onClick={loadVideo}
            className="bg-gradient-to-r from-purple-500 to-blue-500 py-3 rounded-xl text-white font-semibold text-lg hover:scale-[1.02] transition"
          >
            Load Video
          </button>

          {/* LOADING */}
          {loading && (
            <div className="text-sm text-gray-200 animate-pulse">
              ⏳ Preparing video...
            </div>
          )}

        </div>

      </div>
    </div>
  );
}

  // 🔹 Chat Screen
  return <ChatBox messages={messages} onSend={sendMessage} />;
}