import os
import spacy
from openai import OpenAI
from dotenv import load_dotenv
import subprocess

# Load environment variables from .env file
load_dotenv()

# Ensure the spaCy model is available
def ensure_spacy_model():
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("Downloading spaCy model...")
        subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
        nlp = spacy.load("en_core_web_sm")
    return nlp

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
        # Preprocess the query using NLP
        preprocessed_query = preprocess_query(query)

        # Create the prompt for OpenAI, adding file context if available
        file_context = ""
        if columns and sample_data:
            file_context = f"Columns: {columns}\nSample Data:\n{sample_data}\n"
        
        prompt = f"{file_context}Generate an Excel formula for: {preprocessed_query}"

        # Call OpenAI API
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
