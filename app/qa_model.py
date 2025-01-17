import os
import json
from typing import List, Dict, Tuple
from groq import Groq
from transformers import AutoModel, AutoTokenizer
import faiss
import numpy as np
from tqdm.auto import tqdm
import torch

class QAModel:
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.data_path = os.path.join(repo_path, "data")
        self.vector_db_path = os.path.join(repo_path, "data", "vectorDB")

        # Groq Initialization
        self.groq = Groq(api_key="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")
        self.model_name = "llama3-70b-8192"
        self.temperature = 0

        # Load Embedding Model
        self.embedding_model = AutoModel.from_pretrained(
            "jinaai/jina-embeddings-v2-base-en", trust_remote_code=True
        )
        self.embedding_tokenizer = AutoTokenizer.from_pretrained(
            "jinaai/jina-embeddings-v2-base-en", trust_remote_code=True
        )

    def generate_embeddings(self, text: str) -> List[float]:
        inputs = self.embedding_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            embeddings = self.embedding_model(**inputs).pooler_output
        return embeddings.squeeze().tolist()

    def load_text_files_page_based(self, grade_books: Dict[str, List[str]]) -> Dict[str, List[str]]:
        text_chunks = {}
        for grade, books in grade_books.items():
            grade_chunks = []
            for book_path in books:
                with open(book_path, "r", encoding="utf-8") as f:
                    pages = f.read().split("\n---PAGE BREAK---\n")
                    grade_chunks.extend([page.strip() for page in pages if page.strip()])
            text_chunks[grade] = grade_chunks
        return text_chunks

    def build_faiss_index(self, chunks: List[str]) -> Tuple[faiss.IndexFlatL2, Dict[int, str]]:
        print("Generating Embeddings...")
        embeddings = [self.generate_embeddings(chunk) for chunk in tqdm(chunks)]
        embeddings = np.vstack(embeddings).astype("float32")
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        chunk_mapping = {i: chunk for i, chunk in enumerate(chunks)}
        return index, chunk_mapping

    def build_or_load_faiss_index(self, chunks: List[str], grade: str) -> Tuple[faiss.IndexFlatL2, Dict[int, str]]:
        save_path = os.path.join(self.vector_db_path, grade)
        if os.path.exists(os.path.join(save_path, "embeddings.npy")):
            print(f"Loading saved embeddings for {grade}...")
            embeddings, chunk_mapping = self.load_embeddings(save_path)
        else:
            print(f"Generating embeddings for {grade}...")
            embeddings = np.vstack([self.generate_embeddings(chunk) for chunk in tqdm(chunks)]).astype("float32")
            chunk_mapping = {i: chunk for i, chunk in enumerate(chunks)}
            self.save_embeddings(chunks, embeddings, save_path)

        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        return index, chunk_mapping

    def save_embeddings(self, chunks: List[str], embeddings: np.ndarray, save_path: str):
        os.makedirs(save_path, exist_ok=True)
        np.save(os.path.join(save_path, "embeddings.npy"), embeddings)
        with open(os.path.join(save_path, "chunks.json"), "w", encoding="utf-8") as f:
            json.dump(chunks, f)

    def load_embeddings(self, load_path: str) -> Tuple[np.ndarray, Dict[int, str]]:
        embeddings = np.load(os.path.join(load_path, "embeddings.npy"))
        with open(os.path.join(load_path, "chunks.json"), "r", encoding="utf-8") as f:
            chunks = json.load(f)
        chunk_mapping = {i: chunk for i, chunk in enumerate(chunks)}
        return embeddings, chunk_mapping

    def retrieve_chunks_faiss(self, index: faiss.IndexFlatL2, chunk_mapping: Dict[int, str], query: str, top_k=3) -> Tuple[List[str], List[float]]:
        query_embedding = np.array(self.generate_embeddings(query)).astype("float32")[np.newaxis, :]
        distances, indices = index.search(query_embedding, top_k)
        chunks = [chunk_mapping[idx] for idx in indices[0]]
        scores = [1 / (1 + distance / 2) if distance > 0 else 1.0 for distance in distances[0]]
        print("Scores:", scores)
        return chunks, scores

    def generate_response(self, question: str, chunks: List[str], average_score: float, threshold=0.4) -> str:
        if average_score < threshold:
            return "Sorry, I can only answer questions based on the books for your grade."

        context = "\n\n".join(chunks)
        chat_completion = self.groq.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an educational assistant. Answer questions using the provided context. If the context is not related, you should answer with: Sorry, I can only answer questions based on the books for your grade."
                    + f"\n\nContext: {context}\n",
                },
                {"role": "user", "content": f"Question: {question}"},
            ],
            model=self.model_name,
            temperature=self.temperature,
        )
        return chat_completion.choices[0].message.content.strip()

if __name__ == "__main__":
    qa_model = QAModel(repo_path="/mnt/c/Users/Mohammed Habash/Desktop/classera-assignment/grade-specific-chatbot/")

    # Example Grade-Books Mapping
    grade_books = {
        "Grade 4": [
            f"{qa_model.data_path}/Grade4A/{file}" for file in os.listdir(f"{qa_model.data_path}/Grade4A")
        ] + [
            f"{qa_model.data_path}/Grade4B/{file}" for file in os.listdir(f"{qa_model.data_path}/Grade4B")
        ],
        "Grade 5": [
            f"{qa_model.data_path}/Grade5A/{file}" for file in os.listdir(f"{qa_model.data_path}/Grade5A")
        ] + [
            f"{qa_model.data_path}/Grade5B/{file}" for file in os.listdir(f"{qa_model.data_path}/Grade5B")
        ],
    }

    # Step 1: Load and Chunk Data
    text_chunks = qa_model.load_text_files_page_based(grade_books)

    # Step 2: Build FAISS Indices for Each Grade
    indices = {}
    chunk_mappings = {}
    for grade, chunks in text_chunks.items():
        indices[grade], chunk_mappings[grade] = qa_model.build_or_load_faiss_index(chunks, grade)

    # Step 3: Example Query
    user_grade = "Grade 5"
    user_question = "Continue this and tell me in which section: If you’re happy and you know it,"
    retrieved_chunks, scores = qa_model.retrieve_chunks_faiss(indices[user_grade], chunk_mappings[user_grade], user_question, top_k=5)

    response = qa_model.generate_response(user_question, retrieved_chunks, np.mean(scores), threshold=0.5)

    print(f"Question: {user_question}")
    print(f"Answer: {response}")
