import re
import os
from datetime import datetime
import html
import html2text

def extract_posts():
    with open('sql_backup.sql', 'r', encoding='utf-8', errors='replace') as file:
        sql_content = file.read()
    
    # Find all INSERT statements for posts table - be more flexible with table names
    insert_pattern = r"INSERT INTO [`']?(?:earth_posts|wp_posts|posts)[`']? VALUES\s*\((.*?)\);"
    matches = re.findall(insert_pattern, sql_content, re.DOTALL)
    
    print(f"Found {len(matches)} total INSERT statements")
    
    posts = []
    for match_idx, match in enumerate(matches):
        try:
            # Parse the values carefully to handle quoted strings properly
            values = []
            in_quote = False
            current_value = ""
            escaped = False
            
            for char in match:
                if escaped:
                    current_value += char
                    escaped = False
                elif char == '\\':
                    current_value += char
                    escaped = True
                elif char == "'" and not in_quote:
                    in_quote = True
                    current_value += char
                elif char == "'" and in_quote:
                    in_quote = False
                    current_value += char
                elif char == ',' and not in_quote:
                    values.append(current_value.strip())
                    current_value = ""
                else:
                    current_value += char
            
            if current_value:
                values.append(current_value.strip())
            
            # Print sample values to debug
            if match_idx == 0:
                print(f"Sample values from first record (found {len(values)} fields):")
                for i, val in enumerate(values):
                    print(f"  {i}: {val[:50]}...")
            
            # Ensure we have enough values
            if len(values) < 21:
                print(f"Skipping post with insufficient fields: {len(values)}")
                continue
            
            # Clean up values - try to be flexible with field positions
            post_id = values[0].strip()
            post_date = values[2].strip("'")
            post_content = values[4].strip("'").replace("\\'", "'")
            post_title = values[5].strip("'").replace("\\'", "'")
            post_status = values[8].strip("'")
            
            # Check different positions for post_type
            if len(values) > 20:
                post_type = values[21].strip("'")
            else:
                # Try to determine post type another way
                post_type = 'post'  # Default to post
            
            print(f"Record {match_idx}: ID={post_id}, Title={post_title[:30]}..., Type={post_type}, Status={post_status}")
            
            # Be more flexible: include all published content that looks like a post
            if post_status == 'publish' and post_title and post_content:
                posts.append({
                    'id': post_id,
                    'title': html.unescape(post_title),
                    'content': html.unescape(post_content),
                    'date': post_date,
                    'type': post_type,
                    'status': post_status
                })
                print(f"✅ Added post: {post_title[:30]}...")
        except Exception as e:
            print(f"Error processing post {match_idx}: {str(e)}")
    
    print(f"Found {len(posts)} valid posts")
    
    # Group by title and keep only the latest
    posts_by_title = {}
    for post in posts:
        title = post['title']
        if title not in posts_by_title or post['date'] > posts_by_title[title]['date']:
            posts_by_title[title] = post
    
    return list(posts_by_title.values())

def create_markdown_files(posts):
    # Create output directory
    output_dir = "_posts"
    os.makedirs(output_dir, exist_ok=True)
    
    # Configure HTML to Markdown converter
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.body_width = 0  # Don't wrap lines
    h.unicode_snob = True
    
    for post in posts:
        # Convert HTML content to markdown
        content = h.handle(post['content'])
        
        # Format the date and create a slug
        try:
            date_obj = datetime.strptime(post['date'], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # Try alternate date format
            try:
                date_obj = datetime.strptime(post['date'], "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                date_obj = datetime.now()  # Fallback
        
        formatted_date = date_obj.strftime("%Y-%m-%d")
        slug = post['title'].lower().replace(' ', '-')
        slug = re.sub(r'[^a-z0-9-]', '', slug)[:50]  # Limit slug length
        
        # Create the filename
        filename = f"{formatted_date}-{slug}.md"
        
        # Create the Jekyll frontmatter
        frontmatter = f"""---
layout: post
title: "{post['title']}"
date: {post['date']}
categories: [posts]
---

{content}"""
        
        # Write the file
        file_path = os.path.join(output_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter)
        
        print(f"Created: {file_path}")

if __name__ == "__main__":
    posts = extract_posts()
    create_markdown_files(posts)
    print(f"Extracted {len(posts)} unique posts to the _posts directory")