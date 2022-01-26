import requests
from bs4 import BeautifulSoup, Comment
import argparse
import re

def get_gemeinden():
    url = "https://www.aha-region.de/abholtermine/abfuhrkalender"
    response = requests.request("GET", url)
    soup = BeautifulSoup(response.text, 'html.parser')

    gemeinden_raw = soup.find("select", {"id": "gemeinde", "name": "gemeinde"}).findAll("option")
    gemeinden = [ gemeinde.get("value") for gemeinde in gemeinden_raw ]

    return gemeinden

def get_streets(gemeinde, start_letter):
    url = "https://www.aha-region.de/abholtermine/abfuhrkalender"
    if (start_letter == 'Z'):
        end_letter = '['
    else:
        end_letter = chr(ord(start_letter)+1)

    payload = {
            'gemeinde': gemeinde,
            'von': start_letter,
            'bis': end_letter,
    }
    
    response = requests.request("GET", url, params=payload)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    streets_raw = soup.find("select", {"id": "strasse", "name": "strasse"}).findAll("option")
    streets = [ street.get("value") for street in streets_raw ]
    
    return streets

def get_loadingplaces(gemeinde, street, hausnr):
    url = "https://www.aha-region.de/abholtermine/abfuhrkalender"
    payload = {
            'gemeinde': gemeinde,
            'strasse': street,
            'hausnr': hausnr,
    }

    response = requests.request("GET", url, params=payload)
    soup = BeautifulSoup(response.text, 'html.parser')

    ladeplatz_raw = soup.find("select", {"name": "ladeort"}).findAll("option")
    ladeplaces = [ { "id": ladeplatz.get("value"), "name": ladeplatz.get_text() } for ladeplatz in ladeplatz_raw ]

    return ladeplaces

def __build_abholungen(gemeinde, street, hausnr, loading_place):
    url = "https://www.aha-region.de/abholtermine/abfuhrkalender/"

    if (not loading_place):
        ladeort = street.split("@")[0] + "-" + "{:04d}".format(int(hausnr))
    else:
        ladeort = loading_place + "+"

    payload = {
            'gemeinde': gemeinde,
            'jsaus': '',
            'strasse': street.replace(" ", "+"),
            'hausnr': hausnr,
            'hausnraddon': '',
            'ladeort': ladeort,
            'anzeigen': 'Suchen',
    }
    
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded'
    }

    # We need this hack, because requests replaces our dear @ and + with percent-encoding
    payload_str = "&".join("%s=%s" % (k,v) for k,v in payload.items())
    response = requests.request("POST", url, headers=headers, params=payload_str)

    soup = BeautifulSoup(response.text, 'html.parser')

    return_object = {}

    for trash_type in ["Bioabfall", "Restabfall", "Papier", "Leichtverpackungen"]:
        return_object[trash_type] = []
        try:
            abholungen = soup.find("img", {"title": trash_type}).parent.parent.next_sibling.next_sibling.select('tr > td')
        except AttributeError:
            continue
        return_object[trash_type].append(abholungen[1].contents[1])
        return_object[trash_type].append(abholungen[1].contents[3])
        return_object[trash_type].append(abholungen[1].contents[5])

    return return_object

def get_abholungen(input_gemeinde, input_street, hausnr, loading_place):
    gemeinde = input_gemeinde.lower().capitalize()
    raw_streets = get_streets(gemeinde, input_street[0])
    matching_streets = [
        street
        for street in raw_streets
        if re.search(input_street, street, re.IGNORECASE)
    ]
    matching_streets_count = len(matching_streets)
    street = (
        matching_streets[0]
        if matching_streets_count == 1
        else (
            usage_error("No matching street found")
            if matching_streets_count == 0
            else usage_error("Street is ambigous: " + ", ".join(matching_streets))
        )
    )

    return __build_abholungen(gemeinde, street, hausnr, loading_place)

def usage_error(msg):
    raise Exception(msg)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get Abfuhrdaten from the AHA Website')
    parser.add_argument('--gemeinde', type=str, help='The name of the "Gemeinde"')
    parser.add_argument('--street', type=str, help='The name of the street')
    parser.add_argument('--hausnr', type=str, help='The number of the house.')
    parser.add_argument('--loading-place', default="", type=str, help='The id of the loading place.')
    parser.add_argument('--json', action="store_true", required=False, help='Output the results as json')
    parser.add_argument('--list-gemeinden', action='store_true', help='List all "Gemeinden"')
    parser.add_argument('--list-streets', type=str, help='Requires \'Gemeinde,Letter\', where Letter is the first letter of the street you want to find')
    parser.add_argument('--list-loadingplaces', type=str, help='Requires \'Gemeinde, Street, Hausnr\'. Use the output from list-gemeinden and list-streets :)')
    args = parser.parse_args()

    if (args.list_gemeinden):
        for gemeinde in get_gemeinden():
            print(gemeinde)
    elif (args.list_streets):
        g = args.list_streets.split(",")[0]
        l = args.list_streets.split(",")[1]
        for street in get_streets(g, l):
            print(street)
    elif (args.list_loadingplaces):
        g = args.list_loadingplaces.split(",")[0]
        streets = args.list_loadingplaces.split(",")[1]
        hausnr = args.list_loadingplaces.split(",")[2]
        for loadingplace in get_loadingplaces(g, streets, hausnr):
            print("Id: " + loadingplace["id"])
            print("Name: " + loadingplace["name"])
            print("---")
    else:
        abholungen = get_abholungen(args.gemeinde, args.street, args.hausnr, args.loading_place)
        if args.json:
            print(abholungen)
        else:
            for trash_type,dates in abholungen.items():
                print("=== " + trash_type + " ===")
                for date in dates:
                    print("  " + date)
