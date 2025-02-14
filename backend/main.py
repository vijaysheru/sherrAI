from fastapi import FastAPI, HTTPException
import uvicorn
import google.generativeai as genai
import requests
import logging
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# ✅ Load Environment Variables (Store API Keys Securely)
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

# ✅ Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# ✅ Initialize FastAPI
app = FastAPI()

# ✅ Enable CORS for Frontend Access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ✅ Configure Logging
logging.basicConfig(level=logging.INFO)


# ✅ Function to Fetch AI Responses (Handles API Failures)
async def fetch_gemini_response(text):
    """Fetch response from Gemini AI"""
    try:
        gemini_model = genai.GenerativeModel("gemini-pro")
        response = gemini_model.generate_content(text)
        if response and response.candidates:
            return response.candidates[0].content.parts[0].text
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
    return None


async def fetch_perplexity_response(text):
    """Fetch response from Perplexity AI"""
    try:
        url = "https://api.perplexity.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {"model": "perplexity-pro", "messages": [{"role": "user", "content": text}]}
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            logging.error(f"Perplexity API error: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Perplexity API exception: {e}")
    return None


# ✅ Route to Fetch & Compare AI Responses
@app.post("/get-ai-responses")
async def get_ai_responses(data: dict):
    """Fetch responses from Gemini and Perplexity AI models"""
    user_text = data.get("text", "")
    if not user_text:
        raise HTTPException(status_code=400, detail="Text input is required.")

    responses = await asyncio.gather(
        fetch_gemini_response(user_text),
        fetch_perplexity_response(user_text),
    )

    model_responses = {
        "Gemini": responses[0] if responses[0] else "⚠️ Gemini API failed.",
        "Perplexity": responses[1] if responses[1] else "⚠️ Perplexity API failed.",
    }

    # ✅ Summarize and Compare Responses using Gemini
    summary = summarize_responses_gemini(model_responses)

    return {"model_responses": model_responses, "summary": summary}


# ✅ AI-Based Response Summarization Using Gemini
def summarize_responses_gemini(responses):
    """Summarizes responses using Gemini AI"""
    try:
        text = "\n".join([f"{model}: {response}" for model, response in responses.items()])
        gemini_model = genai.GenerativeModel("gemini-pro")
        summary_response = gemini_model.generate_content(f"Summarize this: {text}")

        if summary_response and summary_response.candidates:
            return summary_response.candidates[0].content.parts[0].text
    except Exception as e:
        logging.error(f"Summarization Error with Gemini: {e}")
    return "⚠️ Summarization is not available at the moment."


# ✅ Deploy API on Railway
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
