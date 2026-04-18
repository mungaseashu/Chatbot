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

# -------------------- LOAD ENV --------------------
load_dotenv()

# -------------------- INIT APP --------------------
app = FastAPI()

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- HEALTH CHECK --------------------
@app.get("/")
def root():
    return {"message": "API running 🚀"}

# -------------------- REQUEST MODEL --------------------
class ChatRequest(BaseModel):
    video_url: str
    question: str

# -------------------- CACHE --------------------
vector_store_cache = {}

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
        return " ".join([item.text for item in transcript_list])
    except TranscriptsDisabled:
        raise HTTPException(status_code=400, detail="Transcript disabled")
    except Exception:
        raise HTTPException(status_code=404, detail="Transcript not available")


def create_vector_store(transcript: str):
    # ✅ LIGHTWEIGHT EMBEDDING (CRITICAL)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    docs = splitter.create_documents([transcript])

    return FAISS.from_documents(docs, embeddings)


def get_vector_store(video_id: str):
    if video_id in vector_store_cache:
        return vector_store_cache[video_id]

    transcript = get_transcript(video_id)
    vs = create_vector_store(transcript)

    vector_store_cache[video_id] = vs
    return vs


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# -------------------- PROMPT --------------------
prompt = PromptTemplate(
    template="""
You are a helpful assistant.
Answer ONLY from the transcript.
If not found, say "I don't know".

Context:
{context}

Question:
{question}
""",
    input_variables=["context", "question"]
)

# -------------------- MAIN API --------------------
@app.post("/chat")
def chat(request: ChatRequest):
    try:
        video_id = extract_video_id(request.video_url)

        vector_store = get_vector_store(video_id)
        retriever = vector_store.as_retriever(search_kwargs={"k": 2})

        # ✅ LOAD LLM INSIDE API (CRITICAL FIX)
        llm = HuggingFaceEndpoint(
            repo_id="Qwen/Qwen2.5-7B-Instruct",
            task="conversational",
            temperature=0.2
        )

        chat_model = ChatHuggingFace(llm=llm)

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

        return {"answer": answer}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))