__author__ = "jdanek"

import logging
import sqlite3
from pathlib import Path


# Global Vars 
SCRIPT_DIR = Path(__file__).parent.resolve()
DB_VRADARSERVER_ROUTE = "./data/vradarserver-route.db"
DB_VRADARSERVER_AIRPORT = "./data/vradarserver-airport.db"

# Init logger
logger = logging.getLogger("flight_tracks")

country_dict = {
    "AD":"Andorra", "AE":"UAE", "AF":"Afghanistan", "AG":"Antigua", "AI":"Anguilla", "AL":"Albania", "AM":"Armenia", "AO":"Angola", "AQ":"Antarctica", 
    "AR":"Argentina", "AS":"American Samoa", "AT":"Austria", "AU":"Australia", "AW":"Aruba", "AZ":"Azerbaijan", "BA":"Bosnia", "BB":"Barbados", "BD":"Bangladesh", 
    "BE":"Belgium", "BF":"Burkina Faso", "BG":"Bulgaria", "BH":"Bahrain", "BI":"Burundi", "BJ":"Benin", "BL":"Saint Barthélemy", "BM":"Bermuda", "BN":"Brunei", "BO":"Bolivia", 
    "BQ":"Caribbean Netherlands", "BR":"Brazil", "BS":"Bahamas", "BT":"Bhutan", "BW":"Botswana", "BY":"Belarus", "BZ":"Belize", "CA":"Canada", "CC":"Cocos Islands", 
    "CD":"Kinshasa", "CF":"African Republic", "CG":"Brazzaville", "CH":"Switzerland", "CI":"Côte d'Ivoire", "CK":"Cook Islands", "CL":"Chile", "CM":"Cameroon", 
    "CN":"China", "CO":"Colombia", "CR":"Costa Rica", "CU":"Cuba", "CV":"Cape Verde", "CW":"Curaçao", "CX":"Christmas Island", "CY":"Cyprus", "CZ":"Czech Republic", "DE":"Germany", 
    "DJ":"Djibouti", "DK":"Denmark", "DM":"Dominica", "DO":"Dominican Republic", "DZ":"Algeria", "EC":"Ecuador", "EE":"Estonia", "EG":"Egypt", "EH":"Western Sahara", "ER":"Eritrea", 
    "ES":"Spain", "ET":"Ethiopia", "FI":"Finland", "FJ":"Fiji", "FK":"Falkland Islands", "FM":"Micronesia", "FO":"Faroe Islands", "FR":"France", "GA":"Gabon", "GB":"United Kingdom", 
    "GD":"Grenada", "GE":"Georgia", "GF":"French Guiana", "GG":"Guernsey", "GH":"Ghana", "GI":"Gibraltar", "GL":"Greenland", "GM":"Gambia", "GN":"Guinea", "GP":"Guadeloupe", 
    "GQ":"Equatorial Guinea", "GR":"Greece", "GS":"Sandwich Islands", "GT":"Guatemala", "GU":"Guam", "GW":"Guinea-Bissau", "GY":"Guyana", "HK":"Hong Kong", 
    "HN":"Honduras", "HR":"Croatia", "HT":"Haiti", "HU":"Hungary", "ID":"Indonesia", "IE":"Ireland", "IL":"Israel", "IM":"Isle of Man", "IN":"India", "IO":"British Indian Ocean", 
    "IQ":"Iraq", "IR":"Iran", "IS":"Iceland", "IT":"Italy", "JE":"Jersey", "JM":"Jamaica", "JO":"Jordan", "JP":"Japan", "KE":"Kenya", "KG":"Kyrgyzstan", "KH":"Cambodia", "KI":"Kiribati", 
    "KM":"Comoros", "KN":"Saint Kittss", "KP":"North Korea", "KR":"South Korea", "KS":"Kosovo", "KW":"Kuwait", "KY":"Cayman Islands", "KZ":"Kazakhstan", "LA":"Laos", "LB":"Lebanon", 
    "LC":"Saint Lucia", "LI":"Liechtenstein", "LK":"Sri Lanka", "LR":"Liberia", "LS":"Lesotho", "LT":"Lithuania", "LU":"Luxembourg", "LV":"Latvia", "LY":"Libya", "MA":"Morocco", "MC":"Monaco", 
    "MD":"Moldova", "ME":"Montenegro", "MF":"Saint Martin", "MG":"Madagascar", "MH":"Marshall Islands", "MK":"Macedonia", "ML":"Mali", "MM":"Myanmar", "MN":"Mongolia", "MO":"Macau", 
    "MP":"Mariana Islands", "MQ":"Martinique", "MR":"Mauritania", "MS":"Montserrat", "MT":"Malta", "MU":"Mauritius", "MV":"Maldives", "MW":"Malawi", "MX":"Mexico", "MY":"Malaysia", 
    "MZ":"Mozambique", "NA":"Namibia", "NC":"New Caledonia", "NE":"Niger", "NF":"Norfolk Island", "NG":"Nigeria", "NI":"Nicaragua", "NL":"Netherlands", "NO":"Norway", "NP":"Nepal", "NR":"Nauru", 
    "NU":"Niue", "NZ":"New Zealand", "OM":"Oman", "PA":"Panama", "PE":"Perú", "PF":"French Polynesia", "PG":"Papua New Guinea", "PH":"Philippines", "PK":"Pakistan", "PL":"Poland", 
    "PM":"Saint Pierre", "PN":"Pitcairn", "PR":"Puerto Rico", "PS":"Palestinian Territory", "PT":"Portugal", "PW":"Palau", "PY":"Paraguay", "QA":"Qatar", "RE":"Réunion", 
    "RO":"Romania", "RS":"Serbia", "RU":"Russia", "RW":"Rwanda", "SA":"Saudi Arabia", "SB":"Solomon Islands", "SC":"Seychelles", "SD":"Sudan", "SE":"Sweden", "SG":"Singapore", 
    "SH":"Saint Helena", "SI":"Slovenia", "SK":"Slovakia", "SL":"Sierra Leone", "SM":"San Marino", "SN":"Senegal", "SO":"Somalia", "SR":"Suriname", "SS":"South Sudan", "ST":"São Tomé", 
    "SV":"El Salvador", "SX":"Sint Maarten", "SY":"Syria", "SZ":"Swaziland", "TC":"Turks and Caicos", "TD":"Chad", "TF":"French Territories", "TG":"Togo", "TH":"Thailand", 
    "TJ":"Tajikistan", "TK":"Tokelau", "TL":"Timor-Leste", "TM":"Turkmenistan", "TN":"Tunisia", "TO":"Tonga", "TR":"Turkey", "TT":"Trinidad and Tobago", "TV":"Tuvalu", "TW":"Taiwan", 
    "TZ":"Tanzania", "UA":"Ukraine", "UG":"Uganda", "UM":"US Minor Islands", "US":"United States", "UY":"Uruguay", "UZ":"Uzbekistan", "VA":"Vatican City", 
    "VC":"Saint Vincent", "VE":"Venezuela", "VG":"British Virgin Islands", "VI":"US Virgin Islands", "VN":"Viet Nam", "VU":"Vanuatu", "WF":"Wallis and Futuna", 
    "WS":"Samoa", "XA":"ICAO", "XB":"NATO", "XC":"Netherlands Antilles", "YE":"Yemen", "YT":"Mayotte", "ZA":"South Africa", "ZM":"Zambia", "ZW":"Zimbabwe", "ZZ":""
 }


