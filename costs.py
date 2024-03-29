import csv
from datetime import date 
import os

'''
* ***************************************************************************************** *
*                                                                                           *
* Function name:    get_costs_dataset                                                       *
*                                                                                           *
* Description:      Loads the business costs csv into memory                                *
*                                                                                           *
* Return Value:     [str]   header      :   The header for the csv file                     *
*                   [[str]] indataset   :   The table of the csv file                       *
*                                                                                           *
* ***************************************************************************************** *
'''
def get_costs_dataset(costs_csv_dir='./', costs_csv_filename='costs.csv'):
    inheader = []
    indataset = []
    if os.path.isfile(costs_csv_dir + costs_csv_filename):
        infile = open(costs_csv_dir + costs_csv_filename, 'r')
        incsv = csv.reader(infile, delimiter=',', quotechar='"')

        inheader = incsv.__next__()
        indataset = [row for row in incsv]
        infile.close() 

    return inheader, indataset

'''
* ***************************************************************************************** *
*                                                                                           *
* Function name:    write_csv                                                               *
*                                                                                           *
* Description:      Writes the costs csv out to a file                                      *
*                                                                                           *
* Parameters:       str csv_dir     :   The directory to look for the csv file              *
*                   str csv_filename:   Filename of the csv file                            *
*                   [str] header    :   Header of the csv file                              *
*                   [[str]] dataset :   The data to write to the csv                        *
*                                                                                           *
* Return Value:     none                                                                    *
*                                                                                           *
* ***************************************************************************************** *
'''
def write_csv(csv_dir, csv_filename, header, dataset):
    outfile = open(csv_dir + csv_filename, 'w')
    outcsv = csv.writer(outfile, delimiter=',', quotechar='"')
    
    outcsv.writerow(header)
    outcsv.writerows(dataset)

    outfile.close()

'''
* ***************************************************************************************** *
*                                                                                           *
* Function name:    get_item_row                                                            *
*                                                                                           *
* Description:      Launches into an interactive prompt to enter a transaction into the csv *
*                                                                                           *
* Parameters:       [str] inheader  :   header for the csv file                             *
*                   [[str]] dataset :   The data to write to the csv                        *
*                                                                                           *
* Return Value:     [str] row       :   A row of data for the csv file                      *
*                                                                                           *
* ***************************************************************************************** *
'''
def get_item_row(inheader, indataset):
    items = list(set([row[inheader.index('Item')].strip() for row in indataset]))
    items.sort()
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
    purchase_date = input('Date of purchase, defualt: ' + today_date + ' >> ' )

    if not purchase_date:
        purchase_date = today_date

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


    tax = 0.0
    if has_tax:
        tax = cost_unit * TAX_RATE

    per_item_total = cost_unit + tax
    total = per_item_total * quantity
             
    new_row = [purchase_date, website, item_name, cost_unit, has_tax_str, tax, per_item_total, quantity, total]

    return new_row

'''
* ***************************************************************************************** *
*                                                                                           *
* Function name:    run                                                                     *
*                                                                                           *
* Description:      Launches into an interactive prompt to enter an arbitrary number of     *
*                   transactions into the csv. Also writes out the csv to disk              *
*                                                                                           *
* Parameters:       str csv_dir     :   Directory where the csv will be stored              *
*                   str csv_filename:   Filename of the csv file                            *
*                   [str] inheader  :   header for the csv file                             *
*                   [[str]] dataset :   The data to write to the csv                        *
*                                                                                           *
* Return Value:     none                                                                    *
*                                                                                           *
* ***************************************************************************************** *
'''
def run(csv_dir, csv_filename, header, dataset):
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

        elif cmd == 'add':
            # Date,Website,Item,Cost/unit,Has tax,Tax,Total cost,Quantity,Total,
            new_row = get_item_row(header, dataset)
            print(new_row)
            confirm = input('Does this look right? (y/n) >> ')

            if confirm == 'y':
                indataset.append(new_row)
        
        elif cmd == 'sum':
            print('Total costs: ', sum_costs(header, dataset))

    write_csv(csv_dir, csv_filename, inheader, indataset)

'''
* ***************************************************************************************** *
*                                                                                           *
* Function name:    sum_costs                                                               *
*                                                                                           *
* Description:      Adds up all costs in the csv file                                       *
*                                                                                           *
* Parameters:       [str] header    :   header for the csv file                             *
*                   [[str]] dataset :   The data to write to the csv                        *
*                                                                                           *
* Return Value:     float                                                                   *
*                                                                                           *
* ***************************************************************************************** *
'''
def sum_costs(header, dataset):
    total_i = header.index('Total')
    
    total = 0.0
    for i, row in enumerate(dataset):
        try:
            total += float(row[total_i])
        except TypeError:
            print('No valid data for field "Total" on line ', i)
    
    return total

if __name__ == "__main__":
    csv_filename = 'costs.csv'
    csv_file_dir = './'

    inheader, indataset = get_costs_dataset(csv_file_dir, csv_filename)
    run(csv_file_dir, csv_filename, inheader, indataset)
