import requests
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re

headers = {"Accept-Language": "en-US, en;q=0.5"}
url = 'https://www.boxofficemojo.com/month/{month}/{year}/?grossesOption=calendarGrosses'
movie_url = 'https://www.boxofficemojo.com/{}'
months = ["january","february","march","april","may","june","july","august","september","october","november","december"]

# go year by year

# within each year, go by month

# for each month, go through the list in order of Gross

# store the ranking of the movie in a variable

# click on the movie and go to details

# get the genres of the movie

# push the rank into an array for the genres of that movie

# at the end, average and convert to percentile version

def main():

    box_office_df = pd.read_csv('box_office_cols.csv')
    
    for year in range(2021,2022):    
        print("Starting...")
        
        for month in months[:6]:
            temp_ranks = dict((genre, []) for genre in list(box_office_df)[2:])

            results = requests.get(url.format(month=month, year=year), headers=headers)
            main_site = BeautifulSoup(results.text, 'html.parser')

            rows = main_site.findAll('tr')[1:]
            size = float(len(rows))

            for row in rows:
                row_data = row.findAll('td')[:2]
                rank = int(row_data[0].text)
                print(rank)
                extension = row_data[1].find('a')['href']

                results_2 = requests.get(movie_url.format(extension), headers=headers)
                movie_site = BeautifulSoup(results_2.text, 'html.parser')

                try:
                    genres = str(movie_site.find(text="Genres").findNext('span').contents[0])
                    genres = re.split(', |\n',genres)
                    genres = [x.strip() for x in genres if len(x.strip()) > 1]
                    
                    #print("genre: ", genre,"rank:",rank,"/",size," = ", round(rank/size,5))

                    for genre in genres:
                        percentile_score = round(1-(rank/size),5)
                        temp_ranks[genre].append(percentile_score)
                except:
                    pass

            temp_ranks = dict((key,round(np.mean(vals),5)) if len(vals) != 0 else (key,0) for key,vals in temp_ranks.items()) | {'Year': year, 'Month': month.capitalize()}
            box_office_df = box_office_df.append(temp_ranks,ignore_index=True)
            box_office_df.to_csv('box_office_dataset.csv', mode='a', header=False, index=False)
            box_office_df = box_office_df.iloc[0:0]

    print("Complete!")
    

if __name__ == "__main__":
    main()