def remove_duplicates(str) -> str:
    words = str.split("-")
    result = "-".join(sorted(set(words), key=words.index))
    logger.debug(f"remove_duplicates: str: %s, result: %s", str, result)
    return result


def get_route(country_code, call_sign) -> tuple:
    # lookup route based on icao24 value
    logger.debug(f"get_route: call_sign: %s", call_sign)
    start_airport = "n/a"
    start_location = "n/a"
    end_airport = "n/a"
    end_location = "n/a"

    if not call_sign or len(call_sign) < 2:
        return start_airport, start_location, end_airport, end_location
    
    # connect to Route database
    conn = sqlite3.connect(SCRIPT_DIR / DB_VRADARSERVER_ROUTE)
    cursor = conn.cursor()

    cursor.execute("SELECT AirportCodes FROM route WHERE Callsign = ?", (call_sign,))
    row = cursor.fetchone()
    if row:
        route = row[0]      
        # dedupe route list and save starting and ending airports
        deduped = remove_duplicates(route)
        airport = deduped.split("-")
        start_airport = airport[0]
        end_airport = airport[-1]
    conn.close()

    #  convert ICAO to IATA airport code (if available) 
    if start_airport != "n/a" and end_airport != "n/a":
        # connect to Airport database
        conn = sqlite3.connect(SCRIPT_DIR / DB_VRADARSERVER_AIRPORT)
        cursor = conn.cursor()

        # starting airport
        cursor.execute("SELECT IATA, Location, CountryISO2 FROM airport WHERE ICAO = ?", (start_airport,))
        row = cursor.fetchone()
        if row:
            if row[0] and len(row[0]) > 1:
                start_airport =  row[0]  

             # get location (city) and country of airport
            if row[1] and row[2]:
                start_location = row[1]
                if row[2] != country_code:
                    try:
                        country = country_dict[row[2]]
                        start_location = start_location + ", " + country
                    except KeyError:
                        start_location =start_location

        # ending airport
        cursor.execute("SELECT IATA, Location, CountryISO2 FROM airport WHERE ICAO = ?", (end_airport,))
        row = cursor.fetchone()
        if row:
            if row[0] and len(row[0]) > 1:
                end_airport =  row[0]  

             # get location (city) and country of airport
            if row[1] and row[2]:
                end_location = row[1]
                if row[2] != country_code:
                    try:
                        country = country_dict[row[2]]
                        end_location = end_location + ", " + country
                    except KeyError:
                        end_location = end_location

        conn.close()
    
    logger.debug(f"get_route: start_airport: %s, start_location: %s, end_airport: %s, end_location: %s", start_airport, start_location, end_airport, end_location)
    return start_airport, start_location, end_airport, end_location

