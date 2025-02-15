import { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { FaSpinner } from "react-icons/fa";
import { CircularProgressbar } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";
import { CircularProgress } from "@mui/material";

export default function Home() {
  const [text, setText] = useState("");
  const [aiResponses, setAiResponses] = useState({});
  const [summary, setSummary] = useState("");
  const [aiCheckResult, setAiCheckResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [tab, setTab] = useState("Gemini");
  const [progress, setProgress] = useState(0);

  const API_URL = "http://127.0.0.1:8000"; // Local backend URL

  // Fetch AI Responses
  const fetchResponses = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/get-ai-responses`, { text });
      setAiResponses(res.data.model_responses);
      setSummary(res.data.summary);
    } catch (error) {
      console.error("API Error:", error);
      setAiResponses({
        Gemini: "⚠️ Error fetching from Gemini",
        ChatGPT: "⚠️ Error fetching from OpenAI",
        Perplexity: "⚠️ Error fetching from Perplexity",
      });
      setSummary("⚠️ Failed to generate summary.");
    }
    setLoading(false);
  };

  // AI Checker Function
  const checkAIContent = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/check-ai`, { text });
      setAiCheckResult(res.data);
      setProgress(res.data.ai_score);
    } catch (error) {
      console.error("AI Check Error:", error);
      setAiCheckResult({ message: "⚠️ AI detection failed." });
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-gray-100">
      <motion.h1
        className="text-4xl font-bold text-blue-600 dark:text-blue-400 mb-6"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        AI Response Aggregator
      </motion.h1>

      <textarea
        className="border border-gray-400 dark:border-gray-700 p-3 w-full md:w-2/3 lg:w-1/2 h-32 rounded-lg text-lg bg-white dark:bg-gray-800"
        placeholder="Enter your text here..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <div className="flex space-x-4 mt-4">
        <button
          className="px-6 py-3 bg-blue-600 text-white font-bold rounded-lg shadow-md hover:bg-blue-700 transition"
          onClick={fetchResponses}
          disabled={loading}
        >
          {loading ? <FaSpinner className="animate-spin mx-auto" /> : "Get AI Responses"}
        </button>

        <button
          className="px-6 py-3 bg-red-500 text-white font-bold rounded-lg shadow-md hover:bg-red-600 transition"
          onClick={checkAIContent}
          disabled={loading}
        >
          {loading ? <FaSpinner className="animate-spin mx-auto" /> : "Check AI"}
        </button>
      </div>

      {/* Tabs */}
      <div className="mt-6 flex space-x-4">
        {["Gemini", "ChatGPT", "Perplexity", "Summary", "AI Check"].map((model) => (
          <button
            key={model}
            className={`px-4 py-2 text-sm font-semibold rounded-md transition ${
              tab === model ? "bg-blue-600 text-white" : "bg-gray-300 dark:bg-gray-700 text-gray-800 dark:text-gray-300"
            }`}
            onClick={() => setTab(model)}
          >
            {model}
          </button>
        ))}
      </div>

      {/* Response Display */}
      <div className="mt-4 p-5 w-full md:w-2/3 lg:w-1/2 bg-white dark:bg-gray-800 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-blue-600 dark:text-blue-400">{tab} Response</h2>
        <p className="mt-2 text-gray-800 dark:text-gray-300">
          {tab === "Summary"
            ? summary
            : tab === "AI Check"
            ? aiCheckResult?.message || "No AI check result yet."
            : aiResponses[tab] || "No response yet."}
        </p>
      </div>

      {/* AI Score Meter */}
      {tab === "AI Check" && (
        <div className="mt-6 w-1/3">
          <h3 className="text-lg font-bold text-gray-700 mb-2">AI Score</h3>
          <CircularProgressbar value={progress} text={`${progress}%`} />
        </div>
      )}
    </div>
  );
}
