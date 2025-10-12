import pandas as pd
import time
from camoufox.sync_api import Camoufox

# Input CSV with restaurant links (single column: URL)
INPUT_CSV = "new_data.csv"
# Output CSV with ratings and votes
OUTPUT_CSV = "zomato_dining_ratings.csv"

# CSS selectors from your screenshots
RATING_SELECTOR = "div.sc-1q7bklc-1.cILgox"
VOTES_SELECTOR = "div.sc-1q7bklc-8.kEgyiI"

def extract_dining_rating_votes(page):
    """Extract dining rating and votes using given selectors."""
    rating, votes = "", ""
    try:
        rating_el = page.query_selector(RATING_SELECTOR)
        votes_el = page.query_selector(VOTES_SELECTOR)

        if rating_el:
            rating = rating_el.inner_text().strip()

        if votes_el:
            votes = votes_el.inner_text().strip().replace(",", "")
    except Exception as e:
        print("Error extracting rating/votes:", e)

    return rating, votes

def main():
    # Load restaurant URLs
    df = pd.read_csv(INPUT_CSV , encoding='latin1')
    urls = df[df.columns[0]].dropna().tolist()

    results = []

    # Launch Camoufox browser
    with Camoufox(headless=True) as browser:
        page = browser.new_page()
        for idx, url in enumerate(urls, 1):
            print(f"[{idx}/{len(urls)}] Scraping: {url}")
            try:
                page.goto(url, timeout=60000)
                time.sleep(2)  # wait for JS content to load

                rating, votes = extract_dining_rating_votes(page)
                results.append({"URL": url, "Dining_Rating": rating, "Votes": votes})
            except Exception as e:
                print(f"Error on {url}: {e}")
                results.append({"URL": url, "Dining_Rating": "", "Votes": ""})

            time.sleep(1.5)  # avoid detection

    # Save results to CSV
    pd.DataFrame(results).to_csv(OUTPUT_CSV, index=False)
    print(f"Scraping complete. Data saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
