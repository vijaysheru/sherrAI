from fastapi import FastAPI, HTTPException
import uvicorn
import google.generativeai as genai
import openai
import requests
import logging
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
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


# ✅ Function to Fetch AI Responses (Handles API Failures)
async def fetch_gemini_response(text):
    try:
        gemini_model = genai.GenerativeModel("gemini-pro")
        response = gemini_model.generate_content(text)
        if response and response.candidates:
            return response.candidates[0].content.parts[0].text
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
    return None


async def fetch_openai_response(text):
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": text}]
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
    return None


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
            return response.json()["choices"][0]["message"]["content"]
        else:
            logging.error(f"Perplexity API error: {response.text}")
    except Exception as e:
        logging.error(f"Perplexity API error: {e}")
    return None


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
        "Gemini": responses[0] if responses[0] else "⚠️ Gemini API failed.",
        "ChatGPT": responses[1] if responses[1] else "⚠️ OpenAI API failed.",
        "Perplexity": responses[2] if responses[2] else "⚠️ Perplexity API failed.",
    }

    # ✅ Summarize and Compare Responses
    summary = await summarize_responses(model_responses)
    return {"model_responses": model_responses, "summary": summary}


# ✅ AI-Based Response Summarization
async def summarize_responses(responses):
    try:
        text = "\n".join([f"{model}: {response}" for model, response in responses.items()])

        llm = ChatOpenAI(model_name="gpt-4-turbo", openai_api_key=OPENAI_API_KEY)

        prompt_template = PromptTemplate.from_template(
            "Summarize the following AI-generated responses in a concise and clear way:\n{text}"
        )
        chain = LLMChain(llm=llm, prompt=prompt_template)

        return chain.run(text=text)
    except Exception as e:
        logging.error(f"Summarization Error: {e}")
        return "⚠️ Failed to generate summary."


# ✅ Deploy API on Railway
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
