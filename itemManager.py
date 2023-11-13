import csv
import os
from os.path import isfile

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

        self.lookup_table_header = ['Item','Cost']
        self.lookup_table_item_i = self.lookup_table_header.index('Item')
        self.lookup_table_cost_i = self.lookup_table_header.index('Cost')
        self.lookup_table = []

        self.load_lookup_tables()

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

   
    def load_alias_table(self):
        if os.path.isfile(self.csv_dir + self.alias_table_filename):
            infile = open(self.csv_dir + self.alias_table_filename, 'r')
            incsv = csv.reader(infile, delimiter=',', quotechar='"')

            self.alias_table_header= incsv.__next__()
            self.alias_table = [row for row in incsv]
        else:
            outfile = open(self.csv_dir + self.alias_table_filename, 'w')
            outfile.close()

    
    def load_lookup_tables(self):
        self.load_lookuptable()
        self.load_alias_table()
    
    def write_lookup_table(self):
        outfile = open(self.csv_dir + self.lookup_table_filename, 'w')
        outcsv = csv.writer(outfile, delimiter=',', quotechar='"')
        outcsv.writerow(self.lookup_table_header)
        outcsv.writerows(self.lookup_table)
        outfile.close()

    def write_alias_table(self):
        outfile = open(self.csv_dir + self.alias_table_filename)
        outcsv = csv.writer(outfile, delimiter=',', quotechar='"')
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
            print('Any1: ' ,any(row[self.lookup_table_item_i] == item_name for row in self.lookup_table))
            print('Item name exists', self.get_alias(item_name))
            if not any(row[self.lookup_table_item_i] == item_name for row in self.lookup_table) and not self.get_alias(item_name):
                return False
        
        return True
    
    def create_alias(self, item_name, alias):
        self.alias_table.append([item_name, alias])  
    
    def get_alias(self, item_name):
        for row in self.alias_table:
            if (row[self.alias_table_item_i] == item_name):
                return row[self.alias_table_item_i]

        return ''
    
    def visit_row(self, row):
        self.items.add(row[self.lookup_table_item_i])

if __name__ == "__main__":
    itemManager = ItemManager(['Item title'])
    itemManager.visit_row(['Item1'])
    itemManager.visit_row(['Item2'])
    itemManager.visit_row(['Item4'])
    itemManager.visit_row(['Item3'])
    print('Alias table: ', itemManager.alias_table)
    print('Items: ', itemManager.items)
    print('Item3 alias: ', itemManager.get_alias('Item3'))
    print('Tables complete: ', itemManager.tables_complete())

