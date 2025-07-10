def strip_html(html):
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html)

# Add more helpers as needed
