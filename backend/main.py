import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import (
    HuggingFaceEmbeddings,
    HuggingFaceEndpoint,
    ChatHuggingFace
)
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough,
    RunnableLambda
)
from langchain_core.output_parsers import StrOutputParser



# -------------------- LOAD ENV --------------------
load_dotenv()

# -------------------- INIT APP --------------------
app = FastAPI()

# -------------------- CORS FIX --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API running 🚀"}

# IMPORTANT for Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

# -------------------- GLOBAL CACHE --------------------
vector_store_cache = {}

# -------------------- GLOBAL EMBEDDINGS (LOAD ONCE) --------------------
# Using SMALL model for CPU (FAST)
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",   # 🔥 faster than base
    encode_kwargs={"normalize_embeddings": True}
)

# -------------------- LLM (LOAD ONCE) --------------------
llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    task="conversational",
    temperature=0.2
)

chat_model = ChatHuggingFace(llm=llm)

# -------------------- REQUEST MODEL --------------------
class ChatRequest(BaseModel):
    video_url: str
    question: str

# -------------------- HELPERS --------------------

def extract_video_id(url: str) -> str:
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    raise HTTPException(status_code=400, detail="Invalid YouTube URL")


def get_transcript(video_id: str) -> str:
    try:
        transcript_list = YouTubeTranscriptApi().fetch(video_id, languages=["en"])
        transcript = " ".join([item.text for item in transcript_list])

        if not transcript.strip():
            raise HTTPException(status_code=404, detail="Empty transcript")

        return transcript

    except TranscriptsDisabled:
        raise HTTPException(status_code=400, detail="Transcript is disabled for this video")

    except Exception:
        raise HTTPException(status_code=404, detail="Invalid video or transcript not available")


def create_vector_store(transcript: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,   # smaller = faster on CPU
        chunk_overlap=150
    )

    docs = splitter.create_documents([transcript])

    vector_store = FAISS.from_documents(docs, embeddings)

    return vector_store


def get_vector_store(video_id: str):
    # ✅ CACHE HIT
    if video_id in vector_store_cache:
        return vector_store_cache[video_id]

    # ❌ FIRST TIME → PROCESS
    transcript = get_transcript(video_id)
    vector_store = create_vector_store(transcript)

    vector_store_cache[video_id] = vector_store
    return vector_store


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# -------------------- PROMPT --------------------
prompt = PromptTemplate(
    template="""
You are a helpful assistant.

Answer ONLY from the transcript context.
If not found, say "I don't know".

Context:
{context}

Question:
{question}
""",
    input_variables=["context", "question"]
)

# -------------------- STARTUP WARMUP --------------------
@app.on_event("startup")
def startup_event():
    print("🚀 Backend started (models loaded once)")

# -------------------- HEALTH CHECK --------------------
@app.get("/")
def root():
    return {"message": "YouTube Chatbot API is running 🚀"}

# -------------------- MAIN API --------------------
@app.post("/chat")
def chat(request: ChatRequest):
    try:
        video_id = extract_video_id(request.video_url)

        vector_store = get_vector_store(video_id)
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})  # less docs = faster

        chain = (
            RunnableParallel({
                "context": retriever | RunnableLambda(format_docs),
                "question": RunnablePassthrough()
            })
            | prompt
            | RunnableLambda(lambda x: x.to_string())
            | chat_model
            | StrOutputParser()
        )

        answer = chain.invoke(request.question)

        return {
            "video_id": video_id,
            "answer": answer
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))