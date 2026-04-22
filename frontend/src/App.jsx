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

  // ---------------- EXTRACT VIDEO ID ----------------
  const getVideoId = (url) => {
    const match = url.match(/v=([^&]+)/);
    return match ? match[1] : "";
  };

  // ---------------- LOAD VIDEO ----------------
  const loadVideo = async () => {
    if (!videoUrl.trim()) return;

    setLoading(true);

    try {
      await fetch(import.meta.env.VITE_API_URL + "/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          video_url: videoUrl,
          question: "hello",
        }),
      });

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
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          video_url: videoUrl,
          question,
        }),
      });

      const data = await res.json();

      // 🔥 Typing animation
      let text = "";
      for (let char of data.answer) {
        text += char;

        setMessages([
          ...newMessages,
          { role: "bot", text }
        ]);

        await new Promise((r) => setTimeout(r, 10));
      }

      // Final message with sources
      setMessages([
        ...newMessages,
        {
          role: "bot",
          text: data.answer,
          sources: data.sources
        }
      ]);

    } catch (err) {
      console.error(err);
    }
  };

  // ---------------- UI ----------------

  // 🔹 Input Screen
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

        {/* Overlay */}
        <div className="absolute inset-0 bg-black/75 backdrop-blur-sm"></div>

        {/* Content */}
        <div className="relative z-10 flex flex-col items-center gap-10 text-center">

          {/* Title */}
          <h1 className="text-5xl md:text-6xl font-extrabold text-white tracking-wide drop-shadow-lg">
            <span className="bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
              YouTube Chatbot
            </span>
          </h1>

          {/* Card */}
          <div className="bg-white/10 backdrop-blur-2xl border border-white/20 p-8 rounded-3xl shadow-2xl flex flex-col gap-5 w-[420px]">

            {/* Input */}
            <input
              className="p-4 rounded-xl bg-white/90 text-black outline-none text-base placeholder-gray-500"
              placeholder="Paste YouTube URL..."
              value={videoUrl}
              onChange={(e) => setVideoUrl(e.target.value)}
            />

            {/* 🔥 YouTube Preview */}
            {videoUrl && (
              <img
                src={`https://img.youtube.com/vi/${getVideoId(videoUrl)}/0.jpg`}
                className="rounded-xl"
              />
            )}

            {/* Button */}
            <button
              onClick={loadVideo}
              className="bg-gradient-to-r from-purple-500 to-blue-500 py-3 rounded-xl text-white font-semibold text-lg hover:scale-[1.02] transition"
            >
              Load Video
            </button>

            {/* Loading */}
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