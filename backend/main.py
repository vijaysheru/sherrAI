from fastapi import FastAPI, HTTPException
import uvicorn
import google.generativeai as genai
import openai
import requests
import logging
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from transformers import pipeline
from dotenv import load_dotenv
import os
import time

# ✅ Load Environment Variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
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

# ✅ Load Free Hugging Face Model (Mistral-7B) as Backup
mistral_model = pipeline("text-generation", model="mistralai/Mistral-7B-Instruct-v0.1")

# ✅ Function to Fetch AI Responses (Handles API Failures)
async def fetch_gemini_response(text):
    """Fetch response from Google Gemini API"""
    try:
        gemini_model = genai.GenerativeModel("gemini-pro")
        response = gemini_model.generate_content(text)
        if response and response.candidates:
            return response.candidates[0].content.parts[0].text
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
    return "⚠️ Gemini API failed."

async def fetch_openai_response(text):
    """Fetch response from OpenAI API with auto-retry"""
    for attempt in range(3):  # Retry up to 3 times
        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": text}]
            )
            return response.choices[0].message.content
        except openai.OpenAIError as e:
            logging.error(f"OpenAI API error: {e}")
            if "insufficient_quota" in str(e):
                return "⚠️ OpenAI API quota exceeded. Switching to Mistral."
            time.sleep(2)  # Wait before retrying

    return "⚠️ OpenAI API failed."

async def fetch_perplexity_response(text):
    """Fetch response from Perplexity AI API"""
    try:
        url = "https://api.perplexity.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {PERPLEXITY_API_KEY}", "Content-Type": "application/json"}
        data = {"model": "mistral-7b-instruct", "messages": [{"role": "user", "content": text}]}
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            response_json = response.json()
            return response_json.get("choices", [{}])[0].get("message", {}).get("content", "⚠️ No response from Perplexity.")
        else:
            logging.error(f"Perplexity API error: {response.text}")
            return "⚠️ Perplexity API request failed."
    except Exception as e:
        logging.error(f"Perplexity API error: {e}")
        return "⚠️ Perplexity API failed."

async def fetch_mistral_response(text):
    """Fetch response from free Hugging Face Mistral-7B model"""
    try:
        response = mistral_model(text, max_length=300)
        return response[0]["generated_text"]
    except Exception as e:
        logging.error(f"Mistral API error: {e}")
        return "⚠️ Mistral AI failed."

# ✅ Route to Fetch & Compare AI Responses
@app.post("/get-ai-responses")
async def get_ai_responses(data: dict):
    user_text = data.get("text", "")
    if not user_text:
        raise HTTPException(status_code=400, detail="Text input is required.")

    responses = await asyncio.gather(
        fetch_gemini_response(user_text),
        fetch_openai_response(user_text),
        fetch_perplexity_response(user_text),
        fetch_mistral_response(user_text)
    )

    model_responses = {
        "Gemini": responses[0],
        "ChatGPT": responses[1] if responses[1] != "⚠️ OpenAI API quota exceeded. Switching to Mistral." else responses[3],
        "Perplexity": responses[2]
    }

    summary = await summarize_responses(model_responses)
    return {"model_responses": model_responses, "summary": summary}

# ✅ AI-Based Response Summarization Using LangChain
async def summarize_responses(responses):
    """Summarize AI responses using LangChain"""
    try:
        text = "\n".join([f"{model}: {response}" for model, response in responses.items()])
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        prompt_template = PromptTemplate.from_template("Summarize this content: {text}")
        parser = StrOutputParser()

        # Use OpenAI for summarization if available
        llm = openai.OpenAI(model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)
        chain = load_summarize_chain(llm, chain_type="map_reduce")

        docs = splitter.create_documents([text])
        return chain.run(docs)

    except Exception as e:
        logging.error(f"Summarization Error: {e}")
        return "⚠️ Failed to generate summary."

# ✅ Deploy API on Railway
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
