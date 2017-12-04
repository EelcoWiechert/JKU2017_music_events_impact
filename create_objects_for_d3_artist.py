from create_objects_for_d3 import *

def create_event_dic_artists():

    # LOAD DATA
    artist_id = read_artists("../data/LFM-1b_artists.txt")
    country_id = load_country_id("../data/country_ids_filter_itemLE_10000_userLE_1000.csv")

    # VARIABLES
    time_series_dic = dict()
    error = 0

    files = ["2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014"]

    # READ THE FILES AS CREATED BY MARKUS LINE BY LINE
    for file in files:
        print(file)
        print("\nStarted the year " + str(file) +  " : " + str(time.ctime()) + "\n")
        with open("../data/itemLE_10000_userLE_1000/y" + file + "-m-d-c-a-pc.csv", 'r') as f:
            next(f)

            for line in f:
                try:
                    x = line.strip().split('\t')
                    x = list(map(int, x))

                    # SAVE THE INFORMATION FROM THE FILE PER LINE INTO VARIABLES
                    year = x[0]
                    country_code = country_id.iloc[x[3]]['country']
                    artist = artist_id[x[4]]
                    date_event = (str(x[0]) + '-' + str(x[1]) + '-' + str(x[2]))

                    # AS WE ARE ONLY INTERESTED IN A COUPLE OF ARTISTS (TOP 20), SKIP THE OTERS
                    if x[4] not in {1602, 54, 761458, 320, 153, 55, 4115, 2966994, 27, 470, 283, 16, 137, 140, 245, 99, 2893933, 135, 402, 1648, 172}:
                        continue

                    # CREATE A DICTIONARY {year:{country:{artist:{date}}}}

                    # Add year to dic
                    if year not in time_series_dic:
                        time_series_dic[int(year)] = dict()

                    # Add country to dic
                    if country_code not in time_series_dic[year]:
                        time_series_dic[year][country_code] = dict()

                    # Add artist to dic
                    if artist not in time_series_dic[year][country_code]:
                        time_series_dic[year][country_code][artist] = dict()

                    # add week number of listening event
                    if date_event not in time_series_dic[year][country_code][artist]:
                        time_series_dic[year][country_code][artist][date_event] = 0

                    time_series_dic[year][country_code][artist][date_event] += x[5]

                    # CALCULATE THE TOTAL NUMBER OF SONGS PLAYED IN ORDER TO CALCULATE
                    # THE RELATIVE NUMBER OF SONGS PLAYED

                    if 'total_playcount' not in time_series_dic[year][country_code]:
                        time_series_dic[year][country_code]['total_playcount'] = dict()

                    if date_event not in time_series_dic[year][country_code]['total_playcount']:
                        time_series_dic[year][country_code]['total_playcount'][date_event] = 0

                    time_series_dic[year][country_code]['total_playcount'][date_event] += x[5]

                except:
                    error += 1

    print('Number of lines which could not be read: %s' % (error))

    return time_series_dic

def create_object_list_artists(time_series_dic, LOCATION_OBJECT_LIST_ARTISTS):
    object_list = []

    # for every year
    for year, countries in time_series_dic.items():

        # for every country
        for country, artists in countries.items():

            # for every genre
            for art, date in artists.items():

                if art == 'total_playcount':
                    continue

                # for every week
                for d, playc in date.items():

                    event = {}
                    event['year'] = year
                    event['country'] = country
                    event['artist'] = art
                    event['week'] = d
                    event['playcount'] = playc
                    try:
                        event['relative_play'] = (
                        float(playc) / float(time_series_dic[year][country]['total_playcount'][d]))
                    except:
                        event['relative_play'] = 0

                    object_list.append(event
                                       )

    with open(LOCATION_OBJECT_LIST_ARTISTS, 'w') as fp:
        json.dump(object_list, fp, sort_keys=True, indent=4)

def time_series_analysis_artist(LOCATION_OBJECT_LIST, SAVE_TIME_SERIES):
    needed_columns = ['date', 'country', 'artist', 'original', 'trend', 'seasonal', 'residual']

    with open(LOCATION_OBJECT_LIST) as data_file:
        data = json.load(data_file)

    # LOAD COUNTRY ID
    country_id = load_country_id("../data/country_ids_filter_itemLE_10000_userLE_1000.csv")
    country_list = country_id['country'].tolist()
    artist_list = read_top_artists('../data/top_artists.txt')

    #artist_list = ["Michael Jackson"]

    # CREATE DATAFRAME AND ADD NEW COLUMNS FOR TIME SERIES ANALYSIS
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['week'], format='%Y-%m-%d')
    df.set_index('date', inplace=True)
    df['trend'] = 0
    df['seasonal'] = 0
    df['residual'] = 0

    dic = {}

    for country in country_list[:1]: # ONLY THE COUNTRY WITH THE MOST PLAYCOUNTS
        dic[country] = {}
        for artist in artist_list:
            dic[country][artist] = {}
            print(country, artist)
            ts = df[(df.country == country) & (df.artist == artist)].sort_index(axis=0).filter(
                items=['date', 'relative_play'])



            F = df[(df.country == country) & (df.artist == artist)].sort_index(axis=0)

            print('')
            print('---------------------------------------------')
            print('')
            print(F.head())
            print('')
            print('---------------------------------------------')
            print('')

            decomposition = seasonal_decompose(ts.values, freq=10)

            trend = decomposition.trend
            seasonal = decomposition.seasonal
            residual = decomposition.resid

            dates = []
            for d in F.index.tolist():
                dates.append((str(d.year) + "-" + str(d.month) + "-" + str(d.day)))

            try:
                temp = pd.DataFrame(
                    np.column_stack(
                        [dates, F['country'].tolist(), F['artist'].tolist(), ts, trend, seasonal, residual]),
                    columns=needed_columns)
                final = final.append(temp, ignore_index=True)
            except:
                final = pd.DataFrame(
                    np.column_stack(
                        [dates, F['country'].tolist(), F['artist'].tolist(), ts, trend, seasonal, residual]),
                    columns=needed_columns)

    x = final.to_json(orient='records')

    with open(SAVE_TIME_SERIES, 'w') as fp:
        json.dump(json.loads(x), fp, sort_keys=True, indent=4)