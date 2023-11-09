import csv
import os
from datetime import date, datetime
from re import sub

if __name__ == "__main__":
    csv_filename = 'costs.csv'
    infile = open(csv_filename, 'r')
    incsv = csv.reader(infile, delimiter=',', quotechar='"')

    inheader = incsv.__next__()
    indataset = [row for row in incsv]
    infile.close() 

    items = list(set([row[inheader.index('Item')].strip() for row in indataset]))
    items.sort()

        
    menu = '''
    Commands:
        add - add an item
        sum - total of costs
        exit - exit the program
    '''
    
    while True:
        print(menu)

        cmd = input(">> ")

        if cmd == 'exit':
            break

        if cmd == 'add':
            print('Existing items:')

            for i, item in enumerate(items):
                print(i, " : ", item)
            
            # Get item name
            # =================================================================
            item_name = input('\nEnter a number or the name of a new item >> ')
            
            old_item = False
            try:
                item_int = int(item_name)
                item_name = items[item_int]
                old_item = True
            except ValueError:
                pass
            
            # Get date 
            # =================================================================
            today = date.today() # type: ignore 
            today_date = today.strftime('%m/%d/%Y')
            date = input('Date of purchase, defualt: ' + today_date + ' >> ' )

            if not date:
                date = today_date

            # Get website 
            # =================================================================
            old_website = '' 
            # If the item already exists in the costs csv, look up the website that it was purchased at
            if old_item:
                website_i = inheader.index('Website')
                item_name_i = inheader.index('Item')
                for row in indataset:
                    if (row[item_name_i] == item_name):
                        old_website = row[website_i]

            # This gets hit if we're entering a new item, or for some reason we could not look up the
            # website used the last time the item was purchased
            website = input('Enter the website used for purchase, default (' + old_website + ') >>')
            if not website:
                website = old_website
            
            cost_unit = 0.0
            cost_unit_str = input('Enter the cost/unit >> ')
            try:
                cost_unit = float(cost_unit_str)
            except TypeError:
                raise TypeError("Could not convert cost into a float!")
            
            quantity_str = input('Quantity >> ')
            try:
                quantity = int(quantity_str)
            except TypeError:
                raise TypeError('Could not convert quantity to int')
            
            has_tax = True 
            has_tax_str = input('Sales tax? (y/n) >> ')

            if has_tax_str == 'n':
                has_tax = False 
            
            #TODO Per unit cost with tax needs to be seperate
            TAX_RATE = 0.06

            subtotal = cost_unit * quantity

            tax = 0.0
            if has_tax:
                tax = subtotal * TAX_RATE
            
            total = subtotal + tax
             
            new_row = [date, website, item_name, cost_unit, has_tax_str, tax, subtotal, quantity, total]
            # Date,Website,Item,Cost/unit,Has tax,Tax,Total cost,Quantity,Total,
            print(new_row)
            confirm = input('Does this look right? (y/n) >> ')

            if confirm == 'y':
                indataset.append(new_row)


    
    outfile = open(csv_filename, 'w')
    outcsv = csv.writer(outfile, delimiter=',', quotechar='"')
    
    outcsv.writerow(inheader)
    outcsv.writerows(indataset)

    outfile.close()

    


