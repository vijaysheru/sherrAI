from fastapi import FastAPI, HTTPException
import uvicorn
import google.generativeai as genai
import requests
import logging
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os

# ✅ Load Environment Variables (API Keys)
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

# ✅ Configure Logging
logging.basicConfig(level=logging.INFO)


# ✅ Root Endpoint (Fixes 404 Not Found)
@app.get("/")
def home():
    return {"message": "FastAPI Backend is Running Successfully!"}


# ✅ Health Check Endpoint
@app.get("/status")
def status():
    return {"status": "Backend is up and running!"}


# ✅ Function to Fetch AI Responses with Error Handling
async def fetch_gemini_response(text):
    """Fetches response from Google's Gemini API"""
    try:
        gemini_model = genai.GenerativeModel("gemini-pro")
        response = gemini_model.generate_content(text)
        if response and response.candidates:
            return response.candidates[0].content.parts[0].text
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
    return "⚠️ Gemini API failed."


async def fetch_openai_response(text):
    """Fetches response from OpenAI's ChatGPT API"""
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
    """Fetches response from Perplexity AI"""
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


# ✅ Route to Fetch & Compare AI Responses
@app.post("/get-ai-responses")
async def get_ai_responses(data: dict):
    """Fetches AI responses from multiple models and summarizes the output"""
    user_text = data.get("text", "")
    if not user_text:
        raise HTTPException(status_code=400, detail="Text input is required.")

    # Fetch responses concurrently
    responses = await asyncio.gather(
        fetch_gemini_response(user_text),
        fetch_openai_response(user_text),
        fetch_perplexity_response(user_text),
    )

    # Store AI model responses
    model_responses = {
        "Gemini": responses[0],
        "ChatGPT": responses[1],
        "Perplexity": responses[2],
    }

    # Generate Summary
    summary = summarize_responses(model_responses)

    return {"model_responses": model_responses, "summary": summary}


# ✅ AI-Based Response Summarization Using LangChain
def summarize_responses(responses):
    """Summarizes AI model responses using LangChain"""
    try:
        text = "\n".join([f"{model}: {response}" for model, response in responses.items()])
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

        prompt_template = PromptTemplate.from_template("Summarize this text: {text}")
        llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)
        chain = LLMChain(llm=llm, prompt=prompt_template)

        docs = splitter.create_documents([text])
        return chain.run(text=text)
    except Exception as e:
        logging.error(f"Summarization Error: {e}")
        return "⚠️ Failed to generate summary."


# ✅ Run API Locally (For Development)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
