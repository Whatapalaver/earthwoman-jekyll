import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
import os
import time
import html2text

def get_snapshots_after_date(url, date_after):
    """Get Wayback Machine snapshots after a certain date"""
    # Fetch the calendar page
    cdx_url = f"https://web.archive.org/cdx/search/cdx?url={url}&output=json&from={date_after}&collapse=timestamp:6"
    response = requests.get(cdx_url)
    if response.status_code != 200:
        print(f"Failed to get snapshots: {response.status_code}")
        return []
    
    try:
        data = response.json()
        # Skip header row
        snapshots = data[1:]
        # Extract timestamps and URLs
        return [(item[1], item[2]) for item in snapshots]
    except Exception as e:
        print(f"Error parsing snapshots: {e}")
        return []

def extract_post_content(wayback_url):
    """Extract post content from a Wayback Machine URL"""
    try:
        response = requests.get(wayback_url)
        if response.status_code != 200:
            print(f"Failed to get page: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title - adjust selector based on your WordPress theme
        title_elem = soup.select_one('.entry-title, .post-title, h1.title')
        if not title_elem:
            return None
        title = title_elem.get_text().strip()
        
        # Extract date - adjust selector based on your WordPress theme
        date_elem = soup.select_one('.entry-date, .post-date, .date')
        post_date = date_elem.get_text().strip() if date_elem else None
        
        # Extract content - adjust selector based on your WordPress theme
        content_elem = soup.select_one('.entry-content, .post-content, .content')
        if not content_elem:
            return None
        content = content_elem.prettify()
        
        return {
            'title': title,
            'date': post_date,
            'content': content
        }
    except Exception as e:
        print(f"Error extracting content: {e}")
        return None

def create_markdown_file(post, output_dir="_posts"):
    """Create a Jekyll markdown file from post data"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.body_width = 0
    h.unicode_snob = True
    
    # Parse date and create slug
    try:
        date_obj = datetime.strptime(post['date'], "%B %d, %Y")
        date_str = date_obj.strftime("%Y-%m-%d")
    except:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    slug = post['title'].lower().replace(' ', '-')
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    
    filename = f"{date_str}-{slug[:50]}.md"
    filepath = os.path.join(output_dir, filename)
    
    # Convert HTML content to markdown
    content = h.handle(post['content'])
    
    # Create frontmatter
    frontmatter = f"""---
layout: post
title: "{post['title']}"
date: {post['date']}
categories: [posts]
---

{content}"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter)
    
    print(f"Created: {filepath}")
    return filepath

def main():
    domain = "earthwoman.co.uk"
    date_after = "20121104"  # Start from day after your last post
    
    print(f"Fetching snapshots after {date_after}...")
    snapshots = get_snapshots_after_date(domain, date_after)
    print(f"Found {len(snapshots)} snapshots")
    
    # Extract individual post URLs from the snapshots
    post_urls = []
    for timestamp, url in snapshots:
        wayback_url = f"https://web.archive.org/web/{timestamp}/{url}"
        print(f"Processing: {wayback_url}")
        
        # Get the page
        response = requests.get(wayback_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find post links - adjust selector based on your WordPress theme
            links = soup.select('.post-title a, .entry-title a')
            for link in links:
                if 'href' in link.attrs:
                    post_url = link['href']
                    # Convert to wayback URL if needed
                    if not post_url.startswith('https://web.archive.org'):
                        archive_url = f"https://web.archive.org/web/{timestamp}/{post_url}"
                        post_urls.append(archive_url)
        
        # Be kind to the Wayback Machine
        time.sleep(1)
    
    print(f"Found {len(post_urls)} post URLs")
    
    # Extract and save each post
    for url in post_urls:
        print(f"Extracting: {url}")
        post_data = extract_post_content(url)
        if post_data:
            create_markdown_file(post_data)
        # Be kind to the Wayback Machine
        time.sleep(1)

if __name__ == "__main__":
    main()