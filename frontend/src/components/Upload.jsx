import React, { useState } from "react";

function Upload() {
  const [status, setStatus] = useState("");

  const handleDrop = async (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setStatus("Uploading...");
    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      setStatus(data.message || "Upload complete.");
    } catch (err) {
      console.error(err);
      setStatus("Upload failed.");
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      style={{
        border: "2px dashed #888",
        borderRadius: "8px",
        padding: "1rem",
        textAlign: "center",
        marginBottom: "1rem",
      }}
    >
      <p>Drag & drop a PDF or DOCX file here to upload and process</p>
      <p>{status}</p>
    </div>
  );
}

export default Upload;
