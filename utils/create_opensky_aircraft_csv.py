__author__ = "jdanek"

import csv
import re
import sys

# Global Vars 
DATA_FILE = "../data/opensky/aircraft.csv"

def normalize_string(str):
    if str == "" or str == "''":
        return ""
    else:
        values = ["\(", "\)", "-{2,}", "\.{2,}", "\"", "'"]
        for repl in values:
            str = re.sub(repl, "", str) 
        
        values = ["/", "\\\\"]
        for repl in values:
            str = re.sub(repl, " ", str) 

        return str

def is_roman(str):

    isRoman = True
    for c in str:
        if c.upper() not in "IVXLCDM":
            isRoman = False
    return isRoman


def remove_duplicates(str):
    words = str.split()
    return (" ".join(sorted(set(words), key=words.index)))


def capitalize_model(str):
    temp = ""
    for word in str.split():
        is_alpha_hypen = all(c.isalpha() or c == '-' for c in word)
        if is_alpha_hypen and len(word) > 3 and not is_roman(word):
            temp = temp + word.title() + " "
        else:
            temp = temp + word + " "
    return temp


def capitalize_manufacturer(str):
    temp = ""
    for word in str.split():
        if len(word) < 3:
            temp = temp + word.upper() + " "
        else:
            temp = temp + word.title() + " "
    return temp


def truncate_middle(s, max_length, placeholder="..."):
    if len(s) <= max_length:
        # Return the original string if it is already short enough
        return s

    # Calculate the number of characters to keep at each end
    # Subtract the length of the placeholder from the total allowed length
    # and divide by 2 for the left and right sides
    chars_each_end = (max_length - len(placeholder)) // 2
    
    # Slice the start and end of the string and combine them with the placeholder
    truncated_string = s[:chars_each_end] + placeholder + s[-chars_each_end:]
    return truncated_string


def make_pretty(str):
    # remove if not at start of string
    values = ["Aircraft","Aviation","International"]
    for value in values:
        str = re.sub("(?<!^)\s" + value + "\s*", " ", str) 

    # remove everywhere
    values = ["Dba", "The", "Corporation", "Corp\.?", "Company", "Indust.*", "Inc\.?", "INC\.?", 
        "Ltd\.?","Limited", "Co\.", "Division\ Of", "Division", "Gmbh"]
    for value in values:
        str = re.sub("\s" + value + "\s*", " ", str) 

    # miscellaneous name fixes
    str = re.sub("Dehavilland|De\ Havilland\ Canada|De\ Havilland", "DeHavilland", str, flags=re.IGNORECASE) 
    str = re.sub("Canada Lp(\s|$)|Canada(\s|$)", "", str, flags=re.IGNORECASE) 
    str = re.sub("3017583", "", str) #Canada Inc
    str = re.sub("S\.A\.S\.?|Sas(\s|$)", "", str) 
    str = re.sub("Atr(\s|$)", "ATR ", str) 
    str = re.sub("Brm(\s|$)", "BRM ", str) 
    str = re.sub("Let(\s|$)", "LET ", str) 
    str = re.sub("Lot(\s|$)", "LOT ", str) 
    str = re.sub("Lai(\s|$)", "LAI ", str) 
    str = re.sub("Aai(\s|$)", "AAI ", str) 
    str = re.sub("Iai(\s|$)", "IAI", str) 
    str = re.sub("Fma(\s|$)", "FMA ", str) 
    str = re.sub("Unc(\s|$)", "UNC ", str) 
    str = re.sub("Tbm(\s|$)", "TBM ", str) 
    str = re.sub("Itv(\s|$)", "ITV ", str) 
    str = re.sub("Sas(\s|$)", "SAS ", str) 
    str = re.sub("Raca(\s|$)", "RACA ", str) 
    str = re.sub("S\.A\.N\.?|San(\s|$)", "SAN ", str) 
    str = re.sub("S\.A\.I\.?|Sai(\s|$)", "SAI ", str) 
    str = re.sub("C\.E\.A\.?|Cea(\s|$)", "CEA ", str) 
    str = re.sub("-(\s|$)", " ", str) 
    str = re.sub("([a-z]{3,})-([a-z]{3,})-([a-z]{3,})(\s|$)", r"\1 \2 \3 ", str, flags=re.IGNORECASE) 
    str = re.sub("([a-z]{3,})-([a-z]{3,})(\s|$)", r"\1 \2 ", str, flags=re.IGNORECASE) 
    str = re.sub("  ", " ", str) 
    
    # remove duplicate text and limit size 
    str = remove_duplicates(str).strip()
    #str = truncate_middle(str, 36) 
    return str


def main():
    with open(DATA_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        # row[0]:  icao24
        # row[12]: manufacturerIcao
        # row[13]: manufacturerName
        # row[14]: model
        
        for row in reader:
            try:
                a = normalize_string(row[0])
                b = capitalize_manufacturer(normalize_string(row[12]))
                c = capitalize_manufacturer(normalize_string(row[13]))
                d = capitalize_model(normalize_string(row[14]))
            except IndexError:
                # handle bad data in original open sky csv file
                continue

            # no valid aircraft text
            if( b=="" and c=="" and d=="" ):
                continue

            # concatenate elements
            aircraft = ""
            if b == "":
                aircraft = c + " " + d
            else:
                aircraft = b + " " + c + " " + d

            # output processed entry to stdout
            aircraft = make_pretty(aircraft)
            if( aircraft != "" ):
                print(a + ',' + aircraft)

if __name__ == "__main__":
    main()