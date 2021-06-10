from multiprocessing import pool
import requests
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
from multiprocessing.pool import ThreadPool
import threading
import itertools
import time

headers = {"Accept-Language": "en-US, en;q=0.5"}
url = 'https://www.boxofficemojo.com/month/{month}/{year}/?grossesOption=calendarGrosses'
movie_url = 'https://www.boxofficemojo.com/{}'
months = ["january","february","march","april","may","june","july","august","september","october","november","december"]

def main():

    box_office_df = pd.read_csv('box_office_cols.csv')

    print("starting multithreading...")

    with ThreadPool(1) as pool:
        for year_result in pool.map(df_loops_year,range(2008,2011)):
            box_office_df = box_office_df.append(year_result, ignore_index=True)
    '''
    years = [[range(2000, 2006), range(2006, 2011)], [range(201)]]
    for i in range(2):
        thread1 = threading.Thread(
            target=df_loops_year,
            args=(range(2000,2006),)
        )
        thread2 = threading.Thread(
            target=df_loops_year,
            args=(range(2011,2021),)
        )
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
    '''

    box_office_df.to_csv('box_office_dataset.csv', mode='a', header=False, index=False)
    print("Complete!")

def df_loops_year(year):
    year_df = pd.read_csv('box_office_cols.csv')

    with ThreadPool(2) as pool:
        for month_result in pool.starmap(df_loops_month, zip(months,itertools.repeat(year))):
            year_df = year_df.append(month_result, ignore_index=True)

    return year_df

def df_loops_month(month,_year):
    month_df = pd.read_csv('box_office_cols.csv')
    temp_ranks = dict((genre, []) for genre in list(month_df)[2:])

    results = requests.get(url.format(month=month, year=_year), headers=headers)
    main_site = BeautifulSoup(results.text, 'html.parser')

    rows = main_site.findAll('tr')[1:]
    size = float(len(rows))
    print("YR: ", _year, " MO: ", month)
    for row in rows:
        genre_list,rank = get_genres(row)
        
        try:
            for genre in genre_list:
                percentile_score = round(1-(rank/size),5)
                temp_ranks[genre].append(percentile_score)
        except:
            pass

    temp_ranks = dict((key,round(np.mean(vals),5)) if len(vals) != 0 else (key,0) for key,vals in temp_ranks.items()) | {'Year': _year, 'Month': month.capitalize()}
    month_df = month_df.append(temp_ranks,ignore_index=True)
    return month_df

def get_genres(_row):
    row_data = _row.findAll('td')[:2]
    rank = int(row_data[0].text)
    extension = row_data[1].find('a')['href']
    genres = []
    try:
        results_2 = requests.get(movie_url.format(extension), headers=headers)
        movie_site = BeautifulSoup(results_2.text, 'html.parser')
        genres = str(movie_site.find(text="Genres").findNext('span').contents[0])
        genres = re.split(', |\n',genres)
        genres = [x.strip() for x in genres if len(x.strip()) > 1]
    except:
        pass
    return genres, rank

if __name__ == "__main__":
    main()