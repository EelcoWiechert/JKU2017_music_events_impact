import random
from bs4 import BeautifulSoup
import requests
import pandas as pd
from pytrends.request import TrendReq
import calendar
import time
import csv

'''

This scripts collects events from google trend by searching for the search peak value in time

'''

LOCATION_TREND_SOURCE_CSV = '../data/country_cid.csv'
EVENT_FILE = '../data/events.csv'

def write_event(PATH,line):
    with open(PATH, "a") as csv_file:
            writer = csv.writer(csv_file, delimiter=',', dialect='excel')
            writer.writerow(line)

class get_trend_topics_google(object):

    def __init__(self, LOCATION_TREND_SOURCE_CSV):
        self.link = LOCATION_TREND_SOURCE_CSV

    def get_data(self):
        google_trend_links = pd.read_csv(self.link, header=0, sep=';', dtype={'year': 'str'})
        google_trend_links = google_trend_links.fillna('')
        google_trend_links['trending_topics'] = ""

        for index, row in google_trend_links.iterrows():

            # construct link
            link = 'https://trends.google.com/trends/topcharts/widget?cid=' + str(row['cid']) + '&geo=' + str(
                row['country']) + '&date=' + str(row['year']) + '&vm=trendingchart&h=413'
            # "https://trends.google.nl/trends/topcharts/widget?cid=zg406&geo=&date=2012&vm=trendingchart&h=413

            try:
                time.sleep(3)
                response = requests.post(link)
                soup = BeautifulSoup(response.text, "html.parser")
                print(link)
                result = soup.find_all("div", {"class": "widget-single-item-detailed-title-container"})
                trending_searches = []

                for i in result:
                    trending_searches.append(i.text)

                google_trend_links['trending_topics'][index] = trending_searches

                print(trending_searches)
                if len(trending_searches) == 0:
                    print('2')

                    # construct link
                    link = 'https://trends.google.com/trends/topcharts/widget?cid=' + str(row['cid']) + '&geo=' + str(
                        row['country']) + '&date=' + str(row['year']) + '&vm=chart&h=413'

                    time.sleep(3)
                    response = requests.post(link)
                    soup = BeautifulSoup(response.text, "html.parser")
                    result = soup.find_all("span", {"class": "widget-title-in-list"})
                    trending_searches = []

                    for i in result:
                        trending_searches.append(i.text)

                    google_trend_links['trending_topics'][index] = trending_searches

                    print(trending_searches)

            except:
                print('Could not find link')

        return google_trend_links


def event_date(topic, search_year):

    # Login to Google.
    pytrend = TrendReq()

    # high level search for week

    pytrend.build_payload(kw_list=[topic], timeframe=str(search_year) + '-01-01 ' + str(search_year) + '-12-30')

    interest_over_time_df = pytrend.interest_over_time()

    last_day = str(calendar.monthrange(int(search_year), interest_over_time_df[topic].idxmax(axis=0).month)[1]) # find last day of month

    time.sleep(3)

    # low level search for day

    pytrend.build_payload(kw_list=[topic], timeframe=str(search_year) + '-' + str(interest_over_time_df[topic].
                                                                                      idxmax(axis=0).month) + '-01 ' + str(search_year) + '-' + str(interest_over_time_df[topic].idxmax(axis=0).month) + '-' + last_day)
    interest_over_time_df = pytrend.interest_over_time()



    return interest_over_time_df[topic].idxmax(axis=0)


'''

START SCRIPT

'''

x = pd.DataFrame(get_trend_topics_google(LOCATION_TREND_SOURCE_CSV).get_data())

n = 0
for index, row in x.iterrows():
    search_year = row['year']
    search_cat = row['cat']
    for topic in row['trending_topics']:
        time.sleep(random.randint(1, 20))
        trend_date_of_event = event_date(topic, search_year)
        event = []
        event.append(n)
        event.append(topic)
        event.append(trend_date_of_event.year)
        event.append(trend_date_of_event.month)
        event.append(trend_date_of_event.day)
        event.append(search_cat)

        write_event(EVENT_FILE,event)
        n+=1

        print(event)

