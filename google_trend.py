from bs4 import BeautifulSoup
import requests
import pandas as pd
from pytrends.request import TrendReq
import calendar
import time

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
                result = soup.find_all("div", {"class": "widget-single-item-detailed-title-container"})
                trending_searches = []

                for i in result:
                    trending_searches.append(i.text)

                google_trend_links['trending_topics'][index] = trending_searches


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