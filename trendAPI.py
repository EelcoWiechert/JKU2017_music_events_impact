from google_trend import *
from linewriter import *

import time
import random

LOCATION_TREND_SOURCE_CSV = 'data/country_cid.csv'
EVENT_FILE = 'data/events.csv'

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

