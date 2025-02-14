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
        else:
            return "⚠️ Gemini API returned an empty response."
    except Exception as e:
        logging.error(f"❌ Gemini API Error: {str(e)}")
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
        logging.error(f"❌ OpenAI API Error: {str(e)}")
        return "⚠️ OpenAI API failed."

async def fetch_perplexity_response(text):
    try:
        url = "https://api.perplexity.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {PERPLEXITY_API_KEY}", "Content-Type": "application/json"}
        data = {"model": "perplexity-pro", "messages": [{"role": "user", "content": text}]}
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            json_response = response.json()
            if "choices" in json_response:
                return json_response["choices"][0]["message"]["content"]
            else:
                return "⚠️ Perplexity API returned an empty response."
        else:
            return f"⚠️ Perplexity API Error: {response.status_code} {response.text}"
    except Exception as e:
        logging.error(f"❌ Perplexity API Error: {str(e)}")
        return "⚠️ Perplexity API failed."

@app.post("/get-ai-responses")
async def get_ai_responses(data: dict):
    user_text = data.get("text", "")
    if not user_text:
        raise HTTPException(status_code=400, detail="Text input is required.")

    logging.info(f"🔹 Received text: {user_text}")

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

    logging.info(f"✅ Model Responses: {model_responses}")

    return {"model_responses": model_responses}
