import csv
import pandas as pd
import os
import glob
import datetime
import calendar
import operator

# Scripts I have made
import costs
import itemManager
'''
Purpose: 
    Reads in an ebay orders report, cleans up the file, then writes a file 

Parameters:
    filename: str
'''
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
'''
* ***************************************************************************************** *
*                                                                                           *
* Function name:    update_csv_database                                                     *
*                                                                                           *
* Description:      Loads all ebay transaction report csvs from a directory, puts them into *
*                   into their own pandas data frame, then merges the datafram, drops       * 
*                   duplicates, then dumps the new dataframe to a new csv file              *
*                                                                                           *
* Parameters:       str  reports_dir        :   The directory where the ebay csv reports are*
*                   str  database_filename  :   What the output csv should be called        *
*                   str  database_dir       :   Where the output csv should be stored       *
*                                                                                           *
* Return Value:     pandas dataframe        :   Contains the merged data from all csvs found*
*                                               in reports_dir                              *
*                                                                                           *
* ***************************************************************************************** *
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
   # TODO: Add eccept clauses
    try:
        # Remove data from the report we do not need
        df.drop(df.loc[df['Type'] == 'Payout'].index, inplace=True)
    except:
        print("No rows to drop with 'Type': 'Payout'")

    try:
        df.drop(df.loc[df['Type'] == 'Refund'].index, inplace=True)
    except:
        print("No rows to drop with 'Type': 'Refund'")

    try:
        df.drop(df.loc[df['Type'] == 'Shipping label'].index, inplace=True)
    except:
        print("No rows to drop with 'Type': 'Shipping label'")

    try:
        df.drop(df.loc[df['Type'] == 'Other fee'].index, inplace=True)
    except:
        print("No rows to drop with 'Type': 'Other fee'")

    # Sort the database by date
    df['Transaction creation date'] = pd.to_datetime(df['Transaction creation date'], format='mixed')
    df.sort_values(by='Transaction creation date', inplace=True) 

    df.to_csv(database_dir + database_filename, mode='w', index=False)

    return df
     
'''
* ***************************************************************************************** *
*                                                                                           *
* Class name:       EbayReport                                                              *
*                                                                                           *
* Description:      Contains all statistics about ebay transactions over a given time period*
*                   it memorizes all rows that are passed into it's visit_row function. Any *
*                   rows not within the start_date and end_date will be ignored             *
*                                                                                           *
* Parameters:      [str] header             : The header of the csv database                *
*                  str   name               : An identifier for when this report is printed *
*                  ItemManager item_man     : The class responsible for keeping track of    *
*                                             item costs and if an item should be counted   *
*                  datetime date start_date : The first date(inclusive) that should be      *
*                                             included in the report                        *
*                  datetime date end_date   : The last date(inclusive) that should be       *
*                                             included in the report                        *
*                                                                                           *
* ***************************************************************************************** *
'''
class EbayReport:
    def __init__(self, header, item_man, name, start_date, end_date):
        self.item_man = item_man

        self.name = name
        
        # Indexes of the needed data in a row
        self.date_i = header.index('Transaction creation date')
        self.subtotal_i = header.index('Item subtotal')
        self.item_name_i = header.index('Item title')
        self.shipping_i = header.index('Shipping and handling')
        self.final_fee_i = header.index('Final Value Fee - fixed')
        self.value_fee_i = header.index('Final Value Fee - variable')
        
        # Sumation variables
        self.num_orders = 0
        self.total_sales = 0.0
        self.gross_profit = 0.0
        self.item_costs = 0.0 
        self.shipping_costs = 0.0
        
        # Variables that will get the profit and cost of each order
        # added to it. This will allow the calculation of average 
        # profit margin
        self.order_profits = []
        self.order_costs = []
        
        if start_date == 'begin':
            self.start_date = datetime.date(1900, 1, 1)
        else:
            self.start_date = start_date 

        if end_date == 'end':
            self.end_date = datetime.datetime.now().date()
        else:
            self.end_date = end_date 
        
        # TODO May have added bug here
        self.first_date = datetime.datetime(1, 1, 1) 
        self.last_date = datetime.datetime(1, 1, 1) 
        
        # A dictionary containing each seen item and how many times
        # it was seen
        self.items = {}

    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    visit_row                                                               *
    *                                                                                           *
    * Description:      Memorizes the data in a row into the class and adds it to the statistics*
    *                   that are computed                                                       *
    *                                                                                           *
    * Parameters:       [str]  row  :   A row of data from the ebay CSV files                   *
    *                                                                                           *
    * Return Value:     none                                                                    *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def visit_row(self, row):
        self.item_man.update_valid_items()
        item_cost = item_mngr.get_cost(row[self.item_name_i], row[self.date_i])
        item_date = datetime.datetime.strptime(row[self.date_i], '%Y-%m-%d').date()

        # Statistics should only be calculated for a row if the item exists in the item manager,
        # and the date for the order is within the range start_date to end_date inclusive
        if (item_cost != 'ignore' and item_cost != '-1' and item_cost != -1) and item_date >= self.start_date and item_date <= self.end_date:
            if self.first_date == datetime.datetime(1, 1, 1): # Check if first_date is empty, if it is this is the first row we've seen
                self.first_date = item_date
                
            self.last_date = item_date
            
            # the type conversion from string to float here can fail if there is not data in the cell,
            # ocassionally ebay csvs don't have data in these rows for some reason.
            try:
                order_pofit = float(row[self.subtotal_i]) + float(row[self.final_fee_i]) + float(row[self.value_fee_i]) 
                self.total_sales += float(row[self.subtotal_i])

                self.shipping_costs += float(row[self.shipping_i])

                self.gross_profit += order_pofit
                self.order_profits.append(order_pofit)

                self.item_costs += float(item_cost)
                self.order_costs.append(float(item_cost))

                self.num_orders += 1
                
                # If the item has been seen before, increment the count of it,
                # otherwise create the entry
                if row[self.item_name_i] in self.items:
                    self.items[row[self.item_name_i]] += 1
                else:
                    self.items[row[self.item_name_i]] = 1

            except ValueError:
                print('Junk data, name=', row[self.item_name_i], ' - date=', row[self.date_i])
    
    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    get_net_profit                                                          *
    *                                                                                           *
    * Description:      returns the gross profit minus costs                                    *
    *                                                                                           *
    * Return Value:     float                                                                   *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def get_net_profit(self):
        return self.gross_profit - self.item_costs
    
    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    get_top_items                                                           *
    *                                                                                           *
    * Description:      returns a 2d array containing first the name of an item, followed by    *
    *                   how many times that item was seen by visit_row                          *
    *                                                                                           *
    * Return Value:     [[str, float]]                                                          *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def get_top_items(self):
        items_list = []
        for key in self.items.keys():
            items_list.append([key, self.items[key]])
        
        top_items = sorted(items_list, key=operator.itemgetter(1), reverse=True)

        return top_items
    
    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    get_avg_margin                                                          *
    *                                                                                           *
    * Description:      returns the average profit margin(in percent) of all items seen by      *
    *                   visit_row                                                               *
    *                                                                                           *
    * Return Value:     float                                                                   *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def get_avg_margin(self):
        sum = 0
        for i, profit in enumerate(self.order_profits):
            sum += (profit - self.order_costs[i]) / self.order_costs[i]

        try:
            return sum / len(self.order_profits)
        except:
            return 0.0

    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    print_report                                                            *
    *                                                                                           *
    * Description:      prints to the console a formatted version of the statistcs computed in  *
    *                   this report                                                             *
    *                                                                                           *
    * Return Value:     none                                                                    *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def print_report(self):
        print(self.name)
        print(self.start_date, '-', self.end_date)
        print('=================================================================')
        print('First and last days to receive orders:', self.first_date, '-', self.last_date) # type : ignore
        print('Number of orders:', self.num_orders)
        print('Final value sales:', round(self.total_sales, 2))
        print('Gross Profit: ', round(self.gross_profit, 2))
        print('Estimated Per Item Costs:', round(self.item_costs, 2))
        print('Net profit:', round(self.gross_profit - self.item_costs, 2))
        print('Average profit margin:', str(round(self.get_avg_margin() * 100)) + '%')
        print('Top 5 items:')
        for i, entry in enumerate(self.get_top_items()):
            print('\t', entry[0], '-', entry[1])
            if i >= 4:
                break

'''
* ***************************************************************************************** *
*                                                                                           *
* Class name:       StatsGen                                                                *
*                                                                                           *
* Description:      Orchestrates the generation of commonly needed report timeframes        *
*                   including: last week, last month, last quarter, last year, year to date *
*                   all time, and monthly reports for every month contained within the      *
*                   database                                                                *
*                                                                                           *
* Parameters:      [str]        header   : The header of the csv database                   *
*                  [[str]]      table    : The entire dataset to run the reports on         *
*                  ItemManager  item_man : The class responsible for keeping track of       *
*                                          item costs and if an item should be counted      *
*                                                                                           *
* ***************************************************************************************** *
'''
class StatsGen:
    def __init__(self, header, table, item_man):
        # If you have other sales not on ebay you would like to be added to the full profit calculation
        self.sales_offset = 0
        self.item_man = item_man
        
        self.header = header
        self.table = table

        self.full_report = EbayReport(header, self.item_man, 'All time', 'begin', 'end')
        
        # Ingest the entire report 
        for row in table:
            self.full_report.visit_row(row) 
        
        # Where all monthly reports will be stored so you can iterate on them
        self.monthly_reports = []
        
        # The range of dates contained within the whole dataset
        self.first_date = self.full_report.first_date
        self.last_date = self.full_report.last_date
        
        # Iterate through all months contained in the dataset, find the first and last
        # days, then create reports for those months
        tempdate = self.first_date 
        while tempdate < self.last_date: # pyright : ignore
            monthrange = calendar.monthrange(tempdate.year, tempdate.month) 

            start_date = datetime.datetime(tempdate.year, tempdate.month, 1).date()
            end_date = start_date + datetime.timedelta(monthrange[1] - 1)
            
            name = calendar.month_name[start_date.month] + ' ' + str(start_date.year)
            self.monthly_reports.append(EbayReport(self.header, self.item_man, name, start_date, end_date))

            tempdate = end_date + datetime.timedelta(1) 
        
        # Find the end dates for each relative time range
        date_week = datetime.datetime.now().date() - datetime.timedelta(7)
        date_month = datetime.datetime.now().date() - datetime.timedelta(31)
        date_quarter = datetime.datetime.now().date() - datetime.timedelta(90)
        date_year = datetime.datetime.now().date() - datetime.timedelta(365)

        self.week_report = EbayReport(self.header, self.item_man, 'Last 7 days', date_week, datetime.datetime.now().date())
        self.month_report = EbayReport(self.header, self.item_man, 'Last 31 days', date_month, datetime.datetime.now().date())
        self.quarter_report = EbayReport(self.header, self.item_man, 'Last 90 days', date_quarter, datetime.datetime.now().date())
        self.year_report = EbayReport(self.header, self.item_man, 'Last 365 days', date_year, datetime.datetime.now().date())
        
        self.ytd_report = EbayReport(self.header, self.item_man, 'Year to date', datetime.datetime(datetime.datetime.now().year, 1, 1).date(), datetime.datetime.now().date())

        # All relative reports in a list so they can be iterated on
        self.relative_reports = [self.week_report, self.month_report, self.quarter_report, self.year_report, self.ytd_report]

    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    run_monthly_reports                                                     *
    *                                                                                           *
    * Description:      Ingetsts all data in self.table into all of the monthly reports         *
    *                                                                                           *
    * Return Value:     none                                                                    *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def run_monthly_reports(self):
        for row in self.table:
            for report in self.monthly_reports:
                report.visit_row(row)

    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    print_monthly_reports                                                   *
    *                                                                                           *
    * Description:      Prints all the statistics contained within the monthly reports as well  *
    *                   as the percentage in change from the previous month (if exists)         *
    *                                                                                           *
    * Parameters:       int year    :   The year for which to print reports on                  *
    *                                                                                           *
    * Return Value:     none                                                                    *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def print_monthly_reports(self, year):
        # A function for finding the percent of change between 2 values
        def get_change(current, previous):
            if current == previous:
                return 0
            try:
                return ((current - previous) / previous) * 100.0
            except ZeroDivisionError:
                return float('inf') 

        for i, report in enumerate(self.monthly_reports):
            if (report.end_date.year == year):
                report.print_report() 
                if i > 0:
                    prev = self.monthly_reports[i - 1]
                    print('Percent change from last month:')
                    print('\tNumber of orders:', str(round(get_change(report.num_orders, prev.num_orders),2)) + '%')
                    print('\tFinal Value Sales:', str(round(get_change(report.total_sales, prev.total_sales),2)) + '%')
                    print('\tGross Profit:', str(round(get_change(report.gross_profit, prev.gross_profit), 2)) + '%')
                    print('\tNet profit:', str(round(get_change(report.get_net_profit(), prev.get_net_profit()),2)) + '%')
                print()
    
    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    run_relative_reports                                                    *
    *                                                                                           *
    * Description:      Ingetsts all data in self.table into all of the relative reports        *
    *                                                                                           *
    * Return Value:     none                                                                    *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def run_relative_reports(self):
        for row in self.table:
            self.item_man.visit_row(row)
            for report in self.relative_reports:
                report.visit_row(row)

    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    set_sales_offset                                                        *
    *                                                                                           *
    * Description:      Sets the amount to offset the total profit calculations. Useful if you  *
    *                   have sales on other platforms you want to count in the full calculation *
    *                                                                                           *
    * Parameters:       float amt   : Amount to offset by                                       *
    *                                                                                           *
    * Return Value:     none                                                                    *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def set_sales_offset(self, amt):
        self.sales_offset = amt

    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    print_relative_reports                                                  *
    *                                                                                           *
    * Description:      prints all of the relative reports to the console                       *
    *                                                                                           *
    * Return Value:     none                                                                    *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def print_relative_reports(self):
        for report in self.relative_reports:
            report.print_report()
            print()

        costs_header, costs_dataset = costs.get_costs_dataset()
        sum_costs = costs.sum_costs(header=costs_header, dataset=costs_dataset)

        print('Summary of all orders')
        print(self.full_report.first_date, '-', self.full_report.last_date) # type : ignore
        print('=================================================================')
        print('Gross Profit: ', self.full_report.gross_profit)
        print('non-ebay sales:', self.sales_offset)
        print('Estimated Per Item Costs:', self.full_report.item_costs)
        print('Estimated net profit:', self.full_report.gross_profit - self.full_report.item_costs)
        print()
        print('Materials Costs:', sum_costs)
        print('Total profit minus all costs: ', self.full_report.gross_profit + self.sales_offset - sum_costs)
        print()

        print('Top Items:')
        top_items = self.full_report.get_top_items()
        for entry in top_items:
            print('\t', entry[0], '-', entry[1])

    def dump_reports(self, path, precision):
        pass

if __name__ == "__main__":
    # TODO: fix a bug where if you drop in a new report, it cannot be merged because
    # update_csv_database sorts the dataframe by date and ebay.csv's dates are in a different format
    '''
    then if flag -i is set it will kick into interactive mode 
    
    Also want to save statistics to a text file each run.
    
    '''
    update_csv_database()
    
    infile = open('ebay.csv', 'r')
    incsv = csv.reader(infile, delimiter=",", quotechar='"')
    inheader = incsv.__next__()

    item_mngr = itemManager.ItemManager(header=inheader)
    indataset = [row for row in incsv]
    
    stats = StatsGen(inheader, indataset, item_mngr)
    stats.set_sales_offset(554 + 492.34 + 1196 + 1065)

    print('MONTHLY REPORTS(This year):')
    print('======================================================================')
    stats.run_monthly_reports()
    stats.print_monthly_reports(datetime.datetime.now().year)

    stats.run_relative_reports()
    print('RELATIVE REPORTS:')
    print('======================================================================')
    stats.print_relative_reports()
    

    infile.close()
