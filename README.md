# AHPI

This is a small Python Script/Library which helps getting the next trash pickups from the Website of Aha (also known as "Zweckverband Abfallwirtschaft Region Hannover")

**Important: This script can break as soon as aha changes it's website! **

# Usage

The script expects the following parameters
```
--help                                             
usage: ahpi.py [-h] [--gemeinde GEMEINDE] [--street STREET] [--hausnr HAUSNR]
               [--list-gemeinden] [--list-streets LIST_STREETS]

Get Abfuhrdaten from the AHA Website

optional arguments:
  -h, --help            show this help message and exit
  --gemeinde GEMEINDE   The name of the "Gemeinde"
  --street STREET       The name of the street
  --hausnr HAUSNR       The number of the house.
  --list-gemeinden      List all "Gemeinden"
  --list-streets LIST_STREETS
                        Requires 'Gemeinde,Letter', where Letter is the first letter of the
                        street you want to find
```

The simplest usage is the following:
```
python3 ahpi.py --gemeinde Hannover --street "Hildesheimer Str." --hausnr 123
```
It's important that you use the right street name! You can check it by either looking it up at https://www.aha-region.de/abholtermine/abfuhrkalender/, or by using this functionality from the script:
```
python3 ahpi.py --list-streets 'Hannover,H'
```
This will return entrys in the following format:
```
...
01299@Heusingerstr. / Ledeburg@Ledeburg
...
```
In this case "Heusingerstr." is the right street name you should use. The script will show indefinable errors in case something is wrong.
