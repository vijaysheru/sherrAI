import { useState } from "react";

export default function Home() {
  const [text, setText] = useState("");
  const [aiResponse, setAiResponse] = useState("");
  const [humanizedText, setHumanizedText] = useState("");
  const [aiScore, setAiScore] = useState(null);
  const [plagiarismMatches, setPlagiarismMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [tab, setTab] = useState("aiResponse");
  const [writingStyle, setWritingStyle] = useState("formal");

  const API_URL = "https://your-backend-api-url.com"; // Replace with actual backend URL

  const fetchAiResponse = async () => {
    setLoading(true);
    const res = await fetch(`${API_URL}/get-ai-responses`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await res.json();
    setAiResponse(data.gemini_response);
    setLoading(false);
    setTab("aiResponse");
  };

  const humanizeText = async () => {
    setLoading(true);
    const res = await fetch(`${API_URL}/humanize-text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: aiResponse, style: writingStyle }),
    });
    const data = await res.json();
    setHumanizedText(data.humanized_text);
    setLoading(false);
    setTab("humanizedText");
  };

  return (
    <div className="min-h-screen bg-[#FBFFE4] flex flex-col items-center py-10 px-5">
      <h1 className="text-4xl font-bold text-[#3D8D7A] mb-5">AI Response Aggregator</h1>

      <textarea
        className="border border-gray-400 p-3 w-3/4 md:w-1/2 h-32 rounded-lg text-lg"
        placeholder="Enter your text here..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <div className="mt-4 flex flex-wrap gap-3 justify-center">
        <button className={`px-5 py-2 text-white font-bold rounded-lg text-lg bg-[#3D8D7A]`} onClick={fetchAiResponse}>
          {loading ? "Fetching..." : "Get AI Response"}
        </button>
        <button className={`px-5 py-2 text-white font-bold rounded-lg text-lg bg-[#B3D8A8]`} onClick={humanizeText}>
          {loading ? "Humanizing..." : "Humanize"}
        </button>
      </div>

      <div className="mt-4 flex gap-3">
        <label className="text-lg font-semibold">Select Writing Style:</label>
        <select
          className="border border-gray-400 p-2 rounded-lg"
          value={writingStyle}
          onChange={(e) => setWritingStyle(e.target.value)}
        >
          <option value="formal">Formal</option>
          <option value="casual">Casual</option>
          <option value="creative">Creative</option>
        </select>
      </div>

      {aiResponse && (
        <div className="mt-6 w-3/4 md:w-1/2 bg-white p-5 rounded-lg shadow-md">
          <h2 className="text-2xl font-bold text-[#3D8D7A]">AI Response</h2>
          <p className="mt-2 text-gray-800">{aiResponse}</p>
        </div>
      )}

      {humanizedText && (
        <div className="mt-6 w-3/4 md:w-1/2 bg-white p-5 rounded-lg shadow-md">
          <h2 className="text-2xl font-bold text-[#B3D8A8]">Humanized Text</h2>
          <p className="mt-2 text-gray-800">{humanizedText}</p>
        </div>
      )}
    </div>
  );
}
