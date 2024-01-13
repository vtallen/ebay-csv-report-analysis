import csv
import os
from os import system, name
import datetime 

def clear():
 
    # for windows
    if name == 'nt':
        _ = system('cls')
 
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')

'''
* ***************************************************************************************** *
*                                                                                           *
* Class name:       ItemManager                                                             *
*                                                                                           *
* Description:      Manages the lookup of the cost of specific ebay items. It stores the    *
*                   name of an item, how much that item costs to make, and the Effective    *
*                   date range for that price in a CSV file. It then allows other classes   *
*                   to retreive that data in order to do calculations                       *
*                                                                                           *
* Parameters:      [str] header               : The header of the csv database              *
*                  str   csv_dir              : The directory to put the csv into           *
*                  str   lookup_table_filename: name for the item cost csv file             *
*                  str   alias_table_filename : name for the alias csv file                 *
*                                                                                           *
* ***************************************************************************************** *
'''
class ItemManager:
    def __init__(self, header, csv_dir='./', lookup_table_filename='item_lookup_table.csv', alias_table_filename='item_alias_table.csv'):
        self.csv_dir = csv_dir
        self.lookup_table_filename = lookup_table_filename
        self.alias_table_filename = alias_table_filename

        self.item_name_i = header.index('Item title')
        
        # Where the items visit_row has seen will go
        self.items = set()
        
        # Variables for storing the alias table. This allows multiple item names to 
        # point to the same cost entry in the lookup table
        self.alias_table_header = ['Item','Alias']
        self.alias_table_item_i = self.alias_table_header.index('Item')
        self.alias_table_alias_i = self.alias_table_header.index('Alias')
        self.alias_table = []
        
        # Variables for the lookup table where item names will be associated
        # with their costs and date ranges
        self.lookup_table_header = ['Item','Cost','Start Date', 'End Date']
        self.lookup_table_item_i = self.lookup_table_header.index('Item')
        self.lookup_table_cost_i = self.lookup_table_header.index('Cost')
        self.lookup_table_startdate_i = self.lookup_table_header.index('Start Date')
        self.lookup_table_enddate_i = self.lookup_table_header.index('End Date')
        self.lookup_table = []

        self.load_tables()
        
        # Valid items are the items within the lookup table either with a price, or which are to be ignored
        self.valid_items = []

        # New items are items yet to be added to the lookup table. This allows the define costs function
        # to see which items need costs added to them
        self.new_items = []

    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    load_lookuptable                                                        *
    *                                                                                           *
    * Description:      loads the lookup table csv into memory                                  *
    *                                                                                           *
    * Return Value:     none                                                                    *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def load_lookuptable(self):
        if os.path.isfile(self.csv_dir + self.lookup_table_filename):
            infile = open(self.csv_dir + self.lookup_table_filename, 'r')
            incsv = csv.reader(infile, delimiter=',', quotechar='"')

            self.lookup_table_header = incsv.__next__()
            self.lookup_table = [row for row in incsv]
            infile.close()

        else:
            outfile = open(self.csv_dir + self.lookup_table_filename, 'w')
            outfile.close()

   
    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    load_alias_table                                                        *
    *                                                                                           *
    * Description:      loads the alias table csv into memory                                   *
    *                                                                                           *
    * Return Value:     none                                                                    *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def load_alias_table(self):
        if os.path.isfile(self.csv_dir + self.alias_table_filename):
            infile = open(self.csv_dir + self.alias_table_filename, 'r')
            incsv = csv.reader(infile, delimiter=',', quotechar='"')

            self.alias_table_header= incsv.__next__()
            self.alias_table = [row for row in incsv]
            infile.close()
        else:
            outfile = open(self.csv_dir + self.alias_table_filename, 'w')
            outfile.close()

    
    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    load_tables                                                             *
    *                                                                                           *
    * Description:      loads both the alias table and lookup table csvs into memory            *
    *                                                                                           *
    * Return Value:     none                                                                    *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def load_tables(self):
        self.load_lookuptable()
        self.load_alias_table()
    
    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    write_lookup_table                                                      *
    *                                                                                           *
    * Description:      writes out the lookup table to a file at directory self.csv_dir and     *
    *                   filename self.lookup_table_filename                                     *
    *                                                                                           *
    * Return Value:     none                                                                    *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def write_lookup_table(self):
        outfile = open(self.csv_dir + self.lookup_table_filename, 'w')
        outcsv = csv.writer(outfile, delimiter=',', quotechar='"')
        outcsv.writerow(self.lookup_table_header)
        outcsv.writerows(self.lookup_table)
        outfile.close()

    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    write_alias_table                                                       *
    *                                                                                           *
    * Description:      writes out the alias table to a file at directory self.csv_dir and      *
    *                   filename self.alias_table_filename                                      *
    *                                                                                           *
    * Return Value:     none                                                                    *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def write_alias_table(self):
        outfile = open(self.csv_dir + self.alias_table_filename, 'w')
        outcsv = csv.writer(outfile, delimiter=',', quotechar='"')
        outcsv.writerow(self.alias_table_header)
        outcsv.writerows(self.alias_table)
        outfile.close()

    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    write_tables                                                            *
    *                                                                                           *
    * Description:      writes out both the alias table and the lookup table to csv files       *
    *                                                                                           *
    * Return Value:     none                                                                    *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def write_tables(self):
        self.write_lookup_table()
        self.write_alias_table()
    
    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    tables_exist                                                            *
    *                                                                                           *
    * Description:      Checks if both the alias table csv and the lookup table csv file already*
    *                   exist                                                                   *
    *                                                                                           *
    * Return Value:     bool                                                                    *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def tables_exist(self):
        return os.path.isfile(self.csv_dir + self.lookup_table_filename) and os.path.isfile(self.csv_dir + self.alias_table_filename)
    
    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    tables_complete                                                         *
    *                                                                                           *
    * Description:      Goes through each item that the class has seen and checks if there is an*
    *                   entry in the lookup table for it, or if there is an alias that is       *
    *                   contained within the lookup table. If there is not the function returns *
    *                   False                                                                   *
    *                                                                                           *
    * Return Value:     bool                                                                    *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def tables_complete(self):
        for item_name in self.items:
            if not any(row[self.lookup_table_item_i] == item_name for row in self.lookup_table) and not self.get_alias(item_name):
                return False
        
        return True
    
    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    create_alias                                                            *
    *                                                                                           *
    * Description:      Adds an entry to the alias table                                        *
    *                                                                                           *
    * Return Value:     none                                                                    *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def create_alias(self, item_name, alias):
        self.alias_table.append([item_name, alias])  
    
    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    get_alias                                                               *
    *                                                                                           *
    * Description:      Retreives the alias for a given item name if it exists. Returns '' if   *
    *                   there is not one                                                        *
    *                                                                                           *
    * Parameters:       str item_name   :   The item for which to find an alias for             *
    *                                                                                           *
    * Return Value:     str :   The name of the item item_name points to                        *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def get_alias(self, item_name):
        for row in self.alias_table:
            if (row[self.alias_table_item_i] == item_name):
                return row[self.alias_table_alias_i]

        return ''
    
    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    get_cost                                                                *
    *                                                                                           *
    * Description:      Obtains the cost to create an item given it's name and the date to get  *
    *                   the price for                                                           *
    *                                                                                           *
    * Parameters:       str item      :     The item for which to find the cost for             *
    *                   datetime date :     The date for which to find the cost for             * 
    *                                                                                           *
    * Return Value:     float         :     The cost of the item                                *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def get_cost(self, item, date):
        alias = self.get_alias(item)
            
        if alias:
            item = alias

        if date == 'present':
            date = datetime.datetime.now().date()
        else:
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

        if item in self.valid_items:
            for row in self.lookup_table:
                
                if row[self.lookup_table_cost_i] == -1:
                    return 'ignore' 

                start_str = row[self.lookup_table_startdate_i].strip()
                end_str = row[self.lookup_table_enddate_i].strip()

                if start_str == 'present':
                    start_date = datetime.datetime.today().date()
                else:
                    start_date = datetime.datetime.strptime(row[self.lookup_table_startdate_i].strip(), '%Y-%m-%d').date()
                
                if end_str == 'present':
                    end_date = datetime.datetime.today().date()
                else:
                    end_date = datetime.datetime.strptime(row[self.lookup_table_enddate_i].strip(), '%Y-%m-%d').date()

                if (row[self.lookup_table_item_i] == item) and (date > start_date) and (date <= end_date):
                    return row[self.lookup_table_cost_i]
        
        return -1

    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    visit_row                                                               *
    *                                                                                           *
    * Description:      Memorizes the data from a row into this class                           *
    *                                                                                           *
    * Parameters:       str row     :   A row of data from the ebay database csv                *
    *                                                                                           *
    * Return Value:     none                                                                    *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def visit_row(self, row):
        self.items.add(row[self.item_name_i])

        self.update_valid_items()
    
    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    update_valid_items                                                      *
    *                                                                                           *
    * Description:      Makes it so that any items not in the lookup table are listed in the    *
    *                   new itemes list                                                         *
    *                                                                                           *
    * Return Value:     none                                                                    *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def update_valid_items(self):
        self.valid_items = [item for item in [row[self.lookup_table_item_i] for row in self.lookup_table]]
        self.valid_items.extend([item for item in self.items if self.get_alias(item) != ''])

        self.new_items = [item for item in self.items if item not in self.valid_items]
    
    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    print_lookup_table                                                      *
    *                                                                                           *
    * Description:      Prints a complete price list for the valid items on a date              *
    *                                                                                           *
    * Parameters:       str date    :   The date for which to print the price list for          *
    *                                                                                           *
    * Return Value:     none                                                                    *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def print_lookup_table(self, date='present'):
        lookup_table_items = [item for item in [row[self.lookup_table_item_i] for row in self.lookup_table]]
        
        for i, item in enumerate(lookup_table_items):
            print(i, ':', item, "-", self.get_cost(item, date))
    
    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    print_new_items                                                         *
    *                                                                                           *
    * Description:      Prints all new items in the new items list                              *
    *                                                                                           *
    * Return Value:     none                                                                    *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def print_new_items(self):
        for i, item in enumerate(self.items):
            print(i, ' - ', item)

    '''
    * ***************************************************************************************** *
    *                                                                                           *
    * Function name:    run_define_costs                                                        *
    *                                                                                           *
    * Description:      Runs an interactive shell to add items to the lookup table              *
    *                                                                                           *
    * Return Value:     none                                                                    *
    *                                                                                           *
    * ***************************************************************************************** *
    '''
    def run_define_costs(self):
        menu = '''
            0 - exit
            2 - add costs for new items
            3 - add past costs for a current item 
            4 - modify item
            5 - create alias
        '''

        while True:
            print(menu)
            action = input('>> ')

            if action == '2':
                for item in self.new_items:
                    print('Current item: ', item)
                    print('Enter -1 to ignore the item cost, and exit to quit entering costs')
                    
                    cost = input('Cost >> ')

                    if cost == '-1':
                        self.lookup_table.append([item, cost,'2000-1-1','present']) 
                        continue
                    elif cost == 'exit':
                        break

                    print('Dates in format MM-DD-YYYY')
                    start_date = input('Effective start date >> ')
                    end_date = input('Effective end date (input "present" if this is the current cost) >> ')

                    self.lookup_table.append([item, cost, start_date, end_date])
                    clear() 
                
                self.write_tables()
                self.load_tables()
            elif action == '3':
                self.print_lookup_table()

                item_i = input('Item >> ')

                if int(item_i) < len(self.valid_items):
                    cost = input('Cost >> ')
                    print('Dates in format MM-DD-YYYY')

                    start_date = input('Effective start date >> ')
                    end_date = input('Effective end date (input "present" if this is the current cost) >> ')

                    self.lookup_table.append([self.valid_items[int(item_i)], cost, start_date, end_date])
            elif action == '0':
                break

