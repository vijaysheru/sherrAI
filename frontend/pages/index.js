import { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { FaSpinner, FaSun, FaMoon } from "react-icons/fa";

export default function Home() {
  const [text, setText] = useState("");
  const [aiResponses, setAiResponses] = useState({});
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [tab, setTab] = useState("Gemini");
  const [darkMode, setDarkMode] = useState(false);

  const API_URL = "https://sherrai-production.up.railway.app"; // Update with your backend URL

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

  return (
    <div className={`${darkMode ? "dark bg-gray-900 text-white" : "bg-gray-100 text-black"} min-h-screen flex flex-col items-center justify-center p-6 transition-all`}>

      {/* Dark Mode Toggle */}
      <button
        className="absolute top-5 right-5 p-3 bg-gray-200 dark:bg-gray-700 rounded-full shadow-md transition-all"
        onClick={() => setDarkMode(!darkMode)}
      >
        {darkMode ? <FaSun className="text-yellow-400" /> : <FaMoon className="text-gray-900" />}
      </button>

      <motion.h1
        className="text-4xl font-bold text-blue-600 dark:text-blue-400 mb-6"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        AI Response Aggregator
      </motion.h1>

      <textarea
        className="border border-gray-400 dark:border-gray-700 p-3 w-full md:w-2/3 lg:w-1/2 h-32 rounded-lg text-lg bg-white dark:bg-gray-800 transition-all"
        placeholder="Enter your text here..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <button
        className="mt-4 px-6 py-3 bg-blue-600 text-white font-bold rounded-lg shadow-md hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
        onClick={fetchResponses}
        disabled={loading}
      >
        {loading ? <FaSpinner className="animate-spin mx-auto" /> : "Get AI Responses"}
      </button>

      {/* Tabs */}
      <div className="mt-6 flex space-x-4">
        {["Gemini", "ChatGPT", "Perplexity", "Summary"].map((model) => (
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
      <div className="mt-4 p-5 w-full md:w-2/3 lg:w-1/2 bg-white dark:bg-gray-800 rounded-lg shadow-md transition-all">
        <h2 className="text-2xl font-bold text-blue-600 dark:text-blue-400">{tab} Response</h2>
        <p className="mt-2 text-gray-800 dark:text-gray-300">
          {tab === "Summary" ? summary : aiResponses[tab] || "No response yet."}
        </p>
      </div>
    </div>
  );
}
