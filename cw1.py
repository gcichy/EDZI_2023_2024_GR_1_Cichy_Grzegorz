import requests
from bs4 import BeautifulSoup
import re

def get_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # mw-parser-output to klasa HTML uzywana na platformie MediaWiki - jest glownym kontenerem dla tresci
    content = soup.find('div', class_='mw-parser-output').text
    return content

def process_text(text):
    text = text.lower()
    text = re.sub(r'[\n\t]',' ', text)
    text = re.sub(r'[^a-z0-9 ]','', text)
    return text

def get_ranked_words(text):
    words = text.split(' ')
    ranked_words = dict()
    for w in words:
        if w in ranked_words:
            ranked_words[w] += 1
        else:
            ranked_words[w] = 1
    del ranked_words['']        
    ranked_words = dict(sorted(ranked_words.items(), key=lambda item: item[1],reverse=True))   
    
    output_string = ''
    counter = 1
    for key, item in ranked_words.items():
        if(counter) > 100:
            break
        output_string += f"{str(counter)};{key};{item}\n"
        counter += 1

    return output_string

def write_results(full_path, results, filename):
    try:
        with open(full_path + filename, 'w') as file:
            file.write(results)
        print('File saved successfully.')
    except Exception as e:
        print(f'Error occurred while saving the file: {e}')
        

def main():
    url = 'https://en.wikipedia.org/wiki/Web_scraping'
    text = get_text(url)
    cleaned_text = process_text(text)

    final_words = get_ranked_words(cleaned_text)
    full_path = "C:\\Users\\gcich\\OneDrive\\Pulpit\\Magister\\Semestr1\\EkstrakcjaDanych\\"
    write_results(full_path, final_words, 'output.txt')

if __name__ == "__main__":
    main()