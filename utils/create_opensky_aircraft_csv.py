'''This module contains the preconditioning script for OpenSky aircraft data'''
__author__ = "jdanek"

import csv
import re

# Global Vars
DATA_FILE = "../data/opensky/aircraft.csv"

def normalize_string(text):
    '''Normalize text'''
    if text == "" or text == "''":
        return ""
    else:
        values = [r"\(", r"\)", r"-{2,}", r"\.{2,}", r"\"", "'"]
        for repl in values:
            text = re.sub(repl, "", text)

        values = ["/", "\\\\"]
        for repl in values:
            text = re.sub(repl, " ", text)

        return text

def is_roman(text):
    '''Check if text contains Roman numerals'''
    is_roman_bool = True
    for c in text:
        if c.upper() not in "IVXLCDM":
            is_roman_bool = False
    return is_roman_bool


def remove_duplicates(text):
    '''Remove duplicate words from text'''
    words = text.split()
    return (" ".join(sorted(set(words), key=words.index)))


def capitalize_model(text):
    '''Capitalize aircraft model'''
    temp = ""
    for word in text.split():
        is_alpha_hypen = all(c.isalpha() or c == '-' for c in word)
        if is_alpha_hypen and len(word) > 3 and not is_roman(word):
            temp = temp + word.title() + " "
        else:
            temp = temp + word + " "
    return temp


def capitalize_manufacturer(text):
    '''Capitalize manufacturer'''
    temp = ""
    for word in text.split():
        if len(word) < 3:
            temp = temp + word.upper() + " "
        else:
            temp = temp + word.title() + " "
    return temp


def make_pretty(text):
    '''Improve presentation of aircraft name'''

    # Remove values if not at start of string
    values = ["Aircraft","Aviation","International"]
    for value in values:
        text = re.sub(r"(?<!^)\s" + value + r"\s*", " ", text)

    # Remove everywhere
    values = ["Dba", "The", "Corporation", r"Corp\.?", "Company", r"Indust.*", r"Inc\.?", r"INC\.?",
        r"Ltd\.?","Limited", r"Co\.", r"Division\ Of", "Division", "Gmbh"]
    for value in values:
        text = re.sub(r"\s" + value + r"\s*", " ", text)

    # Miscellaneous name fixes
    text = re.sub(r"Dehavilland|De\ Havilland\ Canada|De\ Havilland", "DeHavilland", text, flags=re.IGNORECASE)
    text = re.sub(r"Canada Lp(\s|$)|Canada(\s|$)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"3017583", "", text) #Canada Inc
    text = re.sub(r"S\.A\.S\.?|Sas(\s|$)", "", text)
    text = re.sub(r"Atr(\s|$)", "ATR ", text)
    text = re.sub(r"Brm(\s|$)", "BRM ", text)
    text = re.sub(r"Let(\s|$)", "LET ", text)
    text = re.sub(r"Lot(\s|$)", "LOT ", text)
    text = re.sub(r"Lai(\s|$)", "LAI ", text)
    text = re.sub(r"Aai(\s|$)", "AAI ", text)
    text = re.sub(r"Iai(\s|$)", "IAI", text)
    text = re.sub(r"Fma(\s|$)", "FMA ", text)
    text = re.sub(r"Unc(\s|$)", "UNC ", text)
    text = re.sub(r"Tbm(\s|$)", "TBM ", text)
    text = re.sub(r"Itv(\s|$)", "ITV ", text)
    text = re.sub(r"Sas(\s|$)", "SAS ", text)
    text = re.sub(r"Raca(\s|$)", "RACA ", text)
    text = re.sub(r"S\.A\.N\.?|San(\s|$)", "SAN ", text)
    text = re.sub(r"S\.A\.I\.?|Sai(\s|$)", "SAI ", text)
    text = re.sub(r"C\.E\.A\.?|Cea(\s|$)", "CEA ", text)
    text = re.sub(r"-(\s|$)", " ", text)
    text = re.sub(r"([a-z]{3,})-([a-z]{3,})-([a-z]{3,})(\s|$)", r"\1 \2 \3 ", text, flags=re.IGNORECASE)
    text = re.sub(r"([a-z]{3,})-([a-z]{3,})(\s|$)", r"\1 \2 ", text, flags=re.IGNORECASE)
    text = re.sub("  ", " ", text)

    # Remove duplicate text and limit size
    text = remove_duplicates(text).strip()
    return text


def main():
    '''Main function'''
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
                # Handle bad data in original open sky csv file
                continue

            # No valid aircraft text
            if( b=="" and c=="" and d=="" ):
                continue

            # Concatenate elements
            aircraft = ""
            if b == "":
                aircraft = c + " " + d
            else:
                aircraft = b + " " + c + " " + d

            # Output processed entry to stdout
            aircraft = make_pretty(aircraft)
            if aircraft != "" :
                print(a + ',' + aircraft)

if __name__ == "__main__":
    main()
