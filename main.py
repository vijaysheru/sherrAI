from fastapi import FastAPI
import uvicorn
import torch
from transformers import pipeline, GPT2LMHeadModel, GPT2Tokenizer
from googlesearch import search
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ✅ Load AI Detection Model
ai_detector = pipeline("text-classification", model="roberta-base-openai-detector")

# ✅ Load GPT-2 Model for Humanization
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")


@app.get("/")
def home():
    """Check if FastAPI is running."""
    return {"message": "FastAPI is running successfully!"}


# ✅ AI Content Detection Route
@app.post("/ai-detection")
async def detect_ai_content(data: dict):
    text = data.get("text", "")
    result = ai_detector(text)
    ai_score = result[0]["score"] * 100
    return {"ai_score": round(ai_score, 2)}


# ✅ Humanization Route
@app.post("/humanize-text")
async def humanize_text(data: dict):
    text = data.get("text", "")
    style = data.get("style", "formal")

    temperature = 0.7 if style == "formal" else 1.0 if style == "creative" else 0.5

    input_ids = tokenizer.encode(text, return_tensors="pt")
    output = model.generate(input_ids, max_length=300, temperature=temperature)

    humanized_text = tokenizer.decode(output[0], skip_special_tokens=True)
    return {"humanized_text": humanized_text}


# ✅ Plagiarism Checking with Google Search
@app.post("/plagiarism-check")
async def check_plagiarism(data: dict):
    text = data.get("text", "")
    search_query = f'"{text[:50]}"'
    results = [url for url in search(search_query, num_results=5)]
    return {"possible_matches": results}


# ✅ Run API on Railway
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
