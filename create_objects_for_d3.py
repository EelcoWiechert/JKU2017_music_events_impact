from statsmodels.tsa.seasonal import seasonal_decompose
import json
import pandas as pd
from collections import OrderedDict
import numpy as np
import matplotlib.pylab as plt
import time

def read_top_artists(a_file):

    # READ ARTISTS
    artist_id = read_artists_reversed("../data/LFM-1b_artists.txt")
    top_artists = []

    # READ THE FILE WITH THE NAMES OF THE TOP ARTISTS
    for t in open(a_file):

        # FIND THE USED ID FOR THESE ARTISTS
        top_artists.append(t.rstrip('\n'))

    return top_artists


# read the created event file and load into pandas dataframe
def read_events(a_file):
    events = pd.read_csv(a_file, sep=",", names=['id', 'description', 'year', 'month', 'day', 'category'])
    return events


# Read artists file, returns a dictionary of {id:name}
def read_artists(a_file):
    artist_names = {}
    with open(a_file, 'r') as f:
        for line in f:
            content = line.strip().split('\t')
            if len(content) == 2:
                artist_names[np.int32(content[0])] = content[1]
            else:
                print('Problem encountered with ', content)
    return artist_names


# Read artists file, returns a dictionary of {name:id}
def read_artists_reversed(a_file):
    artist_names = {}
    with open(a_file, 'r') as f:
        for line in f:
            content = line.strip().split('\t')
            if len(content) == 2:
                 artist_names[content[1]] = np.int32(content[0])
            else:
                print('Problem encountered with ', content)
    return artist_names

# Read genres of each artist, returns a dic of {name:list_of_genres}
def read_artist_genre(a_file):
    artist_genre = {}
    with open(a_file, 'r') as f:
        for line in f:
            content = line.strip().split('\t')

            if len(content) > 1:
                artist_genre[content[0]] = list(map(int, content[1:]))

    return artist_genre

# Load a pandas dataframe that
def read_genre_id(a_file):
    genre_coding = pd.read_csv(a_file, sep="\t", header=None)
    return genre_coding

def load_country_id(a_file):
    country_id = pd.read_csv(a_file, sep="\t", index_col=0)

    return country_id

def create_object_list(time_series_dic, LOCATION_OBJECT_LIST):
    object_list = []

    # for every year
    for year, countries in time_series_dic.items():

        # for every country
        for country, genres in countries.items():

            # for every genre
            for genre_, week in genres.items():

                # for every week
                for w, playc in week.items():

                    event = {}
                    event['year'] = year
                    event['country'] = country
                    event['genre'] = genre_
                    event['week'] = w
                    event['playcount'] = playc
                    try:
                        event['relative_play'] = (
                        float(playc) / float(time_series_dic[year][country]['total_playcount'][w]))
                    except:
                        event['relative_play'] = 0

                    object_list.append(event
                                       )

    with open(LOCATION_OBJECT_LIST, 'w') as fp:
        json.dump(object_list, fp, sort_keys=True, indent=4)

def create_event_dic():

    # LOAD DATA
    artist_id = read_artists("data/time_series_analysis/LFM-1b_artists.txt")
    artist_genre = read_artist_genre("data/time_series_analysis/LFM-1b_artist_genres_allmusic.txt")
    genre_coding = read_genre_id("data/time_series_analysis/genres_allmusic.txt")
    country_id = load_country_id("data/time_series_analysis/country_ids_filter_itemLE_10000_userLE_1000.csv")

    files = ["2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014"]

    # VARIABLES
    time_series_dic = dict()
    error = 0

    #FUNCTION
    for file in files:
        print(file)
        print("\nStarted the year " + str(file) +  " : " + str(time.ctime()) + "\n")
        with open("../data/itemLE_10000_userLE_1000/y" + file + "-m-d-c-a-pc.csv", 'r') as f:
            next(f)

            for line in f:
                try:
                    x = line.strip().split('\t')
                    x = list(map(int, x))

                    # get variable names
                    year = x[0]
                    country_code = country_id.iloc[x[3]]['country']
                    genres = list(map(lambda x: genre_coding.iloc[x][0], artist_genre[artist_id[x[4]]][:1]))
                    weeknumber_event = (str(x[0]) + '-' + str(x[1]) + '-' + str(x[2]))

                    # Add year to dic
                    if year not in time_series_dic:
                        time_series_dic[int(year)] = dict()

                    # Add country to dic
                    if country_code not in time_series_dic[year]:
                        time_series_dic[year][country_code] = dict()

                    # Add genre to dic
                    for genre in genres:  # find list of genres
                        if genre not in time_series_dic[year][country_code]:
                            time_series_dic[year][country_code][genre] = dict()

                        if genre == 'total_playcount':
                            print('next line')
                            continue

                        # add week number of listening event
                        if weeknumber_event not in time_series_dic[year][country_code][genre]:
                            time_series_dic[year][country_code][genre][weeknumber_event] = 0

                        time_series_dic[year][country_code][genre][weeknumber_event] += x[5]

                        if 'total_playcount' not in time_series_dic[year][
                            country_code]:
                            time_series_dic[year][country_code]['total_playcount'] = dict()

                        if weeknumber_event not in \
                                time_series_dic[year][country_code]['total_playcount']:
                            time_series_dic[year][country_code]['total_playcount'][weeknumber_event] = 0

                        time_series_dic[year][country_code]['total_playcount'][weeknumber_event] += x[5]
                except:
                    error += 1

    print('Number of lines which could not be read: %s' % error)

    return time_series_dic


