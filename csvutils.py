import csv
import datetime

# Takes in a filename to a csv file. It then opens the csv
# and converts every value in col_num in date format in_fmt
# to the format defined in out_fmt
def fix_date_format(filename, col_num, in_fmt, out_fmt):
    infile = open(filename, 'r')
    incsv = csv.reader(infile, delimiter=',', quotechar='"')
    inheader = incsv.__next__() 

    out_table = []
    out_table.append(inheader)

    for i, row in enumerate(incsv):
        try:
            indate = datetime.datetime.strptime(row[col_num], in_fmt).date()
            outdate = indate.strftime(out_fmt)

            temprow = row
            temprow[col_num] = outdate
            out_table.append(temprow)
        except ValueError:
            print('line', i+1, 'contains a date', row[col_num], 'not consistant with format', in_fmt, ', ignoring row')
            out_table.append(row)
    
    infile.close()

    outfile = open(filename, 'w')
    outcsv = csv.writer(outfile, delimiter=',', quotechar='"')
    outcsv.writerows(out_table)
    outfile.close()

def sum_col(filename, field_str):
    infile = open(filename, 'r')
    incsv = csv.reader(infile, delimiter=',', quotechar='"')
    inheader = incsv.__next__()

    col_i = inheader.index(field_str)
    sum = 0.0

    for row in incsv:
        sum += float(row[col_i])
    
    return sum

if __name__ == '__main__':
    print(sum_col('mercari_reports/2022report.csv', 'Net Seller Proceeds')) 
    print(sum_col('mercari_reports/2023report.csv', 'Net Seller Proceeds')) 
