'''
' By Wesley Duffee-Braun
' For the purposes of searching the CJIS system of Nashville/Davidson Metro Area
' To help improve efficiency of expungement requests
' See more information including license at https://github.com/wduffee/expungement-metro
'''

import sys, argparse
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime


class SearchResults:
    def __init__(self):
        self.datetime_of_report = ""
        self.url = ""
    
    def return_report_datetime_for_filename(self):
        date_obj = datetime.strptime(self.datetime_of_report,'%m/%d/%Y %I:%M:%S %p')
        date_string = str(date_obj)
        date_string = date_string.replace(' ','-')
        date_string = date_string.replace(':','')
        return date_string
        
class ExpungementCandidate:
    def __init__(self):
        self.fname = ""
        self.lname = ""
        self.bday = ""
        self.oca = ""
        self.records = []

    def set_info(self, fname, lname, bday, oca):
        self.fname = fname
        self.lname = lname
        self.bday = bday
        self.oca = oca

    def add_record(self,record):
        self.records.append(record)

    def return_record_information(self, record_type):
        dict_to_return = []
        for record in self.records:
            if record.record_type == record_type:
                dict_to_return.append(record.information)
        return dict_to_return


class Record:
    def __init__(self):
        self.information = {}
        self.record_type = ""


# Declare variables needed to get the program started  

initial_search_args = {"fname": "", "lname": "", "bday": "", "oca":""}
candidate = ExpungementCandidate()
search_results = SearchResults()

def parse_options(argv):

    parser = argparse.ArgumentParser(description="For the purposes of searching the CJIS system of Nashville/Davidson Metro Area")
    parser.add_argument("-f",'--first',required=True, help="First name to include in the search")
    parser.add_argument("-l",'--last',required=True, help="Last name to include in the search")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-b','--birthday',help="Birthday to include in the search. Use MM/DD/YYYY format with quotes. Do not use with --nobirthday flag.")
    group.add_argument('--nobirthday',action='store_true',help="Do not include birthdays in the initial search. Required if omitting the -b/--birthday flag.")
    parser.add_argument('-o','--oca',help="OCA number to include in search (optional). Including this flag will bypass the initial search, potentially with unexpected results.")
    args = parser.parse_args()

    initial_search_args["fname"] = args.first
    initial_search_args["lname"] = args.last

    # Don't want to have None in the initial_search_args, easier to use an empty string
    if args.birthday == None:
        initial_search_args["bday"] = ""
    else:
        initial_search_args["bday"] = args.birthday
    if args.oca == None:
        initial_search_args["oca"] = ""
    else:
        initial_search_args["oca"] = args.oca
    

def initial_search():

    initial_search_url = "https://sci.ccc.nashville.gov/Search/Search?firstName="+ \
        initial_search_args["fname"]+ \
        "&lastname="+initial_search_args["lname"]+ \
        "&birthday="+initial_search_args["bday"]+ \
        "&oca="+initial_search_args["oca"]
    
    print("Initial Search URL: ", initial_search_url)
    
    r = requests.get(initial_search_url, stream=True)

    soup = BeautifulSoup(r.text, 'html.parser')
    results_html = soup.find(attrs={'id':'results-list'})
      
    name_birthday_search = []

    # Look through the results-list table and pull all links
    # The links will provide the information needed for the user
    # to make a selection of which candidate to further examine
    
    if results_html:
        for a in results_html.find_all('a', href=True):
            # Don't add the same link more than once
            if a['href'] not in name_birthday_search:
                name_birthday_search.append(a['href'])
            
    if not name_birthday_search:
        # display that there were zero results found for the search criteria.
        print("--------------------------------------------------------------")
        print("No results found for search criteria")
        print("-----------\n| Exiting |\n-----------\n")
        return 0
    else:
        # walk through the results
        count = 1
        print("--------------------------------------------------------------")
        print("Results found. See below and choose a result to proceed:")
        print("--------------------------------------------")
        for link in name_birthday_search:
            parsed_link = link.split("/")
            parsed_results = parsed_link[3].split("^")
            print("Result #"+str(count)+":")
            print("\tFirst Name: "+ parsed_results[0])
            print("\tLast Name : "+ parsed_results[1])
            print("\tBirthday  : "+ parsed_results[2])
            print("\tOCA Number: "+ parsed_results[3])
            count += 1
        print("Choose which result to gather further information.\nFor example, if you want to choose result 1 above, press 1 and then press Enter")
        print("To exit, enter 0 and press Enter")
        search_selection = input("Choose your selection: ")

        search_selection_value = -1

        invalid_selection = True

        while invalid_selection:
            # Is input a number of any kind?
            if search_selection.isnumeric():
                # Is input an integer?
                try:
                    search_selection_value = int(search_selection)
                except ValueError:
                    print("Amount must be a number (no decimals) from 0 to " + str(count-1))

                # Is input an integer within range?
                if search_selection_value > -1 and search_selection_value < count:
                    # Successful input
                    invalid_selection = False;
                else:
                    # Drop here for a valid number but not an integer or one in range
                    print("You chose " + str(search_selection)+". Please enter a number from 0 to " + str(count-1))
                    search_selection = input("Enter your selection: \n")
            else:
                # Input is not a number at all
                print("You chose " + str(search_selection)+". Please enter a number from 0 to " + str(count-1))
                search_selection = input("Enter your selection: \n")

        if search_selection_value > 0:
            # Valid Search Selection
            # Prepare for next data retrieval

            parsed_link = name_birthday_search[search_selection_value-1].split("/")
            parsed_results = parsed_link[3].split("^")            
            fname = parsed_results[0]
            lname = parsed_results[1]
            bday = parsed_results[2]
            oca = parsed_results[3]
            candidate.set_info(fname,lname,bday,oca)
            return 1

        else:
            print("-----------\n| Goodbye |\n-----------\n")
            return 0

