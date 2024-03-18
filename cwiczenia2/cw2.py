import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import random as rand

def get_links(url):
    response = requests.get(url)
    bs = BeautifulSoup(response.text, 'html.parser')
    links = bs.find_all('a', href=True)
    absolutes = [urljoin(url, link['href']) for link in links]
    return list(set(absolutes))

def draw_link_no(link_cnt):
    if link_cnt == 0:
        return -1
    return rand.randint(0,link_cnt-1)

def is_valid_link(website_url):
    if website_url.find('https://') != -1 and len(website_url) > len('https://'):
        return True
    return False
    

def main():
    visited_sites = []

    website_url = input("Enter the URL of the source to crawl: ")
    initial_link = website_url
    if is_valid_link(initial_link) == False:
        print('Start value must be a valid link!')
        return -1;
    
    seed = rand.randint(0,1000)
    print(seed)
    rand.seed(seed)
    i = 1
    while i <= 100:
        try:
            if is_valid_link(website_url):
                links = get_links(website_url)
                
                index = draw_link_no(len(links))
                
                if index == -1:
                    raise Exception('No links found on current website.')
                else:
                    #url is assigned only when it has more than 0 links 
                    visited_sites.append(website_url)
                    print(f'próba {i},ilosc linków: {len(links)},index: {index}\n adres url: {website_url}')
                    
                    #assign new url
                    website_url = links[index]
                    i += 1
            else:
                raise Exception('Link not valid.')
            
        except Exception as e:
                print(f'Wykryto błąd: {e}')
                if len(visited_sites) == 0:
                    print('Empty link list. Strting from beginning.')
                    website_url = initial_link
                    i = 1
                else:
                    website_url = visited_sites[-1]
                    del visited_sites[-1]
        
        
          
if __name__ == "__main__":
 main()