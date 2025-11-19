from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def extract_price(text):
    match = re.search(r'(\d+[,.]\d{2})\s*zl', text)
    if match:
        return match.group(1)
    return None

def extract_promotions(html, store_name):
    soup = BeautifulSoup(html, 'html.parser')
    promotions = []
    
    try:
        links = soup.find_all('a', limit=10)
        
        for link in links:
            text = link.get_text(strip=True)
            
            if len(text) > 5 and text not in ['', 'o nas', 'kontakt', 'pomoc']:
                parent = link.parent
                if parent:
                    parent_text = parent.get_text()
                    price = extract_price(parent_text)
                    
                    if price:
                        promotions.append({
                            'store': store_name,
                            'title': text[:100],
                            'price': price,
                            'url': link.get('href', '')
                        })
        
        if not promotions:
            all_text = soup.get_text()
            lines = all_text.split('\n')
            
            for i, line in enumerate(lines[:20]):
                if extract_price(line):
                    title_line = ''
                    for j in range(max(0, i-5), i):
                        if len(lines[j].strip()) > 5:
                            title_line = lines[j].strip()
                            break
                    
                    if title_line:
                        promotions.append({
                            'store': store_name,
                            'title': title_line[:100],
                            'price': extract_price(line),
                            'url': ''
                        })
        
        return promotions[:3]
        
    except Exception as e:
        print('Error: ' + str(e))
        return []

def scrape_store(url, store_name):
    promotions = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print('\n--- Scraping ' + store_name + ' ---')
        print('Opening: ' + url)
        
        try:
            page.goto(url, wait_until='networkidle', timeout=30000)
            print('Page loaded!')
            page.wait_for_timeout(3000)
            html = page.content()
            promos = extract_promotions(html, store_name)
            print('Found ' + str(len(promos)) + ' promotions')
            promotions = promos
            
        except Exception as e:
            print('Error: ' + str(e))
        
        finally:
            browser.close()
    
    return promotions

def main():
    print('=' * 60)
    print('SCRAPER PROMOCJI')
    print('=' * 60)
    
    all_promotions = []
    all_promotions.extend(scrape_store('https://helion.pl/', 'Helion'))
    all_promotions.extend(scrape_store('https://onepress.pl/', 'Onepress'))
    all_promotions.extend(scrape_store('https://ebookpoint.pl/', 'Ebookpoint'))
    
    data = {
        'updated': datetime.now().isoformat(),
        'total_promotions': len(all_promotions),
        'promotions': all_promotions
    }
    
    with open('promocje.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print('\n' + '=' * 60)
    print('SUCCESS! Saved ' + str(len(all_promotions)) + ' promotions')
    print('=' * 60)

if __name__ == '__main__':
    main()
