import requests
from bs4 import BeautifulSoup, Comment
import argparse

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


def __build_abholungen(gemeinde, street, hausnr):
    url = "https://www.aha-region.de/abholtermine/abfuhrkalender/"

    ladeort = street.split("@")[0] + "-" + "{:04d}".format(int(hausnr))

    payload_2 = {
            'gemeinde': gemeinde,
            'strasse': street.replace(" ", "+"),
            'hausnr': hausnr,
            'hausnraddon': '',
            'ladeort': ladeort,
            'anzeigen': 'Suchen',
    }
    
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    response = requests.request("POST", url, headers=headers, data = payload_2)
    
    soup = BeautifulSoup(response.text, 'html.parser')

    return_object = {}
    
    for trash_type in ["Bioabfall", "Restabfall", "Papier", "Leichtverpackungen"]:
        return_object[trash_type] = []
        abholungen = soup.find("img", {"title": trash_type}).parent.parent.parent.select('tr > td')
        return_object[trash_type].append(abholungen[3].contents[1])
        return_object[trash_type].append(abholungen[3].contents[3])
        return_object[trash_type].append(abholungen[3].contents[5])

    return return_object

def get_abholungen(gemeinde, input_street, hausnr):
    raw_streets = get_streets(gemeinde, input_street[0])
    street = [ street for street in raw_streets if input_street in street ][0]

    return __build_abholungen(gemeinde, street, hausnr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get Abfuhrdaten from the AHA Website')
    parser.add_argument('--gemeinde', type=str, help='The name of the "Gemeinde"')
    parser.add_argument('--street', type=str, help='The name of the street')
    parser.add_argument('--hausnr', type=str, help='The number of the house.')
    parser.add_argument('--list-gemeinden', action='store_true', help='List all "Gemeinden"')
    parser.add_argument('--list-streets', type=str, help='Requires \'Gemeinde,Letter\', where Letter is the first letter of the street you want to find')
    args = parser.parse_args()

    if (args.list_gemeinden):
        for gemeinde in get_gemeinden():
            print(gemeinde)
    elif (args.list_streets):
        g = args.list_streets.split(",")[0]
        l = args.list_streets.split(",")[1]
        for street in get_streets(g, l):
            print(street)
    else:
        abholungen = get_abholungen(args.gemeinde, args.street, args.hausnr)
        for trash_type,dates in abholungen.items():
            print("=== " + trash_type + " ===")
            for date in dates:
                print("  " + date)