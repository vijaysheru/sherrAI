from fastapi import FastAPI, HTTPException
import uvicorn
import google.generativeai as genai
import openai
import requests
import logging
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
import os

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


# ✅ Function to Fetch AI Responses
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
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # ✅ Fallback to GPT-3.5
            messages=[{"role": "user", "content": text}]
        )
        return response.choices[0].message.content
    except openai.OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
        return "⚠️ OpenAI API failed."


async def fetch_perplexity_response(text):
    try:
        url = "https://api.perplexity.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "mistral-7b-instruct",
            "messages": [{"role": "user", "content": text}]
        }
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
    )

    model_responses = {
        "Gemini": responses[0],
        "ChatGPT": responses[1],
        "Perplexity": responses[2],
    }

    summary = await summarize_responses(model_responses)
    return {"model_responses": model_responses, "summary": summary}


# ✅ AI-Based Response Summarization
async def summarize_responses(responses):
    try:
        text = "\n".join([f"{model}: {response}" for model, response in responses.items()])
        llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)
        chain = RunnablePassthrough() | llm
        return chain.invoke(text)  # ✅ `.invoke()` replaces `.run()`
    except Exception as e:
        logging.error(f"Summarization Error: {e}")
        return "⚠️ Failed to generate summary."


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
