#!/usr/bin/env python3
# scrapeToRag.py - Web scraper for RAG workflows using FireCrawl
# Usage: python scrapeToRag.py <url>

import os
import sys
import argparse
import time
import logging
import re
import json
from datetime import datetime
from firecrawl import FirecrawlApp
from urllib.parse import urlparse
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def setup_arg_parser():
    """Set up and return the argument parser."""
    parser = argparse.ArgumentParser(
        description='Scrape a website and generate well-formatted text for RAG workflows'
    )
    parser.add_argument('url', help='URL of the website to scrape')
    parser.add_argument(
        '--output-dir', 
        default='outputs',
        help='Directory to save the output file (default: outputs)'
    )
    parser.add_argument(
        '--max-urls', 
        type=int, 
        default=100,
        help='Maximum number of links to crawl (default: 100)'
    )
    parser.add_argument(
        '--api-key',
        help='FireCrawl API key (can also be set with FIRECRAWL_API_KEY environment variable)'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--formats',
        default=['markdown'],
        nargs='+',
        choices=['markdown', 'html', 'rawHtml', 'links', 'screenshot', 'extract', 'json'],
        help='Output format(s) for scraped content (default: markdown)'
    )
    parser.add_argument(
        '--wait',
        type=int,
        default=60,
        help='Maximum time in seconds to wait for crawl completion (default: 60)'
    )
    return parser

def get_domain(url):
    """Extract the domain from a URL."""
    parsed_url = urlparse(url)
    return parsed_url.netloc

def get_output_filename(url):
    """Generate a filename based on the URL and current timestamp."""
    domain = get_domain(url)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{domain.replace('.', '_')}_{timestamp}.txt"

def clean_text(text):
    """Clean the text content for better readability."""
    if not text:
        return ""
        
    # Replace multiple newlines with double newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Replace multiple spaces with single space
    text = re.sub(r' {2,}', ' ', text)
    
    # Remove any remaining problematic characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    return text.strip()

