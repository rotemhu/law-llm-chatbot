import requests
from bs4 import BeautifulSoup
import csv

url = "https://he.wikisource.org/wiki/%D7%A1%D7%A4%D7%A8_%D7%94%D7%97%D7%95%D7%A7%D7%99%D7%9D_%D7%94%D7%A4%D7%AA%D7%95%D7%97"
headers = {"User-Agent": "Mozilla/5.0 (compatible; Scraper/1.0)"}
response = requests.get(url, headers=headers)

# Parse HTML
soup = BeautifulSoup(response.text, "lxml")

# Get the page title
print(soup.title.string)

#Get law names and links
root_url = 'https://he.wikisource.org'
law_html_elements = soup.select("dd a")
law_items = []
for l in law_html_elements:
    url = root_url + l['href']
    law_name = l.text
    law_items.append({'law_name': law_name, 'url': url})

#print them and storing in csv file
for item in law_items:
    print(f'name: {item.get("law_name")}, link: {item.get("url")}')

with open('output_dict.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['law_name', 'url'])
    writer.writeheader() # Writes the header row
    writer.writerows(law_items)