if __name__ == "__main__":

    print('ItemManager test cases: ')
    lookup_table_header = ['Item', 'Cost', 'Start Date', 'End Date']
    lookup_table = [['Item1', '10.99', '01-22-2012','present'],
                    ['Item2', '29.99', '02-12-2015', 'present'],
                    ['Item4', '10.86', '03-13-2021','present'],]

    alias_table_header = ['Item', 'Alias']
    alias_table = [['Item3', 'Item1'],
                   ['Item8', 'Item2'],]

    itemManager = ItemManager(['Item title'])
    itemManager.lookup_table = lookup_table
    itemManager.lookup_table_header = lookup_table_header
    itemManager.alias_table_header = alias_table_header
    itemManager.alias_table = alias_table

    itemManager.visit_row(['Item8'])
    itemManager.visit_row(['Item1'])
    itemManager.visit_row(['Item3'])

    
    print('Lookup table: ', itemManager.lookup_table)
    print('Alias table: ', itemManager.alias_table)
    print('Items: ', itemManager.items)
    print('Item3 alias: ', itemManager.get_alias('Item3')) 
    itemManager.update_valid_items()
    print('Cost of Item3:', itemManager.get_cost('Item3', 'present'))
    print('Cost of Item2:', itemManager.get_cost('Item2', datetime.datetime(2019, 5, 23)))
    print('Cost of Item1:', itemManager.get_cost('Item1', datetime.datetime(2020, 6, 26)))
    print('Tables complete: ', itemManager.tables_complete())

    itemManager.print_lookup_table()
    
    print('new items:')
    itemManager.print_new_items()
    

