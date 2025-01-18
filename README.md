# Grade-Specific Chatbot 🤖 [![Docker Pulls](https://img.shields.io/docker/pulls/mohammadhabash/grade-specific-chatbot)](https://hub.docker.com/r/mohammadhabash/grade-specific-chatbot)

A powerful, containerized chatbot designed for Grade 4 and Grade 5 students. This chatbot answers curriculum-specific questions based on textbooks using Retrieval-Augmented Generation (RAG) and FAISS for efficient query matching. **Page-based chunking** has been applied to enhance retrieval performance, ensuring precise alignment between the query and the relevant context from the textbooks. The solution is fully containerized, deployable with Docker, and user-friendly.

---

## Features
- **Page-Based Chunking**: The textbooks are split into pages, allowing efficient retrieval and precise matching of the context.
- **Grade-Specific Responses**: Tailored answers based on grade-level textbooks.
- **Preprocessing and Text Cleaning**: Comprehensive cleaning of extracted text to ensure data quality.
- **Efficient Retrieval**: Uses FAISS for page-based query retrieval.
- **Streamlit UI**: Clean, interactive interface with optional authentication.
- **Dockerized Solution**: Portable and easy to deploy.

---

## Demo Videos

### Without Authentication
[![Without Authentication](https://img.youtube.com/vi/7yHPdQ5G1VM/0.jpg)](https://www.youtube.com/watch?v=7yHPdQ5G1VM)

### With Authentication
[![With Authentication](https://img.youtube.com/vi/<another_video_id>/0.jpg)](https://www.youtube.com/watch?v=<another_video_id>)


---

## Example Questions and Responses
### **Grade 4 Examples**
- **Question**: "What animals live in Ajloun forest?"
  - **Response**: "Ajloun forest is home to foxes, owls, and deer, as mentioned in your textbook."
- **Question**: "What time did Uncle Issa arrive?"
  - **Response**: "Uncle Issa arrived at 7 PM according to the story."

### **Grade 5 Examples**
- **Question**: "Complete this: If you’re happy and you know it..."
  - **Response**: "Clap your hands! This is from the 'Rhythms and Listening' section in your book."

### **Out-of-Scope Question**
- **Question**: "Who discovered electricity?"
  - **Response**: "Sorry, I can only answer questions based on the books for your grade."

---

## Working Pipeline
The following pipeline outlines how the chatbot processes and retrieves answers:

### **1. Text Extraction**
- **Script**: `extract_text.py`
- Text is extracted from the provided textbooks in **page-based chunks**, ensuring that the retrieved content aligns with the user’s query.
- The page structure is preserved for accurate retrieval.

### **2. Preprocessing and Text Cleaning**
- **Script**: `extract_text.py`
- **Steps Performed**:
  1. **Whitespace Cleanup**: Removed excessive whitespace and ensured proper spacing around punctuation (e.g., `" ." → "."`, `" ," → ","`).
  2. **Remove Patterns**:
     - Removed unwanted text patterns like:
       - References starting with `W/WWCC` and ending with `PM/PPMM`.
       - CD references (e.g., `"CD123 45"`).
       - Dates in the format `DD/MM/YYYY`.
       - Times in the format `HH::MM`.
       - URLs.
  3. **Fix Repeated Characters**:
     - Replaced sequences of repeated characters with normalized forms (e.g., `"aaannndd" → "and"`).
     - Applied normalization to all words to ensure consistency.
  4. **Remove Non-English or Non-Numeric Characters**:
     - Removed any characters outside English alphabets, numbers, and standard punctuation.

This cleaning ensures that the text extracted from PDFs is consistent, readable, and ready for embedding and retrieval steps.


### **3. Generating and Saving Embeddings**
- **Script**: `qa_model.py`
- Used the **Jais Model** (`jinaai/jina-embeddings-v2-base-en`) via Hugging Face to generate high-quality embeddings for each page.
- The embeddings are saved to a **FAISS index**, enabling efficient similarity-based retrieval.

### **4. FAISS-Based Retrieval**
- **Script**: `qa_model.py`
- How it works:
  1. Converts the user query into embeddings.
  2. Searches the FAISS index to retrieve the top-k most relevant pages (chunks).
  3. Returns the relevant pages and similarity scores.

### **5. Context and Query Formation**
- **Script**: `qa_model.py`
- Relevant pages (retrieved chunks) are combined to form the context.
- The query and context are structured as:
  ```plaintext
  "You are an educational assistant. Answer questions using the provided context. If the context is not related, you should answer with: Sorry, I can only answer questions based on the books for your grade.

  Context: [Retrieved Chunks]

  Question: [User's Query]"

- Fallback Response: If the context score is below a threshold, the chatbot responds with:

  ```plaintext
  "Sorry, I can only answer questions based on the books for your grade."
