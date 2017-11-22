
'''

This script is used to make a list of object,
where each object comprises a date and the number of unique users on that day

'''

import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

file = json.load(open('../data/unique_users_per_day.json'))

df = pd.DataFrame(file)

df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

print(df.head())

df.plot(x='date', y='number_of_unqiue_listeners')

plt.xlim([datetime.datetime(2005,1,1),datetime.datetime(2014,12,31)])
plt.title('From 1-1-2005 to 31-12-2014')
plt.suptitle('Number of unique users per day')

plt.savefig('unique_users_per_day_LFM.png', dpi=300)

CREATE_LIST = False   # Set to true if you would like to create an object list
CREATE_PLOT = True      # Set to true if you would like to plot the object list

print('start script')

# DEFINE VARIABLES
LOCATION_LFM_LE_FILE = '../data/LFM-1b/LFM-1b_LEs.txt' # Location of listening event file
LOCATION_OBJECT_LIST = '../data/unique_users_per_day.json' # where to place the new json file that contains the number of users
users_per_day = dict() # temp dic
users_per_day_final = dict() # temp dic
event_list = [] # object list

if CREATE_LIST:

    # OPEN THE LISTENING EVENT FILE AND SET LINE COUNTER TO 0
    n = 0
    print('create objects')
    print(datetime.now())
    with open(LOCATION_LFM_LE_FILE) as f:
        for line in f:
            n+=1

            # PRINT PROGRESS
            if n % 1000000 == 0:
                print(round(n/1088161692, 4))

            # CONVERT TIMESTAMP TO YYYY-MM-DD
            date_raw = datetime.fromtimestamp(int(line.split()[4]))
            date = str(date_raw.year) + '-' + str(date_raw.month) + '-' + str(date_raw.day)

            # WHEN WE ENCOUNTER THE DATE FOR THE FIRST TIME, ADD TO DIC
            if date not in users_per_day:
                users_per_day[date] = []

            # ADD THE DATE AS KEY, {USER_1 : ''} AS VALUE
            # THIS WAY DOUBLE USERS ARE OVERWRITTEN
            users_per_day[date].append(int(line.split()[0]))

    print('Creating objects')
    print(datetime.now())
    n = 0

    for date, users in users_per_day.items():
        n+=1
        print(date)

        if n % 100 == 0:
            print(n)

        # ONLY GET THE UNIQUE IDS IN LIST
        usersUnique = list(set(users))

        # CREATE AN OBJECT
        x = {'date': date, 'number_of_unqiue_listeners': len(usersUnique)}

        # ADD OBJECT TO LIST
        event_list.append(x)

    with open(LOCATION_OBJECT_LIST, 'w') as fp:
        json.dump(event_list, fp, sort_keys=True, indent=4)

if CREATE_PLOT:

    file = json.load(open(LOCATION_OBJECT_LIST))

    df = pd.DataFrame(file)

    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

    df.plot(x='date', y='number_of_unqiue_listeners')

    plt.xlim([datetime.datetime(2005, 1, 1), datetime.datetime(2014, 12, 31)])
    plt.title('From 1-1-2005 to 31-12-2014')
    plt.suptitle('Number of unique users per day')

    plt.savefig('../data/unique_users_per_day_LFM.png', dpi=300)

