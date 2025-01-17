import pdfplumber
import os
from tqdm.auto import tqdm

from utils import clean_text

# Paths to the uploaded files
pdf_files = {
    "Grade4A": "../../Grade4A.pdf",
    "Grade4B": "../../Grade4B.pdf",
    "Grade5A": "../../Grade5A.pdf",
    "Grade5B": "../../Grade5B.pdf"
}

# Directory to save the extracted text for review
output_dir = "../data/"
os.makedirs(output_dir, exist_ok=True)

def extract_text_by_page(pdf_path, output_dir, file_prefix):
    os.makedirs(f"{output_dir}/{file_prefix}", exist_ok=True)

    """
    Extracts text from a PDF file page by page, cleaning and sorting words based on
    their positions with priority to top-left text, and saves it to text files.
    :param pdf_path: Path to the PDF file.
    :param output_dir: Directory to save the output text files.
    :param file_prefix: Prefix for the output files.
    """
    extracted_pages = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in tqdm(enumerate(pdf.pages[1:], start=1)):
            # Extract words with position data
            words = page.extract_words()

            # Sort words based on their vertical (top) and horizontal (x0) positions
            sorted_words = sorted(words, key=lambda word: (word['top'], word['x0']))

            # Reconstruct the text in the correct order based on the sorted words
            sorted_text = ""
            current_line = []
            prev_top = None

            for word in sorted_words:
                # If the current word is on a new line (based on the top position), join and add the current line to text
                if prev_top is not None and abs(word['top'] - prev_top) > 2:  # Adjust 2 as needed to handle line breaks
                    sorted_text += ' '.join(current_line) + '\n'
                    current_line = []
                current_line.append(word['text'])
                prev_top = word['top']

            # Add the last line of words
            if current_line:
                sorted_text += ' '.join(current_line)

            # Clean the text
            sorted_text = clean_text(sorted_text)

            extracted_pages.append(sorted_text)

            # Save each page's text into a separate file
            output_file = os.path.join(f"{output_dir}/{file_prefix}", f"{file_prefix}_page_{page_number}.txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(sorted_text)

    return extracted_pages

if __name__ == '__main':
    # Process each uploaded PDF and save the output
    extracted_texts = {}
    for grade, pdf_path in pdf_files.items():
        print(f"Extracting \"{pdf_path}\"")
        extracted_texts[grade] = extract_text_by_page(pdf_path, output_dir, grade)
