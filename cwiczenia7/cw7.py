import requests
import os
from summarizer import Summarizer

def get_random_wikipedia_article_text():
    # Endpoint URL for the MediaWiki API
    endpoint = "https://en.wikipedia.org/w/api.php"

    article_params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "titles": "Silesia", #Here come the title you want to get
        "explaintext": True  # Return plain text instead of HTML
    }
    article_response = requests.get(endpoint, params=article_params)
    if article_response.status_code == 200:
        article_data = article_response.json()
        # Extract the text of the article
        article_text = next(iter(article_data["query"]["pages"].values()))["extract"]
        return article_text
    else:
        print("Failed to fetch article text")

def save_file(file_name, text):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),file_name)

    with open(path, 'w', encoding='utf-8') as file:
        file.write(text)
        
def main():

    random_article_text = get_random_wikipedia_article_text()

    save_file('org.txt', random_article_text)
    
    model = Summarizer()
    result = model(random_article_text, ratio=0.3)  # Specified with ratio
    save_file('outcome.txt', result)

    
if __name__ == "__main__":
    main()