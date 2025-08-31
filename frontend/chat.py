import streamlit as st
import requests
import json

# -------------------------------
# Backend configuration
# -------------------------------
API_URL = "http://localhost:8000"

# -------------------------------
# Session state initialization
# -------------------------------
if "docs" not in st.session_state:
    st.session_state.docs = []  # [{"id": ..., "filename": ...}]
if "history" not in st.session_state:
    st.session_state.history = []  # [{"question":..., "answer":..., "sources":...}]
if "notes" not in st.session_state:
    st.session_state.notes = []  # saved answers
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

# -------------------------------
# Sidebar: Document Manager
# -------------------------------
with st.sidebar:
    st.header("📑 Documents")

    # Fetch doc list from backend
    try:
        r = requests.get(f"{API_URL}/docs")
        docs_data = r.json()
        if isinstance(docs_data, list):
            st.session_state.docs = docs_data
        elif isinstance(docs_data, dict) and "docs" in docs_data:
            st.session_state.docs = docs_data["docs"]
        else:
            st.session_state.docs = []
    except Exception:
        st.warning("⚠️ Backend not running or no docs indexed")
        st.session_state.docs = []

    # Show existing docs
    for doc in st.session_state.docs:
        cols = st.columns([3, 1])
        cols[0].text(doc.get("filename", doc.get("name", "unknown")))
        if cols[1].button("❌", key=f"rm_{doc.get('id', doc.get('filename'))}"):
            try:
                resp = requests.delete(f"{API_URL}/docs/{doc.get('filename')}")
                resp.raise_for_status()
                st.success(f"Removed {doc.get('filename')}")
                # Refresh doc list
                r = requests.get(f"{API_URL}/docs")
                st.session_state.docs = r.json() if isinstance(r.json(), list) else r.json().get("docs", [])
            except Exception as e:
                st.error(f"Failed to remove {doc.get('filename')}: {e}")

    # Upload new document
    uploaded = st.file_uploader("➕ Add document", type=["pdf", "docx", "txt"])
    if uploaded and st.session_state.uploaded_file != uploaded.name:
        with st.spinner(f"Uploading {uploaded.name}..."):
            files = {"file": (uploaded.name, uploaded.getvalue())}
            try:
                resp = requests.post(f"{API_URL}/docs", files=files)
                resp.raise_for_status()
                st.success(f"Uploaded {uploaded.name}")
                st.session_state.uploaded_file = uploaded.name
                # Refresh doc list
                r = requests.get(f"{API_URL}/docs")
                st.session_state.docs = r.json() if isinstance(r.json(), list) else r.json().get("docs", [])
            except Exception as e:
                st.error(f"Upload failed: {e}")

# -------------------------------
# Main Tabs
# -------------------------------
tab1, tab2 = st.tabs(["🔍 Research", "📝 Notebook"])

# -------------------------------
# Tab 1: Research
# -------------------------------
with tab1:
    st.subheader("Ask a Research Question")
    query = st.text_input("Enter your question:", placeholder="e.g. What are the main findings in doc X?")

    if query:
        with st.spinner("Thinking..."):
            try:
                r = requests.get(f"{API_URL}/ask", params={"q": query})
                r.raise_for_status()
                result = r.json()
            except Exception as e:
                st.error(f"Query failed: {e}")
                result = None

        if result:
            # Save to history
            st.session_state.history.append(result)

            # Display answer
            st.markdown("### 🧠 Answer")
            st.write(result.get("answer", ""))

            # Sources expandable
            sources = result.get("sources", [])
            if sources:
                with st.expander("📂 Sources"):
                    for src in sources:
                        st.markdown(
                            f"- **{src.get('doc','')}** (conf: {src.get('confidence', 0) * 100:.1f}%)\n\n"
                            f"  {src.get('snippet','')}"
                        )

            # Save to notebook
            if st.button("💾 Save to Notebook"):
                st.session_state.notes.append(result)
                st.success("Saved!")

    # History section
    if st.session_state.history:
        st.markdown("### Recent Questions")
        for h in reversed(st.session_state.history[-5:]):
            st.markdown(f"**Q:** {h.get('question','')}\n**A:** {h.get('answer','')[:200]}...")

# -------------------------------
# Tab 2: Notebook
# -------------------------------
with tab2:
    st.subheader("Your Notes")
    if st.session_state.notes:
        for i, note in enumerate(st.session_state.notes):
            st.markdown(f"**Q:** {note.get('question','')}")
            st.write(note.get("answer",""))
            st.markdown("---")

        # Export as JSON
        if st.button("📤 Export Notebook"):
            with open("notebook.json", "w") as f:
                json.dump(st.session_state.notes, f, indent=2)
            st.success("Exported to notebook.json")
    else:
        st.info("No notes saved yet")
