"""
Cambridge Dictionary API scraper to fetch IPA pronunciation and audio URLs
"""

import requests
from bs4 import BeautifulSoup
import re
import os

def fetch_cambridge_data(word):
    """
    Fetch pronunciation (IPA) and audio URLs from Cambridge Dictionary
    Returns: dict with ipa_us, ipa_uk, audio_us, audio_uk
    """
    # Cambridge Dictionary URL
    url = f"https://dictionary.cambridge.org/dictionary/english/{word.lower().strip()}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # Clear environment proxy settings to prevent interference
    session = requests.Session()
    session.trust_env = False  # Ignore system proxy settings
    
    try:
        response = session.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"[Cambridge API] HTTP {response.status_code} for '{word}'")
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        result = {
            'ipa_us': None,
            'ipa_uk': None,
            'audio_us': None,
            'audio_uk': None
        }
        
        # Find pronunciation sections
        pos_header = soup.find('div', class_='pos-header')
        if not pos_header:
            return None
        
        # Get UK pronunciation
        uk_pron = pos_header.find('span', class_='uk')
        if uk_pron:
            ipa_uk = uk_pron.find('span', class_='ipa')
            if ipa_uk:
                result['ipa_uk'] = ipa_uk.get_text(strip=True)
            
            # Get UK audio
            audio_uk = uk_pron.find('source', attrs={'type': 'audio/mpeg'})
            if audio_uk and audio_uk.get('src'):
                audio_url = audio_uk.get('src')
                if audio_url.startswith('//'):
                    audio_url = 'https:' + audio_url
                elif audio_url.startswith('/'):
                    audio_url = 'https://dictionary.cambridge.org' + audio_url
                result['audio_uk'] = audio_url
        
        # Get US pronunciation
        us_pron = pos_header.find('span', class_='us')
        if us_pron:
            ipa_us = us_pron.find('span', class_='ipa')
            if ipa_us:
                result['ipa_us'] = ipa_us.get_text(strip=True)
            
            # Get US audio
            audio_us = us_pron.find('source', attrs={'type': 'audio/mpeg'})
            if audio_us and audio_us.get('src'):
                audio_url = audio_us.get('src')
                if audio_url.startswith('//'):
                    audio_url = 'https:' + audio_url
                elif audio_url.startswith('/'):
                    audio_url = 'https://dictionary.cambridge.org' + audio_url
                result['audio_us'] = audio_url
        
        # Return result if at least one field is populated
        if any(result.values()):
            return result
        
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"[Cambridge API] Network error for '{word}': {str(e)}")
        return None
    except Exception as e:
        print(f"[Cambridge API] Unexpected error for '{word}': {str(e)}")
        return None


def fetch_pronunciation_data(word, skip_fetch=False):
    """
    Main function to fetch pronunciation data
    First tries Cambridge, can be extended with other sources
    
    Args:
        word: The word to fetch pronunciation for
        skip_fetch: If True, skip external API calls (for servers without internet)
    """
    if skip_fetch:
        print(f"[Cambridge API] Skipping fetch for '{word}' (disabled)")
        return {
            'ipa_us': None,
            'ipa_uk': None,
            'audio_us': None,
            'audio_uk': None
        }
    
    print(f"[Cambridge API] Attempting to fetch data for: {word}")
    cambridge_data = fetch_cambridge_data(word)
    
    if cambridge_data and any(cambridge_data.values()):
        print(f"[Cambridge API] Success - Found pronunciation data")
        return cambridge_data
    
    print(f"[Cambridge API] No data found, returning empty")
    # Could add fallback to other dictionaries here
    return {
        'ipa_us': None,
        'ipa_uk': None,
        'audio_us': None,
        'audio_uk': None
    }
