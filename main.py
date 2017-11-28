from create_objects_for_d3 import *
from create_objects_for_d3_artist import *

# MAKE OBJECT LIST
OBJECT_LIST = 0
# 0 = on genre
# 1 = on artists

CREATE_OBJECT_LIST = False
TIME_SERIES = True
LOCATION_OBJECT_LIST = "../data/allCountries_relativePlaycount_Genre.json"
LOCATION_OBJECT_LIST_ARTISTS = "../data/data_rel_playcount_artist.json"
SAVE_TIME_SERIES = "../data/time_series_analysis_artist2.json"

# START SCRIPT

if CREATE_OBJECT_LIST:

    if OBJECT_LIST == 0:

        # THIS FUNCTION CREATES A DICTIONARY => YEAR, COUNTRY, GENRE, WEEK
        time_series_dic = create_event_dic()

        # CREATE OBJECT LIST
        create_object_list(time_series_dic, LOCATION_OBJECT_LIST)

    if OBJECT_LIST == 1:

        # THIS FUNCTION CREATES A DICTIONARY => YEAR, COUNTRY, ARTIST, WEEK
        time_series_dic = create_event_dic_artists()

        # CREATE OBJECT LIST
        create_object_list_artists(time_series_dic, LOCATION_OBJECT_LIST_ARTISTS)


# IF TRUE, TIME SERIE ANALYSIS WILL BE ADDED TO THE OBJECT LIST
if TIME_SERIES:

    if OBJECT_LIST == 0:

        time_series_analysis2(LOCATION_OBJECT_LIST, SAVE_TIME_SERIES)

    if OBJECT_LIST == 1:
        time_series_analysis_artist(LOCATION_OBJECT_LIST_ARTISTS, SAVE_TIME_SERIES)

exit()












"""

# PARAMETERS
DISPLAY = 'rel'
YEAR = '2005'
COLORS = ['black','gray','rosybrown','red','sienna','bisque','gold','olivedrab','darkgreen','mediumspringgreen','lightseagreen','paleturquoise','darkcyan','deepskyblue','royalblue','navy','blue','plum','m','deeppink','crimson']
COUNTRIES = ['US', 'UK', 'RU', 'DE', 'FI', 'SE', 'NL', 'AU']

events = read_events('data/events.csv')
events_filtered = events[(events['year'] == int(YEAR))]
weeks_of_events = []
names_of_events = []
for index, row in events_filtered.iterrows():
    weeknumber_event = datetime.date(row['year'], row['month'], row['day']).isocalendar()[1]
    weeks_of_events.append(weeknumber_event)
    names_of_events.append(row['description'])

for COUNTRY_OF_INTEREST in COUNTRIES:
    # Total playcount
    total_playcount ={}
    for gen in genre_list:
        try:
            for week, playcount in time_series_dic[int(YEAR)][COUNTRY_OF_INTEREST][gen].items():
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
    plt.xlabel('Week', fontsize=8)
    plt.ylabel('Playcount (' + DISPLAY + ')', fontsize=8)
    plt.grid(True)
    lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., fontsize=6)
    plt.savefig('data/' + COUNTRY_OF_INTEREST + '_' + YEAR + '_' + DISPLAY +'.png', dpi=400, bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.close()

"""