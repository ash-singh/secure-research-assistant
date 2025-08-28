import React, { useState } from "react";

function QueryBox({ onSubmit, loading }) {
  const [question, setQuestion] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (question.trim() === "") return;
      onSubmit(question);
      //setLastQuestion(question);  // store it for display
      //setQuestion("");            // clear input
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: "1rem" }}>
      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        rows={3}
        cols={60}
        placeholder="Type your question here..."
        style={{ padding: "0.5rem" }}
      />
      <br />
      <button type="submit" disabled={loading} style={{ marginTop: "0.5rem" }}>
        {loading ? "Loading..." : "Ask"}
      </button>
    </form>
  );
}

export default QueryBox;