def selected_search():

    search_results.url = "https://sci.ccc.nashville.gov/Search/CriminalHistory?P_CASE_IDENTIFIER="+ \
        candidate.fname+"%5E"+candidate.lname+"%5E"+candidate.bday+"%5E"+candidate.oca
    
    print("Selected search url:", search_results.url)    
    r = requests.get(search_results.url, stream=True)

    soup = BeautifulSoup(r.text, 'html.parser')

    # Establish date when the report was generated (according to the search results)
    ch_report_header = str(soup.find(attrs={'id':'crim-history-report-info'}))

    # Split the header in the content between "Date of Report:" and first HTML character
    search_date_index = ch_report_header.index('Date of Report:')
    ch_report_header = ch_report_header[search_date_index+16:]
    search_date_index = ch_report_header.index('<')
    search_results.datetime_of_report = ch_report_header[:search_date_index]

    ch_tag_rows = soup.find_all("div", {"class": "crim-history-row"})

    # Walk the list of BS4 tags returned from the find_all above
    for ch_tag in ch_tag_rows:

        # New Record for this entry
        record = Record()

        # Convert the ch_tag to string ch_row
        ch_row = str(ch_tag)

        # This entry is a CJIS entry
        if ch_row.find('Case Details') != -1:
            record.record_type = "Case" 
        # This entry is an Arrest Information entry
        elif ch_row.find('Arrest Information') != -1:
            record.record_type = "Arrest"
        
        # Walk the list of CH information and assign to the cjis_entry / legacy_entry instances
        ch_labels = ch_tag.find_all("span", {"class": "crim-history-label"})
        ch_fields = ch_tag.find_all("span", {"class": "crim-history-field"})
        
        label_count = 0

        # Walk the list of crim-history-labels and correlate related crim-history-field
        # Storing label:field as key:value pair in the record object instance
        for label in ch_labels:
            record.information[label.text.strip()] = ch_fields[label_count].text.strip()
            label_count += 1
        
        candidate.add_record(record)


def write_results():

    cases_filename = candidate.fname+"-"+candidate.lname+"-"+candidate.bday+"-"+search_results.return_report_datetime_for_filename()+"-cjis.csv"
    arrests_filename = candidate.fname+"-"+candidate.lname+"-"+candidate.bday+"-"+search_results.return_report_datetime_for_filename()+"-legacy.csv"

    cases = candidate.return_record_information("Case")
    
    if len(cases) > 0:
        with open(cases_filename,'w',encoding="utf8",newline="") as output_file:
            fc = csv.DictWriter(output_file,fieldnames=cases[0].keys(),)
            fc.writeheader()
            fc.writerows(cases)
        print("CJIS CSV created with",len(cases),"entries.")
    else:
        print("No CJIS Information Found.")
    
    arrests = candidate.return_record_information("Arrest")
    
    if len(arrests) > 0:
        with open(arrests_filename,'w',encoding="utf8",newline="") as output_file:
            fc = csv.DictWriter(output_file,fieldnames=arrests[0].keys(),)
            fc.writeheader()
            fc.writerows(arrests)
        print("Legacy CSV created with",len(arrests),"entries.")
    else:
        print("No Legacy Information Found.")
    

def main(argv):
    parse_options(argv)
    proceed = 0
  
    print ("This is your search criteria:")
    print ("\tFirst Name\t: ", initial_search_args["fname"])
    print ("\tLast Name \t: ", initial_search_args["lname"])
    print ("\tBirthday  \t: ", initial_search_args["bday"])

    if initial_search_args["oca"] != '':
        print ("\tOCA\t\t: ", initial_search_args["oca"])        
        candidate.set_info(initial_search_args["fname"], initial_search_args["lname"], 
                           initial_search_args["bday"].replace('/',''), initial_search_args["oca"])
        proceed = 1

    if proceed == 0:
        proceed = initial_search()
       
    if proceed == 1:
        selected_search()
        write_results()

if __name__ == "__main__":
    main(sys.argv[1:])


