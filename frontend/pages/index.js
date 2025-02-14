"use client";
import { useState } from "react";

export default function Home() {
  const [text, setText] = useState("");
  const [aiResponses, setAiResponses] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("Gemini");

  const API_URL = "https://sherrai-production.up.railway.app";

  const fetchAiResponses = async () => {
    setLoading(true);
    setAiResponses(null);

    const response = await fetch(`${API_URL}/get-ai-responses`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    const data = await response.json();
    setAiResponses(data);
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-5">
      <h1 className="text-4xl font-bold text-[#3D8D7A] mb-5">AI Response Aggregator</h1>

      <textarea
        className="border border-gray-400 p-3 w-3/4 md:w-1/2 h-32 rounded-lg text-lg shadow-sm focus:outline-none"
        placeholder="Enter your question..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <button
        className="px-6 py-3 mt-4 text-white font-bold bg-[#3D8D7A] hover:bg-[#2F6E5A] rounded-lg text-lg transition duration-300"
        onClick={fetchAiResponses}
      >
        {loading ? "Fetching Responses..." : "Get AI Responses"}
      </button>

      {loading && <div className="mt-4 text-lg text-gray-700">⚡ Fetching AI responses, please wait...</div>}

      {aiResponses && (
        <div className="mt-6 w-3/4 md:w-1/2 bg-white p-5 rounded-lg shadow-lg">
          <h2 className="text-2xl font-bold text-[#3D8D7A] mb-4">AI Responses</h2>

          {/* Tabs for AI Models */}
          <div className="flex gap-4">
            {Object.keys(aiResponses.model_responses).map((model) => (
              <button
                key={model}
                onClick={() => setActiveTab(model)}
                className={`px-4 py-2 rounded-md font-bold ${
                  activeTab === model ? "bg-[#3D8D7A] text-white" : "bg-gray-200"
                }`}
              >
                {model}
              </button>
            ))}
          </div>

          {/* AI Model Response */}
          <div className="mt-4">
            <h3 className="text-xl font-bold text-[#3D8D7A]">{activeTab} Response:</h3>
            <p className="mt-2 text-gray-800 whitespace-pre-line">
              {aiResponses.model_responses[activeTab]}
            </p>
          </div>

          {/* Summarization Section */}
          <div className="mt-6">
            <h3 className="text-xl font-bold text-[#B3D8A8]">Summary:</h3>
            <p className="mt-2 text-gray-800">{aiResponses.summary}</p>
          </div>
        </div>
      )}
    </div>
  );
}