def crawl_website(url, max_urls, api_key, formats, wait_time, verbose):
    """Crawl the website using FireCrawl API."""
    if verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug(f"Starting to crawl: {url}")
    
    # Set up FireCrawl
    if not api_key:
        api_key = os.getenv('FIRECRAWL_API_KEY')
        if not api_key:
            logger.error("No API key provided. Please set the FIRECRAWL_API_KEY environment variable or provide it with --api-key.")
            return None
    
    logger.info(f"Initializing FireCrawl for {url}")
    
    try:
        # Create FireCrawl instance
        app = FirecrawlApp(api_key=api_key)
        
        # Configure crawl parameters
        params = {
            'crawlerOptions': {
                'limit': max_urls,
                'maxDepth': 3,  # Maximum crawl depth
                'mode': 'default'  # Use default mode for better accuracy
            },
            'pageOptions': {
                'onlyMainContent': True,  # Extract only the main content
                'replaceAllPathsWithAbsolutePaths': True  # Make all links absolute
            }
        }
        
        if formats:
            if 'html' in formats:
                params['pageOptions']['includeHtml'] = True
            if 'rawHtml' in formats:
                params['pageOptions']['includeRawHtml'] = True
        
        if verbose:
            logger.debug(f"Crawl parameters: {json.dumps(params, indent=2)}")
        
        # Execute the crawl
        logger.info("Starting the crawl...")
        try:
            # Try to use the synchronous version first with wait_until_done
            logger.info("Using synchronous crawl with timeout...")
            crawl_result = app.crawl_url(
                url, 
                params=params,
                wait_until_done=True,
                timeout=wait_time  # Maximum time to wait in seconds
            )
            
            if verbose:
                logger.debug(f"Crawl result: {json.dumps(crawl_result, indent=2)}")
                
            # Check if the result contains data
            if 'data' in crawl_result and crawl_result['data']:
                logger.info(f"Crawl completed successfully with {len(crawl_result['data'])} pages.")
                return crawl_result['data']
            else:
                logger.error(f"Crawl completed but no data found in result: {json.dumps(crawl_result, indent=2)}")
                return None
                
        except Exception as e:
            logger.error(f"Synchronous crawl failed: {str(e)}")
            logger.info("Falling back to asynchronous crawl...")
            
            # Fall back to asynchronous version
            try:
                # Start the asynchronous crawl
                crawl_status = app.crawl_url(url, params=params, wait_until_done=False)
                
                if verbose:
                    logger.debug(f"Initial crawl status: {json.dumps(crawl_status, indent=2)}")
                
                # Get the crawl ID
                job_id = crawl_status.get('jobId')
                
                if not job_id:
                    logger.error(f"No job ID in response: {json.dumps(crawl_status, indent=2)}")
                    return None
                    
                logger.info(f"Crawl started with job ID: {job_id}")
                
                # Poll for crawl status until completed or timed out
                total_wait_time = 0
                poll_interval = 5  # seconds
                
                while total_wait_time < wait_time:
                    time.sleep(poll_interval)
                    total_wait_time += poll_interval
                    
                    status = app.check_crawl_status(job_id)
                    
                    if verbose:
                        logger.debug(f"Current status after {total_wait_time}s: {json.dumps(status, indent=2)}")
                    
                    if status.get('status') == 'completed':
                        logger.info("Crawl completed successfully!")
                        if 'data' in status and status['data']:
                            return status['data']
                        else:
                            logger.error(f"No data found in completed crawl: {json.dumps(status, indent=2)}")
                            return None
                        
                    elif status.get('status') == 'failed':
                        logger.error(f"Crawl failed: {status.get('error', 'Unknown error')}")
                        return None
                        
                    logger.info(f"Crawl in progress... ({total_wait_time}s/{wait_time}s)")
                
                logger.warning(f"Crawl timed out after {wait_time} seconds.")
                return None
                
            except Exception as e:
                logger.error(f"Error during async crawl: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                return None
        
    except Exception as e:
        logger.error(f"Error during crawl setup: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def format_content(crawl_results):
    """Format the crawled content for RAG."""
    if not crawl_results:
        return ""
    
    formatted_content = []
    
    for page_data in crawl_results:
        url = page_data.get('url', 'Unknown URL')
        
        # Try to get the title from different possible locations
        title = None
        if 'title' in page_data:
            title = page_data['title']
        elif 'metadata' in page_data and 'title' in page_data['metadata']:
            title = page_data['metadata']['title']
        
        title = title or "No Title"
        
        # Get content from the available formats
        content = None
        for format_type in ['markdown', 'html', 'text']:
            if format_type in page_data:
                content = page_data[format_type]
                break
        
        content = clean_text(content or "No content found for this page.")
        
        # Add section header
        formatted_content.append(f"# {title}")
        formatted_content.append(f"URL: {url}")
        formatted_content.append("")
        
        # Add content
        formatted_content.append(content)
        formatted_content.append("")
        formatted_content.append("-" * 80)
        formatted_content.append("")
    
    return '\n'.join(formatted_content)

def save_content(content, output_dir, filename):
    """Save the formatted content to a file."""
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")
    
    output_path = os.path.join(output_dir, filename)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Successfully saved content to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error saving content to {output_path}: {e}")
        return None

def main():
    """Main entry point of the script."""
    parser = setup_arg_parser()
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    logger.info(f"Starting to scrape: {args.url}")
    start_time = time.time()
    
    # Crawl the website
    results = crawl_website(args.url, args.max_urls, args.api_key, args.formats, args.wait, args.verbose)
    
    if not results:
        logger.error("Crawling failed. No content retrieved.")
        return 1
    
    # Format the content
    logger.info("Formatting content for RAG...")
    formatted_content = format_content(results)
    
    # Generate output filename and save content
    output_filename = get_output_filename(args.url)
    output_path = save_content(formatted_content, args.output_dir, output_filename)
    
    if not output_path:
        logger.error("Failed to save the content.")
        return 1
    
    elapsed_time = time.time() - start_time
    logger.info(f"Process completed in {elapsed_time:.2f} seconds.")
    logger.info(f"Output saved to: {output_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())