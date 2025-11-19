from playwright.sync_api import sync_playwright
import json
from datetime import datetime

def scrape_store_debug(url, store_name):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("\n--- DEBUG: " + store_name + " ---")
        print("Opening: " + url)
        
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            print("Page loaded!")
            
            page.wait_for_timeout(5000)
            
            html = page.content()
            
            filename = "debug_" + store_name.lower() + ".html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            
            print("Saved HTML to " + filename + " (" + str(len(html)) + " chars)")
            
            page.screenshot(path="debug_" + store_name.lower() + ".png")
            print("Saved screenshot")
            
            promo_elements = page.query_selector_all("[class*='promo']")
            print("Found " + str(len(promo_elements)) + " elements with promo")
            
            book_elements = page.query_selector_all("[class*='book']")
            print("Found " + str(len(book_elements)) + " elements with book")
            
        except Exception as e:
            print("Error: " + str(e))
        
        finally:
            browser.close()

def main():
    print("=" * 60)
    print("SCRAPER DEBUG MODE")
    print("=" * 60)
    
    scrape_store_debug("https://helion.pl/", "Helion")
    scrape_store_debug("https://onepress.pl/", "Onepress")
    scrape_store_debug("https://ebookpoint.pl/", "Ebookpoint")
    
    data = {
        "updated": datetime.now().isoformat(),
        "total_promotions": 0,
        "promotions": [],
        "note": "Debug mode"
    }
    
    with open("promocje.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("DEBUG COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
