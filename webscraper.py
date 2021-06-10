import requests
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re

headers = {"Accept-Language": "en-US, en;q=0.5"}
movie_data = pd.DataFrame(columns=['Year','Rank','Title', 'Genre', 'Critic_Rating','Audience_Rating','Box_Office_USA'])

def main():
  for year in range(2000, 2001):
    url = 'https://www.rottentomatoes.com/top/bestofrt/?year=' + str(year)
    results = requests.get(url, headers=headers)
    soup = BeautifulSoup(results.text, "html.parser")
    containers = soup.find_all('table', class_='table')
    
    extract_movie_details(containers,year)    
    print(year, "done")
  print (movie_data)   

  #movie_data.to_csv('movie_df.csv',index=False) <-- to prevent any accidental overriding
  

def extract_movie_details(containers_passed, year_passed):
  for container in containers_passed:
    i = 0
    for row in container.findAll('tr')[1:]:
      movie_rank_container = row.findAll("td", {"class":"bold"})
      movie_rank = movie_rank_container[0].text[:-1]
      
      movie_name_container = row.findAll("a", {"class":"unstyled articleLink"})
      movie_name = movie_name_container[0].text.strip()

      movie_link = "https://www.rottentomatoes.com/" + movie_name_container[0]['href']

      movie_details = requests.get(movie_link, headers=headers)  
      movie_soup = BeautifulSoup(movie_details.text, "html.parser")
      
      if i > 5: break

      i += 1
      print(i,movie_name)

      try:
        #language = movie_soup.find_all('div', string="English\n                    ")[0].text
        check_usa = movie_soup.find_all('div', string="Box Office (Gross USA):")[0].text
        print ("check_usa:", check_usa)
        #box_office = movie_soup.find_all('div', string="$")[0].text
        genres = movie_soup.find_all('div', class_="meta-value genre")[0].text
        genres = re.split(', |\n',genres)
        genres = [x.strip() for x in genres if len(x.strip()) > 1]
        
        scores = movie_soup.find('score-board')
        critic_rating= scores['tomatometerscore']
        audience_rating = scores['audiencescore']

        valid_movie = {'Year': year_passed, 'Rank': movie_rank, 'Title': movie_name, 'Genre': genres, 'Critic_Rating': critic_rating, 'Audience_Rating': audience_rating, 'Box_Office_USA': box_office}
        movie_data = movie_data.append(valid_movie, ignore_index=True)
      except:
        pass    

if __name__ == "__main__":
    main()