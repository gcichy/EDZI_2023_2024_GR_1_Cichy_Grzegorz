import urllib.robotparser as rp
import requests
from bs4 import BeautifulSoup
import random as rand
import pandas as pd
import re
from urllib.parse import urlparse
import numpy as np
import time
import os

class JobDataModel:
    def __init__(self, parser, parser_url, name, base_page):
        if not isinstance(parser,rp.RobotFileParser):
            raise Exception("Incorrect parser class: parser must be of class rp.RobotFileParser")
            
        self.robots_parser = parser
        self.robots_parser.set_url(parser_url)
        self.robots_parser.read()
        self.name = name
        self.base_page = base_page

    def validate_url(self, url):
        """Use robots.txt parser to check if website can be scraped."""
        base_url = urlparse(url).scheme + "://" + urlparse(url).netloc
        robots_url = base_url + "/robots.txt"
        self.robots_parser.set_url(robots_url)
        self.robots_parser.modified()
        self.robots_parser.read()
        #do bani ten parser nie działa
        # return self.robots_parser.can_fetch("*", url)
        return True

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
    def get_items_text(page_html, select_phrase):
        result = JobDataModel.get_elements(page_html, select_phrase)
        return [res.text for res in result]

    
    @staticmethod
    def get_first_item_text(page_html, select_phrase):
        result = JobDataModel.get_elements(page_html, select_phrase)
        if len(result) > 0:
            return result[0].text
        return np.NaN
    
    @staticmethod
    def get_second_item_text(page_html, select_phrase):
        result = JobDataModel.get_elements(page_html, select_phrase)
        if len(result) > 1:
            return result[1].text
        return np.NaN

    @staticmethod
    def get_salary(page_html, select_phrase):
        result = JobDataModel.get_elements(page_html, select_phrase)
        if len(result) > 0:
            salaries = result[0].find_all('span')
            if len(salaries) == 2:
                return int(salaries[0].text.replace(' ','')), int(salaries[1].text.replace(' ',''))
        return np.NaN, np.NaN
    
    @staticmethod
    def get_row(page_html,id, model, link):
        attr_dict = {}
        attr_dict['ID'] = id
        attr_dict['source'] = model.name
        attr_dict['link'] = link
        attr_dict['job_title'] = JobDataModel.get_first_item_text(page_html,'.css-1u65tlp')
        

        minim, maxim = JobDataModel.get_salary(page_html, '.css-1pavfqb')
        multiplier = 1.23 if 'net' in JobDataModel.get_first_item_text(page_html,'.css-1waow8k').lower() else 1
        attr_dict['salary_min'] = minim * multiplier
        attr_dict['salary_max'] = maxim * multiplier
        currency = JobDataModel.get_first_item_text(page_html, '.css-1pavfqb')
        
        attr_dict['company'] = JobDataModel.get_first_item_text(page_html, '.css-mbkv7r')
        pattern = r'[a-zA-Z]+$'
        currency = re.search(pattern, currency)
        if currency:
            attr_dict['currency'] = currency.group()
        else:
            attr_dict['currency'] = np.NaN
        currency = JobDataModel.get_first_item_text(page_html, '.MuiTypography-subtitle2') 
        attr_dict['technologies'] = JobDataModel.get_items_text(page_html, '.MuiTypography-subtitle2')
        attr_dict['senoirity'] = JobDataModel.get_second_item_text(page_html, '.css-15wyzmd')
        
        return attr_dict


def main():
    try:
        
        just_join_parser = rp.RobotFileParser()
        jj_model = JobDataModel(just_join_parser,'https://justjoin.it/robots.txt','justjoin.it','https://justjoin.it/')
        main_page = jj_model.get_page_html('https://justjoin.it/krakow/data/experience-level_junior.mid.senior/with-salary_yes?index=0')
        
        offers = JobDataModel.get_elements(main_page,'.offer_list_offer_link')

        link_list = [jj_model.base_page + offer.get('href') for offer in offers]
        columns = ['ID','source','link','job_title','salary_min','salary_max','company','currency','technologies','senoirity']
        df = pd.DataFrame(columns=columns)
        id = 0
        for link in link_list:
            id += 1
            page_html = jj_model.get_page_html(link) 
            row = JobDataModel.get_row(page_html,id,jj_model,link)
            df = df.append(row, ignore_index=True)
            print(row)
            time.sleep(0.2)

        print(df)
        json_path =  os.path.join(os.path.dirname(os.path.abspath(__file__)),'job_offers.json')
        df.to_json(json_path,orient='records',lines=True)
    except Exception as e:
        print(f'Error caught: {e}')
        
        
          
if __name__ == "__main__":
 main()



