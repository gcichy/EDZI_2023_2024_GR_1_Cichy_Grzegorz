# %%
import requests
import json
import pandas as pd
import numpy as np


cities = ['bialystok','gdansk','gorzow','katowice','kielce','krakow','lublin','lodz','olsztyn','opole','poznan','rzeszow','szczecin','torun','warszawa','wroclaw','zielonagora']
base_url = 'https://danepubliczne.imgw.pl/api/data/synop/station/'
df = None
i = 0
for city in cities:
    i+=1
    url = base_url + city
    response = requests.get(url)
    row = json.loads(response.text)
    if type(df) != pd.DataFrame:
        df = pd.DataFrame(row,index=[0])
        print(df)
    else:
        df = pd.concat([df,pd.DataFrame(row,index=[i])],axis=0)

df

df['temperatura'] = df['temperatura'].astype(float)
df['suma_opadu'] = df['suma_opadu'].astype(float)
df['cisnienie'] = df['cisnienie'].astype(float)

print('1.Średnia temperatura punktów pomiarowych')
print(f"Średnia temperatura: {np.round(df['temperatura'].mean(),2)}")


print('2. Mainimalna temperatura wraz z miejscem pomiaru')
minim = df.loc[df['temperatura'].idxmin(),['temperatura','stacja']]
print(f"Minimalna temperatura: {minim['stacja']}, {minim['temperatura']}")

print('3. Maksymalna temperatura wraz z miejscem pomiaru')
maxim = df.loc[df['temperatura'].idxmax(),['temperatura','stacja']]
print(f"Minimalna temperatura: {maxim['stacja']}, {maxim['temperatura']}")

print('4. Data oraz godzina pomiaru')
print(str(df.loc[0,'data_pomiaru']) + ' ' + str(df.loc[0,'godzina_pomiaru']))

print('5. Średnia wartość opadów')
np.round(df['suma_opadu'].mean(),2)

print('6. Minimalna wartość opadów wraz z miejscem pomiaru')
minim = df.loc[df['suma_opadu'].idxmin(),['suma_opadu','stacja']]
print(f"Minimalny opad: {minim['stacja']}, {minim['suma_opadu']}")

print('7. Maksymalna wartość opadów wraz z miejscem pomiaru')
maxim = df.loc[df['suma_opadu'].idxmax(),['suma_opadu','stacja']]
print(f"Maksymalny opad: {maxim['stacja']}, {maxim['suma_opadu']}")

print('8. Średnia wartość ciśnienia')
np.round(df['cisnienie'].mean(),2)

minim = df.loc[df['cisnienie'].idxmin(),['cisnienie','stacja']]
print(f"Minimalne cisnienie: {minim['stacja']}, {minim['cisnienie']}")

maxim = df.loc[df['cisnienie'].idxmax(),['cisnienie','stacja']]
print(f"Maksymalne cisnienie: {maxim['stacja']}, {maxim['cisnienie']}")

df.to_csv('dane_pogodowe.csv', encoding='ISO-8859-2')
