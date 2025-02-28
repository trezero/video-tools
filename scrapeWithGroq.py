import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

class NgeneaDocScraper:
    def __init__(self, base_url, output_dir="ngenea_hub_docs"):
        self.base_url = base_url
        self.output_dir = output_dir
        self.visited_urls = set()
        self.file_counter = 1
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def get_next_filename(self):
        """Generate the next incremental filename."""
        filename = f"ngenea_hub_docs_{self.file_counter:03d}.md"
        self.file_counter += 1
        return os.path.join(self.output_dir, filename)

    def save_content(self, url, title, content):
        """Save the extracted content to a Markdown file."""
        filepath = self.get_next_filename()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(f"**URL:** {url}\n\n")
            f.write(content)
        print(f"Saved: {filepath}")

    def format_as_markdown(self, soup):
        """Extract and format content as Markdown."""
        # Try to find the main content area, fallback to body if not found
        content_div = soup.find("div", class_="document") or soup.find("body") or soup
        if not content_div:
            return "No content found."

        markdown = []

        # Iterate through all meaningful elements
        for elem in content_div.find_all(recursive=True):  # Changed to recursive=True
            if elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(elem.name[1])
                markdown.append(f"{'#' * level} {elem.get_text(strip=True)}\n")
            elif elem.name == 'p':
                markdown.append(f"{elem.get_text(strip=True)}\n")
            elif elem.name == 'pre':
                code = elem.get_text(strip=True)
                markdown.append(f"```bash\n{code}\n```\n")
            elif elem.name == 'ul':
                for li in elem.find_all('li', recursive=False):
                    markdown.append(f"- {li.get_text(strip=True)}\n")
            elif elem.name == 'ol':
                for i, li in enumerate(elem.find_all('li', recursive=False), 1):
                    markdown.append(f"{i}. {li.get_text(strip=True)}\n")
            elif elem.name == 'table':
                markdown.append(self._table_to_markdown(elem))
            elif elem.name == 'div' and 'note' in elem.get('class', []):
                note_text = elem.get_text(strip=True)
                markdown.append(f"> **Note:** {note_text}\n")

        # Join lines and clean up excessive newlines
        return "\n".join(line for line in markdown if line.strip()) or "No meaningful content extracted."

    def _table_to_markdown(self, table):
        """Convert HTML table to Markdown."""
        rows = table.find_all('tr')
        if not rows:
            return ""
        
        markdown = []
        headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
        markdown.append("| " + " | ".join(headers) + " |")
        markdown.append("| " + " | ".join(["---"] * len(headers)) + " |")
        
        for row in rows[1:]:
            cells = [td.get_text(strip=True) for td in row.find_all('td')]
            if cells:
                markdown.append("| " + " | ".join(cells) + " |")
        
        return "\n".join(markdown) + "\n"

    def scrape_page(self, url, title_prefix=""):
        """Scrape a single page and follow its links."""
        if url in self.visited_urls:
            print(f"Skipping already visited URL: {url}")
            return
        self.visited_urls.add(url)
        print(f"Scraping new URL: {url} with prefix '{title_prefix}'")

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract the page title
            title_tag = soup.find("h1")
            page_title = title_tag.get_text(strip=True) if title_tag else "Untitled"
            full_title = f"{title_prefix}{page_title}" if title_prefix else page_title

            # Format content as Markdown
            content = self.format_as_markdown(soup)
            self.save_content(url, full_title, content)

            # Find all links within the content area
            content_div = soup.find("div", class_="document") or soup.find("body") or soup
            links = content_div.find_all("a", href=True)
            for link in links:
                href = link.get("href")
                link_text = link.get_text(strip=True)
                if not href or "#" in href or (href.startswith("http") and "ngeneahub/v2.5.3/admin_guide" not in href):
                    continue

                full_url = urljoin(url, href)
                if full_url.startswith("https://docs.arcapix.com/ngeneahub/v2.5.3/admin_guide"):
                    if full_url not in self.visited_urls:  # Double-check before queuing
                        new_prefix = f"{title_prefix}{link_text} - "
                        print(f"Following link: {full_url} ({link_text})")
                        time.sleep(1)  # Polite delay
                        self.scrape_page(full_url, new_prefix)
                    else:
                        print(f"Link already visited, skipping: {full_url}")

        except requests.RequestException as e:
            print(f"Failed to scrape {url}: {e}")

    def run(self):
        """Start the scraping process."""
        print(f"Starting scrape from {self.base_url}")
        self.scrape_page(self.base_url)
        print(f"Scraping complete. Files saved in {self.output_dir}")

if __name__ == "__main__":
    base_url = "https://docs.arcapix.com/ngeneahub/v2.5.3/admin_guide/index.html"
    scraper = NgeneaDocScraper(base_url)
    scraper.run()