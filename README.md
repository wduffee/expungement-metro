# The *expungement-metro* utility

This utility leverages the website of the Criminal Court Clerk of Metropolitan Nashville and Davidson County (*CCC*) to search, format, and export relevant information for expungement candidates.

Information about expungement in the Metropolitan Nashville and Davidson County area: https://ccc.nashville.gov/about-our-services/expungement-information/

## What does this script do?

This utility takes as input search parameters and, after ensuring the search results contain the desired matches, exports CSV files for use.

## Why is this tool needed?

While the CCC provides a public portal for the search and retrieval of records in a format easy to read by humans, the output is difficult to utilize for those needing to perform any additional computation such as sorting, merging, etc. This barrier to access must be removed for full access by the public.

This utility provides a mechanism where the same records available to the public for viewing is delivered to the user as a CSV which can be easily consumed by other tools/software/etc.

# How To Use

## Prerequisites

You must have Python v3.2 or greater and the following libraries installed (in order of program execution):
- **sys:** For running the utility\*
- **argparse:** For parsing the command line parameters\*
- **requests:** For gathering the data from the CCC site
- **bs4 / BeautifulSoup:** For parsing the returned data from the CCC site
- **datetime:** For proper parsing of returned data\*
- **csv:** For exporting the formatted results\*

*\* included in python 3.2 and greater by default*


## Command Line Execution
There is one file to run, `search.py`, which takes a variety of arguments. You must always include a first name and last name to search. There must be either specify a birthday (in MM/DD/YYYY format) or indicate that you do not want to include a birthday in the search. You can also include the OCA number in the search if known, which will bypass the initial search filtering and attempt to go straight to exporting data. Help is also available. 

- **-f FIRST, --first FIRST**: First name to include in the search *(required search parameter)*
- **-l LAST, --last LAST**: Last name to include in the search *(required search parameter)*
- **-b BIRTHDAY, --birthday BIRTHDAY**: Birthday to include in the search. Use MM/DD/YYYY format with quotes. Do not use with --nobirthday flag.
- **--nobirthday**: Do not include birthdays in the initial search. Required if omitting the -b/--birthday flag.
- **-o OCA, --oca OCA**: OCA number to include in search (optional). Including this flag will bypass the initial search, potentially with unexpected results.
- **-h, --help**: Show a help message and exit

## Example Command Line Executions

### Running the utility  with just a first name and last name

```bash
python3 search.py -f "John" -l "Smith" --nobirthday
```

### Running the utility with first name, last name, and a birthday

```bash
python3 search.py -f "John" -l "Smith" -b "05/30/1950"
```

### Running the utility with first name, last name, birthday, and OCA number.

```bash
python3 search.py -f "FIRSTNAME" -l "LASTNAME" -b "05/30/1900" -o '123456'
```

## Program Execution

### Without the OCA parameter

Running the utility without the OCA number generates all matching results from which the user can select their desired match: 

```
$ python3 search.py -f "John" -l "Smith" -b "05/30/1950"
This is your search criteria:
	First Name	:  John
	Last Name 	:  Smith
	Birthday  	:  05/30/1950
Initial Search URL:  https://sci.ccc.nashville.gov/Search/Search?firstName=John&lastname=Smith&birthday=05/30/1950&oca=
--------------------------------------------------------------
Results found. See below and choose a result to proceed:
--------------------------------------------
Result #1:
	First Name: JOHN Q
	Last Name : SMITH
	Birthday  : 05301950
	OCA Number:
Result #2:
	First Name: JOHN
	Last Name : SMITH
	Birthday  : 05301950
	OCA Number: 123456
Choose which result to gather further information.
For example, if you want to choose result 1 above, press 1 and then press Enter
To exit, enter 0 and press Enter
Choose your selection:
```

At this point, the user can enter either `1` or `2` to select the correct person to retrieve records, or `0` to exit.

```
Choose your selection: 2
Selected Search URL: https://sci.ccc.nashville.gov/Search/CriminalHistory?P_CASE_IDENTIFIER=JOHN%5ESMITH%5E05301950%5E123456
CJIS CSV created with 13 entries.
Legacy CSV created with 3 entries.
```

### With the OCA parameter

If the OCA number is known and entered on the command line, the initial search results step is skipped and the program skips straight to outputting the CSV files.

```
$ python3 search.py -f "John" -l "Smith" -b "05/30/1950" -o "123456"
This is your search criteria:
	First Name	:  John
	Last Name 	:  Smith
	Birthday  	:  05/30/1950
        OCA             :  123456
Selected search url: https://sci.ccc.nashville.gov/Search/CriminalHistory?P_CASE_IDENTIFIER=JOHN%5ESMITH%5E05301950%5E123456
CJIS CSV created with 13 entries.
Legacy CSV created with 3 entries.
```

## Output from Execution

This person had 16 total records which were written to two CSV files, depending on the age of the record. These are written to the local directory in the format. Older records are in the "Legacy" and newer records are in the "CJIS" output. They follow the convention

```
FIRSTNAME-LASTNAME-BIRTHDAY-DATETIME_OF_RUNNING_UTILITY-[legacy|cjis].csv
```

The `DATETIME_OF_RUNNING_UTILITY` is in North American Central Time.

The user will see the searches performed to gather information so they can view the same results by copying and pasting the presented "Initial Search URL" and "Selected Search URL" into their web browser.


# Terms of Usage

Usage of this tool must abide by any terms put forth in via the CCC. See details at https://ccc.nashville.gov/

# License and Source

This tool is provided under the open source GPLv3 license with code available at https://github.com/wduffee/expungement-metro/

