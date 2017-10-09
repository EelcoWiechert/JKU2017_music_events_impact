import csv

def write_event(PATH,line):
    with open(PATH, "a") as csv_file:
            writer = csv.writer(csv_file, delimiter=',', dialect='excel')
            writer.writerow(line)