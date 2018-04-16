import ssl
import csv
from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime

# How we store rating data
class ratingEntry:
    artist = None
    album = None
    personal_rating = None

    def __init__(self,**kwargs):
        for k,v in kwargs.items():
            setattr(self,k,v)

    def __str__(self):
        return "{} - {} ({})".format(self.artist,self.album,self.personal_rating)

    # For CSV parsing
    def toList(self):
        return [
            self.artist,
            self.album,
            self.personal_rating
        ]

    # Return scores on varying scales, where the num represents the max score
    def rating5(self):
        return self.personal_rating
    def rating10(self):
        return self.personal_rating*2
    def rating100(self):
        return (self.personal_rating*2)*10
    def rating(self):
        return (self.personal_rating*2)/10

# Formats dates for filenames
def formatDate(s):
    day = datetime.today()
    return ("{}-{}-{}-".format(day.month,day.day,day.year))+s

# Writes error log if there are issues initializing a rating entry during scrape
def errorLog(re,num):
    errors = []
    # Collect errors
    if not re.artist:
        errors.append("Error scraping artist {}".format(num))
    if not re.album:
        errors.append("Error scraping album {}".format(num))
    if not re.personal_rating:
        errors.append("Error scraping album {}".format(num))
    # Record errors
    if errors:
        filedir = "./data/"
        filename = formatDate("errors")
        extension = ".txt"
        with open(filedir+filename+extension, "w+") as error_log:
            error_log.write("ERRORS:")
            for errorMessage in errors:
                error_log.write(errorMessage)

# Initializes BeautifulSoup from given link w/ no SSL certification requirement
def getContent(page_url):
    page_html = urlopen(page_url,context=ssl._create_unverified_context())
    page_content = BeautifulSoup(page_html, "html.parser")

    return page_content

# Creates RE from personal rating entry info
def getRE(entry):
    data = {}
    data["artist"] = entry.td.a.font.contents[0].strip()
    data["album"] = entry.td.a.font.contents[1].text.strip()
    data["personal_rating"] = float(entry.contents[-1].text.strip())

    return ratingEntry(**data)

# Returns list of ratingEntries
def scrape(page_content):
    # Declarations
    data = []
    # Scrape page
    table = page_content.find("table", class_="tableborder")
    iteration = 0
    for entry in table.contents:
        re = getRE(entry)
        data.append(re)
        errorLog(re,iteration)
        iteration += 1

    return data

# Writes scraped ratingEntries to csv file
def writeData(data):
    filedir = "./data/"
    filename = formatDate("sputscrape")
    extension = ".csv"
    with open(filedir+filename+extension, "w+") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["ARTIST","ALBUM","PERSONAL RATING"])
        for re in data:
            writer.writerow(re.toList())

def main():
    page_content = getContent("https://www.sputnikmusic.com/uservote.php?sort=1&memberid=855429")
    data = scrape(page_content)
    writeData(data)

main()