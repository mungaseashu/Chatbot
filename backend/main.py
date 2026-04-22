import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint, ChatHuggingFace
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API running 🚀"}

class ChatRequest(BaseModel):
    video_url: str
    question: str

# ---------------- CACHE ----------------
vector_store_cache = {}

# ---------------- HELPERS ----------------

def extract_video_id(url: str) -> str:
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    raise HTTPException(status_code=400, detail="Invalid YouTube URL")


def get_transcript(video_id: str) -> str:
    try:
        transcript_list = YouTubeTranscriptApi().fetch(video_id, languages=["en"])
        return " ".join([item.text for item in transcript_list])
    except TranscriptsDisabled:
        raise HTTPException(status_code=400, detail="Transcript disabled")
    except Exception:
        raise HTTPException(status_code=404, detail="Transcript not available")


def create_vector_store(video_id, transcript):
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5"
    )

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.create_documents([transcript])

    db_path = f"db/{video_id}"

    if os.path.exists(db_path):
        return FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)

    vector_store = FAISS.from_documents(docs, embeddings)
    vector_store.save_local(db_path)

    return vector_store


def get_vector_store(video_id: str):
    if video_id in vector_store_cache:
        return vector_store_cache[video_id]

    transcript = get_transcript(video_id)
    vs = create_vector_store(video_id, transcript)

    vector_store_cache[video_id] = vs
    return vs


def format_docs(docs):
    return docs


prompt = PromptTemplate(
    template="""
You are a helpful AI assistant.

Answer the question using ONLY the provided transcript context.

If the exact answer is not directly stated, you may:
- infer logically from the context
- summarize relevant parts

But DO NOT use outside knowledge.

If the context is completely unrelated, say:
"I don't know based on the transcript."

If user asks for summary → summarize the context.
Context:
{context}

Question:
{question}
""",
    input_variables=["context", "question"]
)

@app.post("/chat")
def chat(request: ChatRequest):
    video_id = extract_video_id(request.video_url)

    vector_store = get_vector_store(video_id)
    retriever = vector_store.as_retriever(search_kwargs={"k": 6})

    docs = retriever.invoke(request.question)

    context = "\n\n".join([d.page_content for d in docs])

    llm = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen2.5-7B-Instruct",
        task="conversational",
        temperature=0.2
    )

    chat_model = ChatHuggingFace(llm=llm)

    final_prompt = prompt.format(
    context=context,
    question=request.question
)

    answer = chat_model.invoke(final_prompt)

    # 🔥 SOURCES
    sources = [doc.page_content[:120] for doc in docs]

    return {
        "answer": answer.content,
        "sources": sources
    }