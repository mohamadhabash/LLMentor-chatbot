import re

def clean_text(text):
    text = " ".join(text.split()).replace(" .", ".").replace(" ,", ",") # Clean up excessive whitespace
    text = re.sub(r'W?WC.*?P?PMM?', '', text)  # Remove anything starting with W/WWCC and ending with PM/PPMM
    text = re.sub(r'\b(?:https?://|www\.)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}\b(?:/[^\s]*)?', '', text)  # Remove URLs
    text = re.sub(r'CD\d+ \d+', '', text)  # Remove CD references
    text = re.sub(r'\d{2}\/\d{2}\/\d{4}', '', text)  # Remove dates
    text = re.sub(r'\d{1,2}::\d{2}', '', text)  # Remove times

    # Function to handle repeated character normalization
    def normalize_repeated_chars(match):
        word = match.group()
        # Replace sequences of 3+ identical characters with a single character
        return re.sub(r'(.)\1{2,}', r'\1', word)

    # Remove double-repeated characters (aanndd, LLeeaarrnn)
    text = remove_doubled_chars(text)

    # Apply normalization to the entire text
    text = re.sub(r'\b\w+\b', normalize_repeated_chars, text)

    # Normalize "Unit" numbers to single digits
    text = re.sub(r'Unit (\d)\d*', r'Unit \1', text)

    # Remove non-English, non-numeric characters
    text = re.sub(r'[^a-zA-Z0-9\s.,!?\']+', '', text)

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def remove_doubled_chars(sentence):
    words = sentence.split()
    new_words = []
    for word in words:
        if all(word[i] == word[i + 1] for i in range(0, len(word) - 1, 2)):
            fixed_word = "".join(word[i] for i in range(0, len(word), 2))
        else:
            fixed_word = word  
        new_words.append(fixed_word)
    return " ".join(new_words)