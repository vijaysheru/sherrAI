import { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { FaSpinner, FaRobot, FaUser } from "react-icons/fa"; // ✅ Removed unused imports

// ✅ Ensure the rest of the component code remains unchanged

export default function Home() {
  const [text, setText] = useState("");
  const [aiResponses, setAiResponses] = useState({});
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [aiScore, setAiScore] = useState(null);
  const [humanizedText, setHumanizedText] = useState("");
  const [tab, setTab] = useState("Gemini");

  const API_URL = "https://sherrai-production.up.railway.app"; // ✅ Update with your backend URL

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

  const checkAiGenerated = async () => {
    try {
      const res = await axios.post(`${API_URL}/check-ai-text`, { text });
      setAiScore(res.data.ai_score);
    } catch (error) {
      console.error("AI Detection Error:", error);
      setAiScore(null);
    }
  };

  const humanizeText = async () => {
    try {
      const res = await axios.post(`${API_URL}/humanize-text`, { text });
      setHumanizedText(res.data.humanized_text);
    } catch (error) {
      console.error("Humanization Error:", error);
      setHumanizedText("⚠️ Failed to humanize text.");
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-gray-100 dark:bg-gray-900">
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
          className="px-6 py-3 bg-purple-600 text-white font-bold rounded-lg shadow-md hover:bg-purple-700 transition"
          onClick={checkAiGenerated}
        >
          Check AI Origin
        </button>

        <button
          className="px-6 py-3 bg-green-600 text-white font-bold rounded-lg shadow-md hover:bg-green-700 transition"
          onClick={humanizeText}
        >
          Humanize Text
        </button>
      </div>

      {/* Tabs */}
      <div className="mt-6 flex space-x-4">
        {["Gemini", "ChatGPT", "Perplexity", "Mistral", "Claude", "Summary"].map((model) => (
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

      {/* AI Model Response Display */}
      <div className="mt-4 p-5 w-full md:w-2/3 lg:w-1/2 bg-white dark:bg-gray-800 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-blue-600 dark:text-blue-400">{tab} Response</h2>
        <p className="mt-2 text-gray-800 dark:text-gray-300">
          {tab === "Summary" ? summary : aiResponses[tab] || "No response yet."}
        </p>
      </div>

      {/* AI Origin Detection Result */}
      {aiScore !== null && (
        <div className="mt-6 w-full md:w-2/3 lg:w-1/2 p-5 bg-white dark:bg-gray-800 rounded-lg shadow-md">
          <h2 className="text-2xl font-bold text-purple-600 dark:text-purple-400">AI Detection Score</h2>
          <div className="flex items-center space-x-2 mt-2">
            {aiScore > 0.5 ? (
              <FaRobot className="text-red-500 text-xl" />
            ) : (
              <FaUser className="text-green-500 text-xl" />
            )}
            <p className="text-lg">
              {aiScore > 0.5 ? "Likely AI-generated" : "Likely Human-written"} (Score: {aiScore.toFixed(2)})
            </p>
          </div>
        </div>
      )}

      {/* Humanized Text */}
      {humanizedText && (
        <div className="mt-6 w-full md:w-2/3 lg:w-1/2 p-5 bg-white dark:bg-gray-800 rounded-lg shadow-md">
          <h2 className="text-2xl font-bold text-green-600 dark:text-green-400">Humanized Text</h2>
          <p className="mt-2 text-gray-800 dark:text-gray-300">{humanizedText}</p>
        </div>
      )}
    </div>
  );
}
