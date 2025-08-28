function AnswerBox({ answer, sources }) {
  return (
    <div
      style={{
        border: "1px solid #ccc",
        padding: "1rem",
        borderRadius: "8px",
        minHeight: "100px",
        whiteSpace: "pre-wrap",
      }}
    >
      {answer || "Your answer will appear here."}
      {sources && sources.length > 0 && (
        <div style={{ marginTop: "1rem", fontStyle: "italic" }}>
          Sources: {sources.join(", ")}
        </div>
      )}
    </div>
  );
}

export default AnswerBox;
