# **AI-Powered Plagiarism and AI Text Detection System**

## **Project Overview**
AI-Powered Plagiarism and AI Text Detection System is an advanced tool designed to analyze text, detect AI-generated content, check plagiarism, and provide humanized text suggestions. This system is built using **Next.js** for the frontend and **Flask** for the backend, incorporating **NLP models** and **LLMs** for intelligent analysis.

### **Features**
- ✅ **AI Response Aggregator**: Collects responses from various AI models.
- ✅ **AI Plagiarism Detection**: Checks if the text is AI-generated using **ZeroGPT API**.
- ✅ **Humanization Feature**: Rewrites AI-generated text in a more human-like style.
- ✅ **Customizable AI Detection**: Allows users to fine-tune AI-generated content recognition.
- ✅ **Interactive UI**: A sleek, professional design using **Next.js, TailwindCSS, and Framer Motion**.
- ✅ **Cloud Deployment**: Easily deployable on **Vercel (Frontend) and AWS (Backend)**.

---

## **Technologies Used**
### **Frontend:**
- **Next.js 15.1.7** - Framework for React applications
- **TailwindCSS** - Styling for UI
- **Framer Motion** - Smooth animations
- **React Circular Progress Bar** - Visual progress indicators
- **React Icons** - UI icons

### **Backend:**
- **Flask** - Lightweight web framework for API
- **Flask-CORS** - Handles cross-origin requests
- **TensorFlow** - Potential use for AI-powered humanization
- **ZeroGPT API** - Detects AI-generated content
- **Gunicorn** - For production-level WSGI server

### **Deployment:**
- **Frontend**: Hosted on **Vercel**
- **Backend**: Hosted on **AWS EC2 / Railway (When Available)**
- **Database**: Can be extended with **PostgreSQL / Firebase** for user data storage

---

## **Installation & Setup**
### **Prerequisites**
Ensure you have the following installed:
- **Python 3.9+** for backend
- **Node.js 18+** for frontend
- **Virtual Environment** (venv) for Python dependencies
- **NPM / Yarn** for JavaScript dependencies

### **Step 1: Clone the Repository**
```bash
git clone https://github.com/vijaysheru/sherrAI.git
cd sherrAI
```
### **Step 2: Backend Setup**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
pip install -r requirements.txt
python app.py
```
✅ The backend will run at http://127.0.0.1:5000/.
### **Step 3: Frontend Setup**
```bash
cd ../frontend
npm install
npm run dev
```
✅ The frontend will run at http://localhost:3000/.

### **Usage**
---
-1️⃣ Checking for AI-Generated Content
Paste text into the input field.
Click "Check AI".
The system will analyze and return a probability score.

-2️⃣ Humanizing AI-Generated Text
Enter AI-generated content.
Click "Humanize AI".
The text will be rewritten in a more human-like style.

-3️⃣ AI Response Aggregation
The tool will collect and compare AI-generated responses from various models.

