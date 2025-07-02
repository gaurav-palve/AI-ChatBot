import re

def extract_url_from_text(text):
    url_match = re.search(r'https?://[^\s)]+', text)
    return url_match.group(0) if url_match else None