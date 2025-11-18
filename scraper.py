from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_store(url, store_name):
    """Scrapuje promocje ze strony używając Playwright"""
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"\n--- Scraping {store_name} ---")
        print(f"Otwieranie: {url}")
        
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Czekamy aż pojawią się elementy promocji
            print("Czekanie na załadowanie promocji...")
            page.wait_for_selector("div.promo-book-const", timeout=10000)
            
            # Pobieramy HTML
            html = page.content()
            
            # Parsujemy za pomocą BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            items = soup.find_all("div", class_="promo-book-const")
            
            print(f"Znaleziono elementów: {len(items)}")
            
            # Ekstrahujemy dane z każdego elementu
            for i, item in enumerate(items[:3]):  # Bierz max 3 promocje
                try:
                    # Szukamy linku i ceny wewnątrz elementu
                    book_container = item.find("div", class_="book-of-day-container")
                    
                    if book_container:
                        title_elem = book_container.find("a")
                        price_elem = book_container.find("div", class_="book-of-day-price-info")
                        
                        title = title_elem.get_text(strip=True) if title_elem else f"Promocja {i+1}"
                        price = price_elem.get_text(strip=True) if price_elem else "Cena nieznana"
                        
                        promo_type = ["Książka Tygodnia", "Kurs Tygodnia", "Promocja"][i]
                        
                        results.append({
                            "store": store_name,
                            "type": promo_type,
                            "title": title,
                            "price": price,
                            "url": url
                        })
                        
                        print(f"  [{i+1}] {promo_type}: {title} - {price}")
                except Exception as e:
                    print(f"  Błąd przy ekstrakcji elementu {i}: {e}")
            
        except Exception as e:
            print(f"❌ Błąd przy ścielaniu {store_name}: {e}")
        
        finally:
            browser.close()
    
    return results

def main():
    print("=" * 60)
    print("SCRAPER PROMOCJI - POCZĄTEK")
    print("=" * 60)
    
    all_promotions = []
    
    # Scrapuj każdą stronę
    all_promotions.extend(scrape_store("https://helion.pl/", "Helion"))
    all_promotions.extend(scrape_store("https://onepress.pl/", "Onepress"))
    all_promotions.extend(scrape_store("https://ebookpoint.pl/", "Ebookpoint"))
    
    # Przygotuj dane do JSON-a
    data = {
        "updated": datetime.now().isoformat(),
        "total_promotions": len(all_promotions),
        "promotions": all_promotions
    }
    
    # Zapisz do pliku
    with open("promocje.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"✅ SUKCES! Zapisano {len(all_promotions)} promocji do promocje.json")
    print("=" * 60)

if __name__ == "__main__":
    main()
