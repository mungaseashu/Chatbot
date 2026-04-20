# 🎥 YouTube AI Chatbot

An AI-powered full-stack application that allows users to ask questions about any YouTube video using its transcript.

---

## 🚀 Features

- 🔗 Accepts full YouTube video URL
- 📄 Automatically fetches video transcript
- 🧠 Uses embeddings + vector search (FAISS)
- 🤖 Answers questions using LLM (Qwen2.5)
- 💬 Chat-style UI (like ChatGPT)
- ⚡ Fast responses with caching per video
---

## 🛠️ Tech Stack

### Backend
- FastAPI
- LangChain
- HuggingFace (Embeddings + LLM)
- FAISS (Vector Store)
- YouTube Transcript API

### Frontend
- React (Vite)
- Tailwind CSS


---

## 📂 Project Structure
Chatbot/
├── backend/
│ ├── main.py
│ ├── requirements.txt
│
├── frontend/
│ ├── src/
│ ├── components/
│ ├── App.jsx


---

## ⚙️ How It Works

1. User enters YouTube URL  
2. Backend extracts video ID  
3. Transcript is fetched  
4. Text is split into chunks  
5. Embeddings are created  
6. Stored in FAISS vector DB  
7. Relevant context retrieved  
8. LLM generates answer  

---

## 🔧 Local Setup

### Backend

bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

### Frontend

cd frontend
npm install
npm run dev

Environment Variables:
Backend (.env)

HUGGINGFACEHUB_API_TOKEN=your_token
OR Other models API Key

Frontend (.env)
VITE_API_URL=your_backend_url

Demo:
<img width="1895" height="896" alt="image" src="https://github.com/user-attachments/assets/03d40a63-f8a9-4b81-afd3-b9a7ab46790e" />
<img width="1905" height="897" alt="image" src="https://github.com/user-attachments/assets/8a72e4b7-5471-4ee9-aac0-1b42e74c1e8d" />


