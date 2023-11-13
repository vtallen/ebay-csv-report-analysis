import csv
import pandas as pd
import os
import glob

# Scripts I have made
import costs
import itemManager

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

'''
#####################################################################################################################
Parameters: 
    reports_dir - The directory this function should look for .csv files to incorporate into the program's database 
    
    database_filename - The name of the file this function creates with the merged data

    database_dir - The directory the database csv should be stored in

Returns: 
    df - a dataframe of the merged database
#####################################################################################################################
'''
def update_csv_database(reports_dir='./ebay_reports/', database_filename='ebay.csv', database_dir='./'):
    report_files = glob.glob((reports_dir + '*.{}').format('csv')) # Load all csv files that are in the reports_dir 
    cached_reports_filename = 'cached_reports.txt' # This file stores the csv files that have alread been merged into the database csv
    cached_reports = []
    
    cached_reports_file_exists = False; # Flips to true if cached_reports.txt already exists so that the new reports can be appended 

    if os.path.isfile(reports_dir + cached_reports_filename):
        cached_reports_file_exists = True;
        
        # Read the names of all the csv files this program has already seen on past runs
        cached_reports_file = open(reports_dir + cached_reports_filename, 'r')
        cached_reports = [x.strip() for x in cached_reports_file.readlines()]
        cached_reports_file.close()
    else:
        # If the program has not seen any report files yet, it should create the cached_reports.txt file
        # then store the names of the new reports that are being ingested on this run
        cached_reports_file = open(reports_dir + cached_reports_filename, 'w')

        for file in report_files:
            cached_reports_file.write(file)
            cached_reports_file.write('\n')

        cached_reports_file.close()
    
    # Diff of all report files and the reports that have already been cached to get the reports we have not
    # seen yet
    new_reports = [file for file in report_files if file not in cached_reports]     
    
    if new_reports and cached_reports_file_exists: # If the file exist, and there are new reports 
                                                   # append the filenames to the cached_reports.txt file
        cached_reports_file = open(reports_dir + cached_reports_filename, 'a')
        for filename in new_reports:
            cached_reports_file.write(filename)
            cached_reports_file.write('\n')
    
    # Check if we have already created a database csv in the past, if not, create an empty dataframe
    if not os.path.isfile(database_dir + database_filename):
        df = pd.DataFrame()
    else:
        # load current database into memory
        df = pd.read_csv(database_dir + database_filename)
    
    # There are 11 metadata rows in ebay transaction reports as of 11/8/23
    new_reports_dfs = [pd.read_csv(file, skiprows=11) for file in new_reports] # load all of the new reports into memory
    
    # Merge all of the new reports into our main database
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
    
    # Sort the database by date
    df['Transaction creation date'] = pd.to_datetime(df['Transaction creation date'])
    df.sort_values(by='Transaction creation date', inplace=True)

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

'''
#####################################################################################################################
Class EbayCalc:
    Constructor Parameters:
    header - the header for the CSV file you are running reports on

#####################################################################################################################
'''
class EbayCalc:
    def __init__(self, header):
        self.subtotal_i = header.index('Item subtotal')
        self.shipping_i = header.index('Shipping and handling')
        self.final_fee_i = header.index('Final Value Fee - fixed')
        self.value_fee_i = header.index('Final Value Fee - variable')

        self.gross_profit = 0.0

    def get_gross_profit(self, row):
        try:
            order_pofit = float(row[self.subtotal_i]) + float(row[self.shipping_i])
            self.gross_profit += order_pofit
            return order_pofit
        except ValueError:
            print("get_order_profit: could not parse data on row")
    

if __name__ == "__main__":
    update_csv_database()
    
    infile = open('ebay.csv', 'r')
    incsv = csv.reader(infile, delimiter=",", quotechar='"')
    inheader = incsv.__next__()

    indataset = [row for row in incsv]
    
    ebay_calc = EbayCalc(inheader)
    item_mngr = itemManager.ItemManager(header=inheader)

    for row in indataset:
        ebay_calc.get_gross_profit(row)
        item_mngr.visit_row(row)

    costs_header, costs_dataset = costs.get_costs_dataset()
    sum_costs = costs.sum_costs(header=costs_header, dataset=costs_dataset)
    
    print('Gross Profit: ', ebay_calc.gross_profit)
    print('Net Profit: ', ebay_calc.gross_profit - sum_costs)
    
    for item in item_mngr.items:
        print(item)
    
    infile.close()


     
