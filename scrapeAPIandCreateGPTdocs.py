import requests
from bs4 import BeautifulSoup

def scrape_monday_api_docs(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Example: Extracting headings and paragraphs
        # This is a simple extraction and will need to be customized based on the actual structure of the webpage
        content = []
        for header in soup.find_all(['h1', 'h2', 'h3', 'p']):
            content.append({
                'tag': header.name,
                'text': header.get_text(strip=True)
            })

        return content
    except requests.RequestException as e:
        return str(e)

# URL of the Monday.com API documentation
url = 'https://developer.monday.com/apps/docs/mondayapi'
api_docs = scrape_monday_api_docs(url)

# Printing the first few elements for demonstration
print(api_docs[:5])
