'''
' By Wesley Duffee-Braun
' For the purposes of searching the CJIS system of Nashville/Davidson Metro Area
' To help improve efficiency of expungement requests
' See more information including license at https://github.com/wduffee/expungement-metro
'''

import sys, getopt
import requests
from bs4 import BeautifulSoup


def initial_search(fname,lname,bday):
    first_search = "https://sci.ccc.nashville.gov/Search/Search?firstName="+fname+"&lastname="+lname+"&birthday="+str(bday)
    print("First Search: " + first_search)
    r = requests.get(first_search, stream=True)

    soup = BeautifulSoup(r.text, 'html.parser')
    results_html = soup.find(attrs={'id':'results-list'})
    
    # print(results_html)
    
    number_results = 0
    name_birthday_search = []

    # Look through the results-list table and pull all links
    # The links will provide the results without having to look at the table contents
    
    if results_html:
        for a in results_html.find_all('a', href=True):
            number_results += 1

            # Don't add the same link more than once
            if a['href'] not in name_birthday_search:
                name_birthday_search.append(a['href'])
                # print("Found the URL: " + a['href'])
            
    if number_results == 0:
        print("No results found for these search criteria:")
        print("\tFirst Name: ", fname)
        print("\tLast Name : ", str(lname))
        print("\tBirthday  : ", str(bday))
    else:
        count = 1
        for link in name_birthday_search:
            parsed_link = link.split("/")
            parsed_results = parsed_link[3].split("^")
            print("Result #"+str(count)+":")
            print("\tFirst Name: "+ parsed_results[0])
            print("\tLast Name : "+ parsed_results[1])
            print("\tBirthday  : "+ parsed_results[2])
            print("\tOCA Number: "+ parsed_results[3])
            count += 1
        print("Choose which result to gather further information. For example, if you want to choose result 1 above, press 1 and then press Enter")
        print("To cancel, enter 0 and press Enter")
        search_selection = input("Enter your selection: \n")

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
            search_retrieval_link = name_birthday_search[search_selection_value-1]
            print(search_retrieval_link)
        else:
            print("-----------\n| Goodbye |\n-----------\n")

def main(argv):
    fname=""
    lname=""
    bday=""
    opts, args = getopt.getopt(argv,"hf:l:b:") #,["fname=","lname=","bday="])
    for opt, arg in opts:
        if opt == '-h':
            print("Syntax as follows:")
            print("-f FIRSTNAME -l LASTNAME -b BIRTHDAY")
            print("Please use double quotes around each argument")
            print("BIRTHDAY needs to be in MM/DD/YYYY format")
            sys.exit()
        elif opt in ("-f"):
            fname = arg
        elif opt in ("-l"):
            lname = arg
        elif opt in ("-b"):
            bday = arg

    # Check for correct input
    while fname == "":
        fname = input("First name is required. Please provide a first name to search: \n")
    while lname == "":
        lname = input("Last name is required. Please provide a last name to search: \n")
    while bday == "":
        bday = input("Birthday is required. Please provide a birthday in the MM/DD/YYYY format to search: \n")

    print ("This is your search criteria:")
    print ("First Name: ", fname)
    print ("Last Name : ", lname)
    print ("Birthday  : ", str(bday))

    initial_search(fname,lname,bday)

    
        
if __name__ == "__main__":
    main(sys.argv[1:])


