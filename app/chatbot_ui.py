import sys
# /mnt/c/Users/Mohammed Habash/Desktop/classera-assignment/grade-specific-chatbot/
sys.path.append('.')

import streamlit as st
from app.qa_model import QAModel
import numpy as np
import os

class ChatbotApp:
    def __init__(self):
        # Initialize the QA Model
        if "qa_model" not in st.session_state:
            st.session_state["qa_model"] = QAModel(repo_path=".")

        self.qa_model = st.session_state["qa_model"]
        self.grades = ["Grade 4", "Grade 5"]
        self.selected_grade = None
        self.indices = None
        self.chunk_mappings = None

    def set_page_config(self):
        st.set_page_config(page_title="Grade-Specific Chatbot", page_icon="🤖", layout="wide")

    def sidebar(self):
        st.sidebar.header("Select Your Grade")
        self.selected_grade = st.sidebar.selectbox("Grade", self.grades)

    @st.cache_resource
    def load_grade_data(_self, grade):
        grade_books = {
            "Grade 4": [
                f"{_self.qa_model.data_path}/Grade4A/{file}" for file in os.listdir(f"{_self.qa_model.data_path}/Grade4A")
            ] + [
                f"{_self.qa_model.data_path}/Grade4B/{file}" for file in os.listdir(f"{_self.qa_model.data_path}/Grade4B")
            ],
            "Grade 5": [
                f"{_self.qa_model.data_path}/Grade5A/{file}" for file in os.listdir(f"{_self.qa_model.data_path}/Grade5A")
            ] + [
                f"{_self.qa_model.data_path}/Grade5B/{file}" for file in os.listdir(f"{_self.qa_model.data_path}/Grade5B")
            ],
        }

        # Load and process chunks for the selected grade
        text_chunks = _self.qa_model.load_text_files_page_based({grade: grade_books[grade]})
        indices, chunk_mappings = _self.qa_model.build_or_load_faiss_index(text_chunks[grade], grade)
        return indices, chunk_mappings

    def main_ui(self):
        st.title("📘 Grade-Specific Chatbot")
        st.markdown("Ask questions based on your grade-specific books.")
        st.markdown("### Enter Your Question Below")

        user_question = st.text_area("Type your question here and press Enter", "")

        if st.button("Get Answer"):
            if not user_question.strip():
                st.warning("Please enter a valid question!")
            else:
                # Retrieve chunks and generate response
                retrieved_chunks, scores = self.qa_model.retrieve_chunks_faiss(
                    self.indices, self.chunk_mappings, user_question, top_k=5
                )
                average_score = np.max(scores)

                response = self.qa_model.generate_response(user_question, retrieved_chunks, average_score, threshold=0.4)

                st.markdown("### Response")
                st.write(response)
                if "Sorry, I can only answer questions based on the books for your grade." not in response:
                    st.markdown("### Relevant Chunks")
                    for chunk in retrieved_chunks:
                        st.markdown(f"**- {chunk}**")

    def run(self):
        self.set_page_config()
        self.sidebar()

        # Load data for the selected grade (cached)
        self.indices, self.chunk_mappings = self.load_grade_data(self.selected_grade)
        self.main_ui()

if __name__ == "__main__":
    app = ChatbotApp()
    app.run()
