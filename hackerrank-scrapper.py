import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIG ---
CONTEST_URL = "https://www.hackerrank.com/contests/cse-28072025/judge/submissions/"
TOTAL_PAGES = 75
OUTPUT_FILE = "hackerrank_contest_report.xlsx"

# --- SETUP SELENIUM ---
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# --- STEP 1: Login manually (only first time) ---
driver.get("https://www.hackerrank.com/auth/login")
print("\n Please log in manually using Google. Once logged in and redirected, press Enter here...")
input("   Waiting for manual login...")

# --- STEP 2: Scrape all pages ---
all_data = []

for page in range(1, TOTAL_PAGES + 1):
    print(f"🔄 Scraping page {page} of {TOTAL_PAGES}...")
    driver.get(f"{CONTEST_URL}{page}")
    time.sleep(3)  # Wait for page to fully load

    # soup = BeautifulSoup(driver.page_source, "html.parser")
    # submissions = soup.select(".judge-submissions-list-view")
    rows = driver.find_elements(By.CSS_SELECTOR, "div.submissions_item")
    # print(rows)
    for row in rows:
        try:
            problem = row.find_element(By.CSS_SELECTOR, 'div.span2.submissions-title a.challenge-slug').text.strip()
            team = row.find_elements(By.CSS_SELECTOR, 'div.span2.submissions-title a.challenge-slug')[1].text.strip()
            id_text = row.find_element(By.CSS_SELECTOR, 'div.span1.submissions-title p').text.strip()
            lang = row.find_elements(By.CSS_SELECTOR, 'div.span2.submissions-title p.small')[0].text.strip()
            time_taken = row.find_elements(By.CSS_SELECTOR, 'div.span2.submissions-title p.small')[1].text.strip()
            status = row.find_element(By.CSS_SELECTOR, 'div.span3.submissions-title p.small').text.strip()
            result_raw = row.find_elements(By.CSS_SELECTOR, 'div.span1.submissions-title p.small')[0].text.strip()

            all_data.append({
                "Problem": problem,
                "Team": team,
                "ID": id_text,
                "Language": lang,
                "Time": time_taken,
                "Score": result_raw,
                "Status": status
            })
        except Exception as e:
            print("⚠️ Error parsing a row:", e)
            continue

# --- STEP 3: Export to Excel ---
df = pd.DataFrame(all_data)
df.to_excel(OUTPUT_FILE, index=False)
print(f"\n✅ Report saved as '{OUTPUT_FILE}' with {len(df)} rows.")

# --- Clean up ---
driver.quit()
