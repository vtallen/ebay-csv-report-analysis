import csv
import os
from os import system, name
import datetime
import pandas as pd


def clear():
 
    # for windows
    if name == 'nt':
        _ = system('cls')
 
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')

'''
What this class needs to do:
    Visit each row of the transactions csv and derive:
    what items I have sold, then if those items have not
    been given costs, the user should be prompted to 
    give a cost.

    If the item should be ignored in the dataset, the 
    cost should be deleted from the dataset 
    
    The user should be able to enter duplicate removal mode where they can
    select two items and replace the titles of one of the items with the title of the
    other so that they will have the same cost when reports are run

'''
class ItemManager:
    def __init__(self, header, csv_dir='./', lookup_table_filename='item_lookup_table.csv', alias_table_filename='item_alias_table.csv'):
        self.csv_dir = csv_dir
        self.lookup_table_filename = lookup_table_filename
        self.alias_table_filename = alias_table_filename

        self.item_name_i = header.index('Item title')

        self.items = set()
             
        self.alias_table_header = ['Item','Alias']
        self.alias_table_item_i = self.alias_table_header.index('Item')
        self.alias_table_alias_i = self.alias_table_header.index('Alias')
        self.alias_table = []

        self.lookup_table_header = ['Item','Cost','Start Date', 'End Date']
        self.lookup_table_item_i = self.lookup_table_header.index('Item')
        self.lookup_table_cost_i = self.lookup_table_header.index('Cost')
        self.lookup_table_startdate_i = self.lookup_table_header.index('Start Date')
        self.lookup_table_enddate_i = self.lookup_table_header.index('End Date')
        self.lookup_table = []

        self.load_tables()

        self.valid_items = []
        self.new_items = []

    def load_lookuptable(self):
        if os.path.isfile(self.csv_dir + self.lookup_table_filename):
            infile = open(self.csv_dir + self.lookup_table_filename, 'r')
            incsv = csv.reader(infile, delimiter=',', quotechar='"')

            self.lookup_table_header = incsv.__next__()
            self.lookup_table = [row for row in incsv]
            infile.close()

            for line in self.lookup_table:
                print(line)
        else:
            outfile = open(self.csv_dir + self.lookup_table_filename, 'w')
            outfile.close()

   
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

    
    def load_tables(self):
        self.load_lookuptable()
        self.load_alias_table()
    
    def write_lookup_table(self):
        outfile = open(self.csv_dir + self.lookup_table_filename, 'w')
        outcsv = csv.writer(outfile, delimiter=',', quotechar='"')
        outcsv.writerow(self.lookup_table_header)
        outcsv.writerows(self.lookup_table)
        outfile.close()

    def write_alias_table(self):
        outfile = open(self.csv_dir + self.alias_table_filename, 'w')
        outcsv = csv.writer(outfile, delimiter=',', quotechar='"')
        print('alias header' , self.alias_table_header) 
        outcsv.writerow(self.alias_table_header)
        outcsv.writerows(self.alias_table)
        outfile.close()

    def write_tables(self):
        self.write_lookup_table()
        self.write_alias_table()
    
    def tables_exist(self):
        return os.path.isfile(self.csv_dir + self.lookup_table_filename) and os.path.isfile(self.csv_dir + self.alias_table_filename)
    
    def tables_complete(self):
        for item_name in self.items:
            if not any(row[self.lookup_table_item_i] == item_name for row in self.lookup_table) and not self.get_alias(item_name):
                return False
        
        return True
    
    def create_alias(self, item_name, alias):
        self.alias_table.append([item_name, alias])  
    
    def get_alias(self, item_name):
        for row in self.alias_table:
            if (row[self.alias_table_item_i] == item_name):
                return row[self.alias_table_alias_i]

        return ''
    
    def get_cost(self, item, date):
        alias = self.get_alias(item)
            
        if alias:
            item = alias

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

                datelist = pd.date_range(start_date, end_date)
                datelist = [x.date() for x in datelist]

                if (row[self.lookup_table_item_i] == item) and date in datelist: 
                    return row[self.lookup_table_cost_i]
        
        return -1

    def visit_row(self, row):
        self.items.add(row[self.item_name_i])

        self.update_valid_items()
    
    def update_valid_items(self):
        self.valid_items = [item for item in [row[self.lookup_table_item_i] for row in self.lookup_table]]
        self.valid_items.extend([item for item in self.items if self.get_alias(item) != ''])

        self.new_items = [item for item in self.items if item not in self.valid_items]
    
    def print_lookup_table(self, date='present'):
        lookup_table_items = [item for item in [row[self.lookup_table_item_i] for row in self.lookup_table]]
        
        for i, item in enumerate(lookup_table_items):
            print(i, ':', item, "-", self.get_cost(item, date))
    
    def print_new_items(self):
        for i, item in enumerate(self.items):
            print(i, ' - ', item)

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
    

