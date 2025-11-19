from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def extract_promotions(html, store_name):
    soup = BeautifulSoup(html, 'html.parser')
    promotions = []
    
    try:
        full_text = soup.get_text()
        lines = full_text.split('\n')
        
        # Szukaj każdej linii zawierającej cenę w formacie XXX.XX zł lub XXX,XX zł
        price_pattern = r'(\d+[,.]\d{2})\s*zl'
        
        found_prices = []
        for i, line in enumerate(lines):
            # Szukaj ceny bieżącej (bez ~ znaków)
            if re.search(r'^\s*\d+[,.]\d{2}\s*zl\s*$', line):
                # To jest linia TYLKO z ceną
                found_prices.append((i, line.strip()))
        
        # Dla każdej znalezionej ceny - pobierz tytuł
        for idx, (line_num, price) in enumerate(found_prices[:5]):  # Max 5 promocji
            # Szukaj tytułu kilka linii wyżej
            title = ''
            for j in range(max(0, line_num-20), line_num):
                line_content = lines[j].strip()
                # Szukaj linii, która wygląda na tytuł (nie zawiera symboli, ma sensowną długość)
                if (len(line_content) > 10 and 
                    len(line_content) < 150 and
                    line_content not in ['- Druk', '- PDF + ePub + Mobi'] and
                    'zl' not in line_content and
                    'zl' not in line_content and
                    '~~' not in line_content):
                    title = line_content
            
            if title:
                # Wyczyść cenę
                clean_price = price.replace(',', '.').strip()
                
                promotions.append({
                    'store': store_name,
                    'title': title[:100],
                    'price': clean_price,
                    'url': ''
                })
        
        return promotions
        
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
            for promo in promos:
                print('  - ' + promo['title'][:50] + ': ' + promo['price'])
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
