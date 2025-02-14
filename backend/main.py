from fastapi import FastAPI, HTTPException
import uvicorn
import google.generativeai as genai
import openai
import requests
import logging
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from dotenv import load_dotenv
import os

# ✅ Load Environment Variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

# ✅ Validate API Keys
if not GEMINI_API_KEY or not OPENAI_API_KEY or not PERPLEXITY_API_KEY:
    raise ValueError("🚨 API Keys are missing! Ensure they are set in your .env file.")

# ✅ Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# ✅ Initialize FastAPI
app = FastAPI()

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)

# ✅ AI Model API Fetch Functions
async def fetch_gemini_response(text):
    try:
        gemini_model = genai.GenerativeModel("gemini-pro")
        response = gemini_model.generate_content(text)
        if response and response.candidates:
            return response.candidates[0].content.parts[0].text
    except Exception as e:
        return f"⚠️ Gemini API error: {e}"
    return "⚠️ Gemini API failed."

async def fetch_openai_response(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": text}],
            api_key=OPENAI_API_KEY,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ OpenAI API error: {e}"

async def fetch_perplexity_response(text):
    try:
        url = "https://api.perplexity.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {PERPLEXITY_API_KEY}", "Content-Type": "application/json"}
        data = {"model": "perplexity-pro", "messages": [{"role": "user", "content": text}]}
        response = requests.post(url, json=data, headers=headers)
        return response.json()["choices"][0]["message"]["content"] if response.status_code == 200 else "⚠️ Perplexity API failed."
    except Exception as e:
        return f"⚠️ Perplexity API error: {e}"

@app.post("/get-ai-responses")
async def get_ai_responses(data: dict):
    user_text = data.get("text", "")
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

    summary = summarize_responses(model_responses)
    return {"model_responses": model_responses, "summary": summary}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