def time_series_analysis(LOCATION_OBJECT_LIST, SAVE_TIME_SERIES):
    needed_columns = ['date', 'country', 'genre', 'original', 'trend', 'seasonal', 'residual']

    with open(LOCATION_OBJECT_LIST) as data_file:
        data = json.load(data_file)

    # LOAD COUNTRY ID
    country_id = load_country_id("data/time_series_analysis/country_ids_filter_itemLE_10000_userLE_1000.csv")
    country_list = country_id['country'].tolist()
    genre_coding = read_genre_id("data/time_series_analysis/genres_allmusic.txt")
    genre_list = genre_coding[0].tolist()
    genre_list.remove("children's")

    # CREATE DATAFRAME AND ADD NEW COLUMNS FOR TIME SERIES ANALYSIS
    df = pd.DataFrame(data)
    df['week'] = pd.to_datetime(df['week'], format='%Y-%m-%d')
    df['date'] = df['week']
    df.set_index('week', inplace=True)
    df['trend'] = 0
    df['seasonal'] = 0
    df['residual'] = 0

    dic = {}

    for country in country_list[:5]:
        dic[country] = {}
        for genre in genre_list:
            dic[country][genre] = {}
            print(country, genre)
            ts_log = df[(df.country == country) & (df.genre == genre)].sort_index(axis=0).filter(
                items=['week', 'relative_play'])

            print(ts_log.head())

            F = df[(df.country == country) & (df.genre == genre)].sort_index(axis=0)
            decomposition = seasonal_decompose(ts_log.values, freq=10)
            trend = decomposition.trend
            seasonal = decomposition.seasonal
            residual = decomposition.resid

            dates = []
            for d in F['date'].tolist():
                dates.append((str(d.year) + "-" + str(d.month) + "-" + str(d.day)))

            try:
                temp = pd.DataFrame(
                    np.column_stack(
                        [dates, F['country'].tolist(), F['genre'].tolist(), ts_log, trend, seasonal, residual]),
                    columns=needed_columns)
                final = final.append(temp, ignore_index=True)
            except:
                final = pd.DataFrame(
                    np.column_stack(
                        [dates, F['country'].tolist(), F['genre'].tolist(), ts_log, trend, seasonal, residual]),
                    columns=needed_columns)

            plt.subplot(411)
            plt.plot(ts_log, label='Original')
            plt.legend(loc='best')
            plt.subplot(412)
            plt.plot(trend, label='Trend')
            plt.legend(loc='best')
            plt.subplot(413)
            plt.plot(seasonal, label='Seasonality')
            plt.legend(loc='best')
            plt.subplot(414)
            plt.plot(residual, label='Residuals')
            plt.legend(loc='best')
            plt.tight_layout()

            # plt.show()
            plt.close()

    x = final.to_json(orient='records')

    with open(SAVE_TIME_SERIES, 'w') as fp:
        json.dump(json.loads(x), fp, sort_keys=True, indent=4)


def time_series_analysis2(LOCATION_OBJECT_LIST, SAVE_TIME_SERIES):
    needed_columns = ['date', 'country', 'genre', 'original', 'trend', 'seasonal', 'residual']

    with open(LOCATION_OBJECT_LIST) as data_file:
        data = json.load(data_file)

    # LOAD COUNTRY ID
    country_id = load_country_id("data/time_series_analysis/country_ids_filter_itemLE_10000_userLE_1000.csv")
    country_list = country_id['country'].tolist()
    genre_coding = read_genre_id("data/time_series_analysis/genres_allmusic.txt")
    genre_list = genre_coding[0].tolist()
    genre_list.remove("children's")

    # CREATE DATAFRAME AND ADD NEW COLUMNS FOR TIME SERIES ANALYSIS
    df = pd.DataFrame(data)
    df['week'] = pd.to_datetime(df['week'], format='%Y-%m-%d')
    df['date'] = df['week']
    df.set_index('week', inplace=True)
    df['trend'] = 0
    df['seasonal'] = 0
    df['residual'] = 0

    dic = {}

    for country in country_list[:5]:
        dic[country] = {}
        for genre in ['total_playcount']:
            dic[country][genre] = {}
            print(country, genre)
            ts_log = df[(df.country == country) & (df.genre == genre)].sort_index(axis=0).filter(
                items=['week', 'playcount'])

            print(ts_log.head())

            F = df[(df.country == country) & (df.genre == genre)].sort_index(axis=0)
            decomposition = seasonal_decompose(ts_log.values, freq=10)
            trend = decomposition.trend
            seasonal = decomposition.seasonal
            residual = decomposition.resid

            dates = []
            for d in F['date'].tolist():
                dates.append((str(d.year) + "-" + str(d.month) + "-" + str(d.day)))

            try:
                temp = pd.DataFrame(
                    np.column_stack(
                        [dates, F['country'].tolist(), F['genre'].tolist(), ts_log, trend, seasonal, residual]),
                    columns=needed_columns)
                final = final.append(temp, ignore_index=True)
            except:
                final = pd.DataFrame(
                    np.column_stack(
                        [dates, F['country'].tolist(), F['genre'].tolist(), ts_log, trend, seasonal, residual]),
                    columns=needed_columns)

    x = final.to_json(orient='records')

    with open(SAVE_TIME_SERIES, 'w') as fp:
        json.dump(json.loads(x), fp, sort_keys=True, indent=4)