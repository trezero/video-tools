import requests
from bs4 import BeautifulSoup

# Send a GET request to the LinkedIn page
url = "https://www.linkedin.com/company/purestorage/people/"
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

# Find all the people on the page
people = soup.find_all("div", class_="pv-top-card-section__name")

# Extract the names and titles
names_and_titles = []
for person in people:
    name = person.find("span", class_="name").text.strip()
    title = person.find("span", class_="title").text.strip()
    names_and_titles.append((name, title))

# Print the extracted data
for name, title in names_and_titles:
    print(f"{name} - {title}")