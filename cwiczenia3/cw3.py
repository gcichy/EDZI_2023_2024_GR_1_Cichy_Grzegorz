import urllib.robotparser as rp
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import random as rand
import pandas as pd
import re

class FilmDataModel:
    def __init__(self, parser, name):
        if not isinstance(parser,rp.RobotFileParser):
            raise Exception("Incorrect parser class: parser must be of class rp.RobotFileParser")
            
        self.robots_parser = parser
        self.robots_parser.read()
        self.name = name

    def validate_url(self, url):
        """Use robots.txt parser to check if website can be scraped."""
        return True if self.robots_parser.can_fetch("MyBot", url) else False

    def get_page_html(self, url):
        "set html of model's website"
        if self.validate_url(url):
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3', 'Accept-Language': 'en-US,en;q=0.9'})
            return response.text
        else:
            raise Exception("This link is not allowed for scraping by robots.txt")

    @staticmethod
    def get_elements(page_html, select_phrase):
        """get elements of the website using soup.select method."""
        soup = BeautifulSoup(page_html, 'html.parser')
        return soup.select(select_phrase)

    @staticmethod
    def getPattern(tag_list, pattern, limit, output_datatype = 'int'):
        """searches for given pattern in input_list"""
        output_list = []
        for i in range(limit):
            match = re.search(pattern,tag_list[i].text)
            if match:
                if output_datatype == 'int':
                    match = int(match.group())
                elif output_datatype == 'float':
                    match = float(match.group())
                    
                output_list.append(match)
            else:
                output_list.append(0)
        return output_list
    
    @staticmethod
    def left_trim_by_pattern(tag_list, pattern, limit):
        """Trimms stings given in a list basing on provided pattern"""
        output_list = []
        for i in range(limit):
            split_list = re.split(pattern,tag_list[i].text)
            print(split_list)
            if len(split_list) == 2:
                output_list.append(split_list[1])
            else:
                output_list.append('')
        return output_list

class Utils:
    @staticmethod
    def get_page_html(url):
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3', 'Accept-Language': 'en-US,en;q=0.9'})
        return response.text

    @staticmethod
    def get_rotten_movie_score(row):
        """gets score for the movie provided in row from rottentomatoes website"""

        url = 'https://www.rottentomatoes.com/search?search=' + row['title']
        page_html = Utils.get_page_html(url)

        films = FilmDataModel.get_elements(page_html,"search-page-media-row")
        for i in range(len(films)):

            if(films[i]['releaseyear'] == str(row['year'])):
                title = FilmDataModel.get_elements(str(films[i]),'a[slot="title"]')[0]
                print(title.text.strip())
                if title.text.strip() == row['title']:
                    try:
                        score = int(films[i]['tomatometerscore'])
                    except:
                        score = None
                    return score
                break
        
        return None
    
    @staticmethod
    def create_films_df():
        """creates dataframe for the task of film comparison"""
        imdb_model = FilmDataModel(rp.RobotFileParser('https://www.imdb.com/robots.txt'),'IMDB model')
        page_html = imdb_model.get_page_html('https://www.imdb.com/chart/top/?ref_=nv_mv_250')
        titles = FilmDataModel.get_elements(page_html,".ipc-metadata-list-summary-item .ipc-title__text")
        ratings = FilmDataModel.get_elements(page_html,".ipc-metadata-list-summary-item .ratingGroup--imdb-rating")
        years = FilmDataModel.get_elements(page_html,".ipc-metadata-list-summary-item .cli-title-metadata")
        
        titles = FilmDataModel.left_trim_by_pattern(titles,r'^[0-9]+. ', 100)
        ratings = FilmDataModel.getPattern(ratings, r'^[0-9.]+', 100, 'float')
        years = FilmDataModel.getPattern(years, r'^\d{4}', 100, 'int')
        
        return pd.DataFrame({
                             'title' : titles, 
                             'imdb_rank':  [i for i in range(100)],
                             'imdb_rating' : ratings,  
                             "rotten_tomatoes_rating" : [0 for i in range(100)],
                             'year' : years,
                             })


def main():
    try:
        top_list_imdb_rt = Utils.create_films_df()

        for index, row in top_list_imdb_rt.iterrows():
            top_list_imdb_rt.at[index, 'rotten_tomatoes_rating'] = Utils.get_rotten_movie_score(row)
        
        top_list_imdb_rt.columns = ["tytul_filmu","ranking_imdb", "ocena_imdb", "ocena_rotten_tomatoes", "rok_produkcji"]
        
        json_path = r'C:\Users\gcich\OneDrive\Pulpit\Magister\Semestr1\EkstrakcjaDanych\cwiczenia3\films_comparison.json'
        top_list_imdb_rt.to_json(json_path,orient='records')
        
    except Exception as e:
        print(f'Error caught: {e}')
        
        
          
if __name__ == "__main__":
 main()



