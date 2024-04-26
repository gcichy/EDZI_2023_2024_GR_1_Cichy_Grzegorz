import requests
import json
import pandas as pd
import numpy as np


def get_response(code):
    url = f"http://api.nbp.pl/api/exchangerates/rates/A/{code}/last/25/?format=json"
    return requests.get(url) 

def get_currency_data(code):
    response = get_response(code)
    print(response.json())
    data = response.json()['rates']
    currency = response.json()['currency']
    code = response.json()['code']
    df =  pd.DataFrame(data)
    df['currency'] = currency
    df['code'] = code
    return df

def create_df(code_list):
    df = None
    for code in code_list:
        if type(df) != pd.DataFrame:
            df = get_currency_data(code)
            
        else:
            df = pd.concat([df,get_currency_data(code)],axis=0) 
    return df   


def denormalize_data(data):
    print('halo')
    table_currency = pd.DataFrame(data={
        'id': [i for i in range(len(data['code'].unique()))],
        'code': data['code'].unique(),
        'currency': data['currency'].unique()     
    }) 
    print('halo')
    table_rates = data.merge(table_currency, on='code')
    table_rates['currency_id'] = table_rates['id']
    table_rates['id'] = [i for i in range(table_rates.shape[0])] 
    table_rates = table_rates[['id','effectiveDate','no','mid','currency_id']]
    
    return (table_currency,table_rates)
    
    
def main():
    code_list = ['USD','CHF','EUR','GBP','JPY']
    
    df = create_df(code_list)

    table_currency, table_rates = denormalize_data(df)
    table_currency.to_json(r'C:\Users\gcich\OneDrive\Pulpit\Magister\Semestr1\EkstrakcjaDanych\cwiczenia6\table_currency.json',index=False)
    table_rates.to_json(r'C:\Users\gcich\OneDrive\Pulpit\Magister\Semestr1\EkstrakcjaDanych\cwiczenia6\table_rates.json',index=False)
    

if __name__ == "__main__":
    main()