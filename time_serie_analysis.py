import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import collections

# PARAMETERS
DISPLAY = 'rel'
YEAR = '2005'
COLORS = ['black','gray','rosybrown','red','sienna','bisque','gold','olivedrab','darkgreen','mediumspringgreen','lightseagreen','paleturquoise','darkcyan','deepskyblue','royalblue','navy','blue','plum','m','deeppink','crimson']
COUNTRIES = ['US', 'UK', 'RU', 'DE', 'FI', 'SE', 'NL', 'AU']

# read the created event file and load into pandas dataframe
def read_events(a_file):
    events = pd.read_csv(a_file, sep=",", names=['id','description','year','month','day','category'])
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

# Read genres of each artist, returns a dic of {name:list_of_genres}
def read_artist_genre(a_file):
    artist_genre = {}
    with open(a_file, 'r') as f:
        for line in f:
            content = line.strip().split('\t')

            if len(content) >1:
                artist_genre[content[0]] = list(map(int,content[1:]))

    return artist_genre

# Load a pandas dataframe that
def read_genre_id(a_file):
    genre_coding = pd.read_csv(a_file, sep="\t", header=None)
    return genre_coding

def load_country_id(a_file):
    country_id = pd.read_csv(a_file, sep="\t",index_col=0)

    return country_id

# LOAD DATA
events = read_events('data/events.csv')
artist_id = read_artists("data/time_series_analysis/LFM-1b_artists.txt")
artist_genre = read_artist_genre("data/time_series_analysis/LFM-1b_artist_genres_allmusic.txt")
genre_coding = read_genre_id("data/time_series_analysis/genres_allmusic.txt")
country_id = load_country_id("data/time_series_analysis/country_ids_filter_itemLE_10000_userLE_1000.csv")

genre_list = genre_coding[0].tolist()

time_series_dic = {}

error=0

with open("data/time_series_analysis/y2005-m-d-c-a-pc.csv", 'r') as f:
    next(f)

    for line in f:
        try:
            x = line.strip().split('\t')
            x = list(map(int, x))

            # get variable names
            country_code = country_id.iloc[x[3]]['country']
            genres = list(map(lambda x: genre_coding.iloc[x][0], artist_genre[artist_id[x[4]]]))
            weeknumber_event = datetime.date(x[0], x[1], x[2]).isocalendar()[1]

            # Add country to dic

            if country_code not in time_series_dic:
                time_series_dic[country_code] = {}

            # add genre
            for genre in genres: # find list of genres
                if genre not in time_series_dic[country_code]:
                    time_series_dic[country_code][genre] = {}

                # add week number of listening event
                if weeknumber_event not in time_series_dic[country_code][genre]:
                    time_series_dic[country_code][genre][weeknumber_event] = 0

                time_series_dic[country_code][genre][weeknumber_event] += x[5]

        except:
            error+=1


print('Number of lines which could not be read: %s' % (error))
print(time_series_dic)

events_filtered = events[(events['year'] == int(YEAR))]
weeks_of_events = []
names_of_events = []
for index, row in events_filtered.iterrows():
    weeknumber_event = datetime.date(row['year'], row['month'], row['day']).isocalendar()[1]
    weeks_of_events.append(weeknumber_event)
    names_of_events.append(row['description'])

print(names_of_events)
for COUNTRY_OF_INTEREST in COUNTRIES:
    # Total playcount
    total_playcount ={}
    for gen in genre_list:
        try:
            for week, playcount in time_series_dic[COUNTRY_OF_INTEREST][gen].items():
                if week not in total_playcount:
                    total_playcount[week] = playcount
                else:
                    total_playcount[week] += playcount
        except:
            print('genre %s for %s resulted in an error' % (gen, COUNTRY_OF_INTEREST))

    total_sorted = dict(collections.OrderedDict(sorted(total_playcount.items())))

    n = 0
    for gen in genre_list:
        try:
            data = dict(collections.OrderedDict(sorted(time_series_dic[COUNTRY_OF_INTEREST][gen].items())))
            if DISPLAY == 'rel':
                plt.plot(list(data.keys()), [spec / total for spec, total in zip(list(data.values()), total_sorted.values())], label=gen, c=COLORS[n])

            else:
                DISPLAY = 'abs'
                plt.plot(list(data.keys()), list(data.values()), label=gen, c=COLORS[n])

            n += 1
        except:
            print('genre %s for %s resulted in an error' % (gen, COUNTRY_OF_INTEREST))

    m=0
    for e in weeks_of_events:
        plt.axvline(x=e)
        plt.text((e+0.1), 0.2, names_of_events[m], rotation=90, fontsize=4)
        m+=1

    plt.title('Popularity evolution for ' + COUNTRY_OF_INTEREST + ' in ' + YEAR + '(Total playcounts: ' + str(sum(total_sorted.values())) +')')
    plt.xlabel('Week', fontsize=12)
    plt.ylabel('Playcount (' + DISPLAY + ')', fontsize=12)
    plt.grid(True)
    lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., fontsize=6)
    plt.savefig('data/' + COUNTRY_OF_INTEREST + '_' + YEAR + '_' + DISPLAY +'.png', dpi=400, bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.close()