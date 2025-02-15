from fastapi import FastAPI, HTTPException
import uvicorn
import google.generativeai as genai
import requests
import logging
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import re
import difflib
from transformers import pipeline

# ✅ Load Environment Variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

# ✅ Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# ✅ Initialize FastAPI App
app = FastAPI()

# ✅ Enable CORS for Frontend Access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ✅ Logging Configuration
logging.basicConfig(level=logging.INFO)


@app.get("/")
def home():
    return {"message": "AI Response Aggregator Backend Running!"}


# ✅ Fetch AI Responses
async def fetch_gemini_response(text):
    try:
        gemini_model = genai.GenerativeModel("gemini-pro")
        response = gemini_model.generate_content(text)
        if response and response.candidates:
            return response.candidates[0].content.parts[0].text
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
    return "⚠️ Gemini API failed."


async def fetch_openai_response(text):
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        data = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": text}]}
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
    return "⚠️ OpenAI API failed."


async def fetch_perplexity_response(text):
    try:
        url = "https://api.perplexity.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {PERPLEXITY_API_KEY}", "Content-Type": "application/json"}
        data = {"model": "perplexity-pro", "messages": [{"role": "user", "content": text}]}
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"Perplexity API error: {e}")
    return "⚠️ Perplexity API failed."


@app.post("/get-ai-responses")
async def get_ai_responses(data: dict):
    user_text = data.get("text", "").strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Text input is required.")

    responses = await asyncio.gather(
        fetch_gemini_response(user_text),
        fetch_openai_response(user_text),
        fetch_perplexity_response(user_text),
    )

    model_responses = {
        "Gemini": responses[0],
        "ChatGPT": responses[1],
        "Perplexity": responses[2],
    }

    return {"model_responses": model_responses}


# ✅ AI Plagiarism Detection
@app.post("/check-plagiarism")
async def check_plagiarism(data: dict):
    """Compares text with stored academic sources"""
    text = data.get("text", "").strip()
    sources = ["Sample academic source 1", "Example reference document"]

    similarity_scores = [difflib.SequenceMatcher(None, text, source).ratio() for source in sources]
    plagiarism_score = max(similarity_scores) * 100  # Convert to percentage

    return {"plagiarism_score": round(plagiarism_score, 2)}


# ✅ AI Detection
@app.post("/check-ai")
async def check_ai(data: dict):
    text = data.get("text", "").strip()
    ai_patterns = ["GPT", "AI-generated", "machine-generated", "automated"]
    detected = any(re.search(pattern, text, re.IGNORECASE) for pattern in ai_patterns)
    result_text = "AI-generated" if detected else "Human-written"
    return {"ai_check_result": result_text}


# ✅ AI Humanization
@app.post("/humanize-ai")
async def humanize_ai(data: dict):
    text = data.get("text", "").strip()
    humanizer = pipeline("text-generation", model="EleutherAI/gpt-neo-1.3B")
    humanized_text = humanizer(text, max_length=200)[0]["generated_text"]
    return {"humanized_text": humanized_text}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
