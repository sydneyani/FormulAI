import os
import subprocess
import sys

import spacy
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure the spaCy model is available
def ensure_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        print("Downloading spaCy model...")
        subprocess.run(
            [sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
            check=True,
        )
        return spacy.load("en_core_web_sm")

nlp = ensure_spacy_model()  # Ensure the model is loaded

def preprocess_query(query):
    # Process the query using spaCy
    doc = nlp(query)

    # Lemmatize and remove stopwords
    filtered_tokens = [
        token.lemma_ for token in doc
        if not token.is_stop and not token.is_punct
    ]

    # Return the preprocessed query as a string
    return " ".join(filtered_tokens)

def generate_formula(query, columns=None, sample_data=None):
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "Error generating formula: OPENAI_API_KEY is not set."

        # Preprocess the query using NLP
        preprocessed_query = preprocess_query(query)

        # Create the prompt for OpenAI, adding file context if available
        file_context = ""
        if columns and sample_data:
            file_context = f"Columns: {columns}\nSample Data:\n{sample_data}\n"
        
        prompt = f"{file_context}Generate an Excel formula for: {preprocessed_query}"

        # Call OpenAI API
        client = OpenAI(api_key=api_key)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-4o-mini-2024-07-18"
        )

        # Extract the generated message from the response
        formula = chat_completion.choices[0].message.content.strip()

        return formula
    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        return "Error generating formula."
