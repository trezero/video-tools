# ScrapeToRag

A Python utility for scraping websites and generating well-formatted content for Retrieval Augmented Generation (RAG) workflows.

## Overview

ScrapeToRag is a command-line tool that scrapes web pages from a given URL, follows links within the same domain and path, and formats the extracted content in a clean format suitable for RAG applications. It uses FireCrawl to handle the crawling and content extraction, making it particularly effective for documentation sites.

## Features

- Crawls web pages starting from a given URL and follows links within the same domain
- Extracts titles and content while maintaining document structure
- Formats the extracted content for optimal use in RAG workflows
- Configurable number of URLs to crawl
- Output is saved to text files with clear delineation between pages

## Installation

1. Clone this repository or download the script.
2. Install the required dependencies:

```bash
pip install -r requirements_scrapeToRag.txt
```

3. Make sure you have a FireCrawl API key. You can sign up for one at [FireCrawl Website](https://firecrawl.dev/).

## Environment Variables

You can set the following environment variables in a `.env` file or your shell:

- `FIRECRAWL_API_KEY`: Your FireCrawl API key

## Usage

Basic usage:

```bash
python scrapeToRag.py https://docs.example.com
```

Advanced options:

```bash
python scrapeToRag.py https://docs.example.com --output-dir my_outputs --max-urls 50 --verbose
```

### Command Line Arguments

- `url`: URL of the website to scrape (required)
- `--output-dir`: Directory to save the output file (default: `outputs`)
- `--max-urls`: Maximum number of URLs to crawl (default: 100)
- `--api-key`: FireCrawl API key (can also be set with FIRECRAWL_API_KEY environment variable)
- `--formats`: Output format(s) for scraped content: 'markdown', 'html', 'rawHtml', 'links', 'screenshot', 'extract', or 'json' (default: markdown)
- `--wait`: Maximum time in seconds to wait for crawl completion (default: 60)
- `--verbose`: Enable verbose logging

## Output Format

The output is saved as a text file in the specified output directory (default: `outputs/`). The filename is derived from the domain of the URL and the current timestamp.

Each page in the output file is formatted as follows:

```
# Page Title
URL: https://example.com/page

Page content here...

--------------------------------------------------------------------------------

# Next Page Title
URL: https://example.com/next-page

Next page content here...

--------------------------------------------------------------------------------
```

## Examples

### Scraping Documentation Site

```bash
python scrapeToRag.py https://docs.python.org/3/tutorial/ --max-urls 20
```

### Setting API Key

```bash
export FIRECRAWL_API_KEY=your_api_key_here
python scrapeToRag.py https://docs.example.com
```

Or provide it directly:

```bash
python scrapeToRag.py https://docs.example.com --api-key your_api_key_here
```

## Limitations

- FireCrawl requires an API key which may have usage limits
- Some websites may block or rate-limit crawlers
- The output format is optimized for text-based RAG systems

## Troubleshooting

If you encounter issues:

1. Make sure your FireCrawl API key is valid
2. Check if the website allows crawling and isn't blocking your requests
3. For very large sites, consider limiting the crawl with `--max-urls` option
4. Enable verbose logging with `--verbose` to see detailed logs
