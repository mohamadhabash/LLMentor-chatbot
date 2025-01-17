import sys
sys.path.append('.')

import streamlit as st
from app.qa_model import QAModel
import numpy as np
import os
import time

class ChatbotApp:
    def __init__(self):
        # Initialize the QA Model
        if "qa_model" not in st.session_state:
            st.session_state["qa_model"] = QAModel(
                repo_path="."
            )

        self.qa_model = st.session_state["qa_model"]
        self.users = {"student1": {"password": "password1", "grade": "Grade 4"},
                      "student2": {"password": "password2", "grade": "Grade 5"}}
        self.authenticated = False
        self.selected_grade = None
        self.indices = None
        self.chunk_mappings = None

    def set_page_config(self):
        st.set_page_config(page_title="Grade-Specific Chatbot", page_icon="🤖", layout="wide")

    def login_callback(self, username, password):
        """Callback function to handle login logic."""
        user_info = self.users.get(username)
        if user_info and user_info["password"] == password:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.session_state["user_grade"] = user_info["grade"]
            success = st.sidebar.success(f"Welcome, {username}! Your grade is {st.session_state['user_grade']}.")
            time.sleep(2)
            success.empty()
        else:
            st.sidebar.error("Invalid username or password.")


    def login(self):
        st.sidebar.header("User Login")
        username = st.sidebar.text_input("Username", key="username_input")
        password = st.sidebar.text_input("Password", type="password", key="password_input")
        
        if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
            st.session_state["authenticated"] = False
            st.session_state["username"] = None
            st.session_state["user_grade"] = None

        # Use on_click callback for login button
        st.sidebar.button(
            "Login",
            on_click=self.login_callback,
            args=(username, password),  # Pass username and password to the callback
        )





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

        # Handle Authentication
        if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
            self.login()
        else:
            self.selected_grade = st.session_state["user_grade"]

            # Load data for the user's grade (cached)
            self.indices, self.chunk_mappings = self.load_grade_data(self.selected_grade)

            # Welcome Message
            st.markdown(f"### Welcome, {st.session_state['username']}! Your grade is {st.session_state['user_grade']}.")

            # Main Chatbot UI
            self.main_ui()




if __name__ == "__main__":
    app = ChatbotApp()
    app.run()
