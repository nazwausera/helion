from playwright.sync_api import sync_playwright
import json
from datetime import datetime

def scrape_store_debug(url, store_name):
    """Scrapuje stronę i zapisuje HTML do debugowania"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"
--- DEBUG: {store_name} ---")
        print(f"Otwieranie: {url}")
        
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            print("Strona załadowana!")
            
            # Poczekaj 5 sekund, żeby JS się załadował
            page.wait_for_timeout(5000)
            
            # Pobierz cały HTML
            html = page.content()
            
            # Zapisz HTML do pliku
            filename = f"debug_{store_name.lower()}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            
            print(f"✅ Zapisano HTML do {filename} ({len(html)} znaków)")
            
            # Zrób screenshot
            page.screenshot(path=f"debug_{store_name.lower()}.png")
            print(f"✅ Zapisano screenshot do debug_{store_name.lower()}.png")
            
            # Spróbuj znaleźć dowolne elementy z "promo" w klasie
            promo_elements = page.query_selector_all("[class*='promo']")
            print(f"Znaleziono {len(promo_elements)} elementów z 'promo' w klasie")
            
            # Spróbuj znaleźć elementy z "book" w klasie
            book_elements = page.query_selector_all("[class*='book']")
            print(f"Znaleziono {len(book_elements)} elementów z 'book' w klasie")
            
        except Exception as e:
            print(f"❌ Błąd: {e}")
        
        finally:
            browser.close()

def main():
    print("=" * 60)
    print("SCRAPER DEBUG MODE")
    print("=" * 60)
    
    scrape_store_debug("https://helion.pl/", "Helion")
    scrape_store_debug("https://onepress.pl/", "Onepress")
    scrape_store_debug("https://ebookpoint.pl/", "Ebookpoint")
    
    # Zapisz pusty JSON na razie
    data = {
        "updated": datetime.now().isoformat(),
        "total_promotions": 0,
        "promotions": [],
        "note": "Debug mode - sprawdź pliki debug_*.html"
    }
    
    with open("promocje.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("
" + "=" * 60)
    print("✅ DEBUG ZAKOŃCZONY - sprawdź pliki debug_*.html i debug_*.png")
    print("=" * 60)

if __name__ == "__main__":
    main()
