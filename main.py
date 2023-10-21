import csv
from os.path import isfile
import sys
import pandas as pd
import os
import glob

'''
Purpose: 
    Reads in an ebay orders report, cleans up the file, then writes a file 

Parameters:
    filename: str
'''
def clean_ebay_report(filename, overwrite=False):
    with open(filename, 'rb') as file:
    # Read the file content and decode it while removing the BOM
        file_bits = file.read().decode('utf-8-sig')
    
    file_lines = file_bits.splitlines();
    
    file_lines.pop(0) # Remove the first blank line of the file
    file_lines.pop(1) # Remove the blank row after the headers
    file_lines.pop(-1) # Remove the stats line at the end of the file
    file_lines.pop(-1) # Remove the seller id from the end of the file
    file_lines.pop(-1) # Remove the blank line at the end of the file 
    
    if filename.endswith('.csv') and not overwrite:
        filename = filename[:-4]
        filename += '_clean.csv'

    with (open(filename, 'w')) as file:
        for line in file_lines:
            file.write(line + '\n')

def create_csv_database(reports_dir='./ebay_reports/', database_dir='./'):
    
    
    report_files = glob.glob((reports_dir + '*.{}').format('csv')) # Load all csv files that are in the reports_dir 
    cached_reports = []

    if os.path.isfile('./ebay_reports/read_files.txt'):
        print("IS FILE")
        past_imported_reports_file = open('./ebay_reports/read_files.txt', 'r')
        cached_reports = [x.strip() for x in past_imported_reports_file.readlines()]
        past_imported_reports_file.close()
    else:
        past_imported_reports_file = open(reports_dir + "read_files.txt", 'w')

        for file in report_files:
            past_imported_reports_file.write(file)
            past_imported_reports_file.write('\n');

        past_imported_reports_file.close()
    
    new_reports = [file for file in report_files if file not in cached_reports] # Diff of all report files and the reports that have already been cached 
     
    
'''
Parameters:
    data_frame: pandas data frame

Returns:
    A dictionary in the following format, containing all states + cities,
    as well as how many orders were sent to each city

    {
        "NY":{
            "TOTAL":15
            "Brooklyn":10
            "New York":5
        }
    }
'''
def get_location_stats(data_frame):
    location_dict = {} 

    for index, row in data_frame.iterrows():
        state = row['Buyer State']
        city = row['Buyer City']

        if state in location_dict:
            location_dict[state]["TOTAL"] += 1

            if city in location_dict[state]:
                location_dict[state][city] += 1 
            else:
                location_dict[state][city] = 1

        else:
            location_dict[state] = {
                    "TOTAL":1,
                    city:1
                    }

    return location_dict


def get_top_state(location_stats_dict):
    top_state = ''
    top_state_count = 0

    for key in location_stats_dict.keys():
        if location_stats_dict[key]["TOTAL"] > top_state_count:
            top_state = key
            top_state_count = location_stats_dict[key]["TOTAL"]
    
    return top_state

def get_top_city(location_stats_dict):
    top_city = ''
    top_city_state = ''
    top_city_count = 0

    for state in location_stats_dict.keys():
        for city in location_stats_dict[state].keys():
            if city == "TOTAL":
                continue
            
            if location_stats_dict[state][city] > top_city_count:
                top_city = city
                top_city_state = state
                top_city_count = location_stats_dict[state][city]
    
    return [top_city_state, top_city]

if __name__ == "__main__":
    '''
    PLAN:
        keep a cache of which reports have been loaded into the csv database
        On program start, check if there are any new reports, load them and append to the master csv, then drop duplicate rows
    '''
    #clean_ebay_report('ebay.csv')
    create_csv_database()


     
