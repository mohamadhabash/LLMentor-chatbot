# Use the official Python base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Set PYTHONPATH to include the working directory
ENV PYTHONPATH=/app

# Copy requirements.txt to the container and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Pre-download Hugging Face model to cache it
RUN python -c "from transformers import AutoModel, AutoTokenizer; \
                AutoModel.from_pretrained('jinaai/jina-embeddings-v2-base-en', trust_remote_code=True); \
                AutoTokenizer.from_pretrained('jinaai/jina-embeddings-v2-base-en', trust_remote_code=True)"

# Copy the current project files to the container
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Expose the port that Streamlit runs on
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "app/chatbot_ui.py"]
