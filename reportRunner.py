import csv
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

def update_csv_database(reports_dir='./ebay_reports/', database_filename='ebay.csv', database_dir='./'):
    report_files = glob.glob((reports_dir + '*.{}').format('csv')) # Load all csv files that are in the reports_dir 
    cached_reports_filename = 'cached_reports.txt'
    cached_reports = []
    
    cached_reports_file_exists = False; # Flips to true if cached_reports.txt already exists so that the new reports can be appended 

    if os.path.isfile(reports_dir + cached_reports_filename):
        cached_reports_file_exists = True;
        
        cached_reports_file = open(reports_dir + cached_reports_filename, 'r')
        cached_reports = [x.strip() for x in cached_reports_file.readlines()]
        cached_reports_file.close()
    else:
        cached_reports_file = open(reports_dir + cached_reports_filename, 'w')

        for file in report_files:
            cached_reports_file.write(file)
            cached_reports_file.write('\n')

        cached_reports_file.close()
    
    # Diff of all report files and the reports that have already been cached 
    new_reports = [file for file in report_files if file not in cached_reports]     

    if new_reports and cached_reports_file_exists: # If the file exist, and there are new reports 
                                                   # append the filenames to the cached_reports.txt file
        cached_reports_file = open(reports_dir + cached_reports_filename, 'a')
        for filename in new_reports:
            cached_reports_file.write(filename)
            cached_reports_file.write('\n')
    
    if not os.path.isfile(database_dir + database_filename):
        df = pd.DataFrame()
    else:
        # load current database into memory
        df = pd.read_csv(database_dir + database_filename)
    
    # There are 11 metadata rows in ebay transaction reports as of 11/8/23
    new_reports_dfs = [pd.read_csv(file, skiprows=11) for file in new_reports] # load all of the new reports into memory

    for new_df in new_reports_dfs:
        df = df._append(new_df)

    # Remove any accidental duplicate entries based on the order numbers
    df.drop_duplicates(subset='Order number', keep='first', inplace=True)     
   
    try:
        # Remove data from the report we do not need
        df.drop(df.loc[df['Type'] == 'Payout'].index, inplace=True)
        df.drop(df.loc[df['Type'] == 'Refund'].index, inplace=True)

    except:
        print("No rows to drop with 'Type': 'Payout' or 'Refund'")

    df.to_csv(database_dir + database_filename, mode='w', index=False)

    return df
     
    
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

class EbayCalc:
    def __init__(self, header):
        self.subtotal_i = header.index('Item subtotal')
        self.shipping_i = header.index('Shipping and handling')
        self.final_fee_i = header.index('Final Value Fee - fixed')
        self.value_fee_i = header.index('Final Value Fee - variable')

        self.gross_profit = 0.0

    def get_gross_profit(self, row):
        try:
            order_pofit = float(row[self.subtotal_i]) - float(row[self.shipping_i]) - float(row[self.final_fee_i]) - float(row[self.value_fee_i])
            self.gross_profit += order_pofit
            return order_pofit
        except ValueError:
            print("get_order_profit: could not parse data on row")


if __name__ == "__main__":
    '''
    Make the create csv database more general so it can be used for both order reports and transaction reports

    Need a way to pull in ebay fee amount from the transaction reports file so I dont have to calculate it myself

    Idea: Match rows based on the order number, then fill in the missiing data in ebay.csv 

    I could also do it by maintaining 2 csv databses and pulling from both when I need data, this may be easier
    to modify in the future if I want to derive more data
    '''
    update_csv_database()
    
    infile = open('ebay.csv', 'r')
    incsv = csv.reader(infile, delimiter=",", quotechar='"')
    inheader = incsv.__next__()

    indataset = [row for row in incsv]
    
    ebay_calc = EbayCalc(inheader)
    
    for row in indataset:
        print(ebay_calc.get_gross_profit(row))
    
    print(ebay_calc.gross_profit)
    infile.close()


     
