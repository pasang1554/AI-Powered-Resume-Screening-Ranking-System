import nltk
import os


def download_nltk_data():
    resources = [
        "punkt",
        "punkt_tab",
        "stopwords",
        "wordnet",
        "averaged_perceptron_tagger",
        "averaged_perceptron_tagger_eng",
    ]

    for resource in resources:
        try:
            nltk.data.find(f"tokenizers/{resource}") if "punkt" in resource else None
            nltk.data.find(f"corpora/{resource}") if resource not in [
                "punkt",
                "punkt_tab",
            ] else None
            print(f"✓ {resource} already downloaded")
        except LookupError:
            try:
                nltk.download(resource, quiet=True)
                print(f"✓ Downloaded {resource}")
            except Exception as e:
                print(f"✗ Failed to download {resource}: {e}")


if __name__ == "__main__":
    print("Checking NLTK resources...")
    download_nltk_data()
    print("\nNLTK setup complete!")
