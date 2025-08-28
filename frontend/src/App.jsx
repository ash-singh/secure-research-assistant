import React, { useState } from "react";
import QueryBox from "./components/QueryBox";
import AnswerBox from "./components/AnswerBox";
import Upload from "./components/Upload";
import './App.css'

function App() {
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [sources, setSources] = useState([]);
  const [history, setHistory] = useState([]);
  const apiUrl = import.meta.env.VITE_API_URL;

  const askQuestion = async (question) => {
    setLoading(true);
    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await response.json();
      setAnswer(data.answer);
      setSources(data.sources || []);
      setHistory([...history, { question, answer: data.answer }]);
    } catch (err) {
      console.error(err);
      setAnswer("Error querying the backend.");
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial, sans-serif" }}>
      <h1>Offline Research Assistant</h1>
      <Upload />
      <QueryBox onSubmit={askQuestion} loading={loading} />
      <AnswerBox answer={answer} />
    </div>
  );
}

export default App



