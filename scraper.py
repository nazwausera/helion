from playwright.sync_api import sync_playwright
import json
from datetime import datetime

def scrape_store_debug(url, store_name):
    """Debug scraping function"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"
--- DEBUG: {store_name} ---")
        print(f"Opening: {url}")
        
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            print("Page loaded!")
            
            # Wait 5 seconds for JS to load
            page.wait_for_timeout(5000)
            
            # Get full HTML
            html = page.content()
            
            # Save HTML to file
            filename = f"debug_{store_name.lower()}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            
            print(f"Saved HTML to {filename} ({len(html)} chars)")
            
            # Take screenshot
            page.screenshot(path=f"debug_{store_name.lower()}.png")
            print(f"Saved screenshot to debug_{store_name.lower()}.png")
            
            # Try to find any elements with 'promo' in class
            promo_elements = page.query_selector_all("[class*='promo']")
            print(f"Found {len(promo_elements)} elements with 'promo' in class")
            
            # Try to find elements with 'book' in class
            book_elements = page.query_selector_all("[class*='book']")
            print(f"Found {len(book_elements)} elements with 'book' in class")
            
        except Exception as e:
            print(f"Error: {e}")
        
        finally:
            browser.close()

def main():
    print("=" * 60)
    print("SCRAPER DEBUG MODE")
    print("=" * 60)
    
    scrape_store_debug("https://helion.pl/", "Helion")
    scrape_store_debug("https://onepress.pl/", "Onepress")
    scrape_store_debug("https://ebookpoint.pl/", "Ebookpoint")
    
    # Save empty JSON for now
    data = {
        "updated": datetime.now().isoformat(),
        "total_promotions": 0,
        "promotions": [],
        "note": "Debug mode - check debug_*.html files"
    }
    
    with open("promocje.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("
" + "=" * 60)
    print("DEBUG COMPLETE - check debug_*.html and debug_*.png files")
    print("=" * 60)

if __name__ == "__main__":
    main()
