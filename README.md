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

## Demo GIF

### Without Authentication (Dropdown Menu)
![Without Authentication](https://i.imgur.com/kmVlQdK.gif)

### With Authentication
![With Authentication](https://i.imgur.com/UJZ1kGV.gif)

#### **Login Credentials**:
- **Grade 4**: 
  - Username: `student1`
  - Password: `password1`
- **Grade 5**: 
  - Username: `student2`
  - Password: `password2`

---

## Example Questions and Generated Responses
### **Grade 4 Examples**
- **Question**: "Describe the animals in Ajloun Forest."
  - **Response**: "In Ajloun Forest, there are big animals like deer, jackals, and wolves. Jackals and wolves are more dangerous than deer. There are also small animals like squirrels that live in the trees."
- **Question**: "What time did Uncle Issa arrive?"
  - **Response**: "According to the context, Uncle Issa arrived at 11 o'clock in the morning."

### **Grade 5 Examples**
- **Question**: "Answer this question from ACCIDENTAL INVENTIONS!: Read and circle. Which fact isn’t mentioned?"
  - **Response**: The correct answer is:(b) The second food he cooked in the microwave was an egg. The passage doesn't mention what the second food was that Percy Spencer cooked in the microwave. It only mentions that the first food was popcorn!"
    
- **Question**: "Where are rugs and carpets made?"
  - **Response**: "Rugs and carpets are made in Amman, Jordan."

### **Out-of-Scope Question**
- **Question**: "Who invented electricity?"
  - **Response**: "Sorry, I can only answer questions based on the books for your grade."

---

## Repository Structure
```
grade-specific-chatbot/
├── Dockerfile
├── LICENSE
├── README.md
├── app
│   ├── __init__.py
│   ├── chatbot_ui.py
│   ├── chatbot_ui_with_auth.py
│   └── qa_model.py
├── data
│   ├── Grade4A
│   │   ├── Grade4A_page_1.txt
│   │   ├── Grade4A_page_2.txt
│   │   ├── etc
│   ├── Grade4B
│   │   ├── Grade4B_page_1.txt
│   ├── Grade5A
│   │   ├── Grade5A_page_1.txt
│   ├── Grade5B
│   │   ├── Grade5B_page_1.txt
│   └── vectorDB
│       ├── Grade 4
│       │   ├── chunks.json
│       │   └── embeddings.npy
│       └── Grade 5
│           ├── chunks.json
│           └── embeddings.npy
├── data_processing
│   ├── extract_text.py
│   └── utils.py
└── requirements.txt
```

---

## Working Pipeline
The following pipeline outlines how the chatbot processes and retrieves answers:

### **1. Text Extraction**
- Text is extracted from the provided textbooks in **page-based chunks**, ensuring that the retrieved content aligns with the user’s query.
- The page structure is preserved for accurate retrieval.

### **2. Preprocessing and Text Cleaning**
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
     - Replaced sequences of repeated characters with normalized forms (e.g., `"aanndd" → "and"`).
     - Applied normalization to all words to ensure consistency.
  4. **Remove Non-English or Non-Numeric Characters**:
     - Removed any characters outside English alphabets, numbers, and standard punctuation.

This cleaning ensures that the text extracted from PDFs is consistent, readable, and ready for embedding and retrieval steps.


### **3. Generating and Saving Embeddings**
- Used the **Jais Model** (`jinaai/jina-embeddings-v2-base-en`) via Hugging Face to generate high-quality embeddings for each page.
- The embeddings are saved to a **FAISS index**, enabling efficient similarity-based retrieval.

### **4. FAISS-Based Retrieval**
- How it works:
  1. Converts the user query into embeddings.
  2. Searches the FAISS index to retrieve the top-k most relevant pages (chunks).
  3. Returns the relevant pages and similarity scores.

### **5. Context and Query Formation**
- Relevant pages (retrieved chunks) are combined to form the context.
- The query and context are structured as:
  ```plaintext
  "You are an educational assistant. Answer questions using the provided context. If the context is not related, you should answer with: Sorry, I can only answer questions based on the books for your grade.

  Context: [Retrieved Chunks]

  Question: [User's Query]"
  ```

### **6. Response Generation**
- Uses the Groq API with Llama3 to generate responses:
  - If the context is relevant, generates a detailed answer.
  - If not, and chunks similarity scores are lower than threshold, returns the fallback response: 
    ```plaintext
    "Sorry, I can only answer questions based on the books for your grade."
    ```

---

## Running using Docker Instructions

### **1. Pull the Docker Image from Dockerhub** [![Docker Pulls](https://img.shields.io/docker/pulls/mohammadhabash/grade-specific-chatbot)](https://hub.docker.com/r/mohammadhabash/grade-specific-chatbot)
```bash
docker pull mohammadhabash/grade-specific-chatbot:latest
```
### OPTIONAL: Alternatively, Build Docker Image Locally
If you prefer building the image locally:
  #### Clone the repository:
  ```bash
    git clone https://github.com/mohamadhabash/grade-specific-chatbot.git
    cd grade-specific-chatbot
  ```
  #### Build the Docker image:
  ```bash
    docker build -t mohammadhabash/grade-specific-chatbot:latest .
  ```


### **2. Run the Docker Image**
- Without Authentication (Dropdown menu)
  ```bash
  docker run -p 8501:8501 mohammadhabash/grade-specific-chatbot:latest
  ```
- With Authentication
  ```bash
  docker run -p 8501:8501 mohammadhabash/grade-specific-chatbot:latest streamlit run app/chatbot_ui_with_auth.py
  ```

### **3. Access the App**
```
http://localhost:8501
```

---

## Contribution
```
Feel free to fork the repository, open issues, or submit pull requests. Contributions are welcome!
```

## License
```
This project is licensed under the GNU Affero General Public License (AGPL) for non-commercial use.
Commercial use requires a separate license. Please contact mshabash187@gmail.com for details.
```

