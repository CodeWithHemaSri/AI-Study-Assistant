import os
import streamlit as st
from google import genai
from pypdf import PdfReader

st.title("🤖 AI Document Q&A Assistant")

st.write("Upload a document and ask multiple questions about it.")

# Get Gemini API key
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key not found.")
    st.stop()

client = genai.Client(api_key=api_key)

# Upload document
uploaded_file = st.file_uploader(
    "Choose a document",
    type=["txt", "pdf"]
)

if uploaded_file is not None:

    # Read PDF
    if uploaded_file.name.endswith(".pdf"):

        pdf_reader = PdfReader(uploaded_file)

        document_text = ""

        for page in pdf_reader.pages:

            text = page.extract_text()

            if text:
                document_text += text + "\n"

    # Read TXT
    else:

        document_text = uploaded_file.read().decode("utf-8")

    # Check whether text was extracted
    if not document_text.strip():

        st.warning(
            "⚠️ No readable text was found in this document. "
            "This may be a scanned or image-based PDF."
        )

        st.stop()

    st.success("Document uploaded successfully!")

    # Document information
    st.write("📄 **File:**", uploaded_file.name)

    if uploaded_file.name.endswith(".pdf"):
        st.write("📑 **Pages:**", len(pdf_reader.pages))

    st.write("📝 **Characters extracted:**", len(document_text))

    st.divider()

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display previous questions and answers
    for chat in st.session_state.chat_history:

        st.markdown("### 👤 Question")
        st.write(chat["question"])

        st.markdown("### 🤖 Answer")
        st.write(chat["answer"])

        st.divider()

    # Create a form for the question
    with st.form("question_form", clear_on_submit=True):

        question = st.text_input(
            "Ask a question about the document:"
        )

        ask_button = st.form_submit_button("Ask Gemini")

    if ask_button:

        if not question.strip():

            st.warning("Please enter a question.")

        else:

            prompt = f"""
You are an AI document assistant.

Read and understand the uploaded document carefully.

Answer the user's question based only on the information available in the document.

You can summarize, explain, analyze, or organize information from the document when requested.

Do not invent facts that are not supported by the document.

If the user asks for an evaluation or rating, clearly explain the criteria used for the evaluation and base it on the content of the document.

DOCUMENT:
{document_text}

USER QUESTION:
{question}
"""

            try:

                with st.spinner(
                    "🤖 Gemini is analyzing your document..."
                ):

                    interaction = client.interactions.create(
                        model="gemini-3.8-flash",
                        input=prompt
                    )

                answer = interaction.output_text

                # Save question and answer
                st.session_state.chat_history.append(
                    {
                        "question": question,
                        "answer": answer
                    }
                )

                # Refresh the page
                st.rerun()

            except Exception as e:

                st.error("❌ Gemini API Error")

                st.code(
                    str(e),
                    language="text"
                )

    # Clear conversation button
    if st.session_state.chat_history:

        if st.button("🗑️ Clear Questions and Answers"):

            st.session_state.chat_history = []

            st.rerun()
