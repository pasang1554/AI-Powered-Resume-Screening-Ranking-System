
import nltk
import os
import shutil

# unexpected error with LazyCorpusLoader
# Try to force download and reload

print("Fixing NLTK data...")

# Define nltk data path
nltk_data_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'nltk_data')
print(f"NLTK Data Path: {nltk_data_path}")

# Delete existing stopwords if they exist to force clean download
stopwords_path = os.path.join(nltk_data_path, 'corpora', 'stopwords')
if os.path.exists(stopwords_path):
    print(f"Removing existing stopwords at {stopwords_path}...")
    try:
        shutil.rmtree(stopwords_path)
    except Exception as e:
        print(f"Error removing stopwords: {e}")

zip_path = os.path.join(nltk_data_path, 'corpora', 'stopwords.zip')
if os.path.exists(zip_path):
    print(f"Removing existing stopwords.zip at {zip_path}...")
    try:
        os.remove(zip_path)
    except Exception as e:
        print(f"Error removing zip: {e}")

# Download again
print("Downloading stopwords...")
nltk.download('stopwords')
print("Downloading punkt...")
nltk.download('punkt')
print("Downloading wordnet...")
nltk.download('wordnet')

# Verify
try:
    from nltk.corpus import stopwords
    print("Testing stopwords load...")
    # Force load
    extracted_words = stopwords.words('english')
    print(f"Successfully loaded {len(extracted_words)} stopwords.")
except Exception as e:
    print(f"Still failing: {e}")
