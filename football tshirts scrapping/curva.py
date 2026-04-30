import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import yagmail
import datetime as dt
import os
import time

# -------------------- SCRAPER --------------------
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def scrapper():
    global name
    URL = "https://curvaegypt.com/about/top-products"
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    all_products_data = []
    MAX_PAGES_TO_SCRAPE = 10

    driver.get(URL)

    for page_num in range(1, MAX_PAGES_TO_SCRAPE + 1):
        driver.refresh()
        time.sleep(3)
        # الانتظار حتى تظهر المنتجات في الـ DOM
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "grid"))
        )

        # تمرير بسيط للتأكد من تحميل الصور (Lazy loading) إذا لزم الأمر
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/4);")
        time.sleep(1)

        # تحويل محتوى الصفحة الحالي إلى BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # البحث عن حاوية المنتجات
        products_containers = soup.find_all('div', class_='relative bg-gray-light rounded-lg overflow-hidden')

        print(f"Scraping page {page_num} | products found: {len(products_containers)}")

        for item in products_containers:
            # استخراج الاسم
            name_tag = item.find('p', class_='line-clamp-2')
            name = name_tag.get_text(strip=True) if name_tag else "N/A"

            # استخراج الأسعار
            price_container = item.find('div', class_='flex gap-4')

            # السعر الحالي (المخصم أو الأساسي)
            current_price_tag = price_container.find('span',
                                                     class_='text-[--primary-color]') if price_container else None
            current_price = current_price_tag.get_text(strip=True).replace('EGP', '') if current_price_tag else "0"

            # السعر الأصلي (قبل الخصم) إن وجد
            old_price_tag = item.find('div', class_='relative text-xl font-bold')
            old_price = old_price_tag.find('span').get_text(strip=True) if old_price_tag else None

            all_products_data.append({
                "name": name,
                "current_price": current_price,
                "original_price": old_price if old_price else current_price,
                "has_discount": old_price is not None,
            })

        if page_num < MAX_PAGES_TO_SCRAPE:
            try:
                # البحث عن زر الصفحة التالية والضغط عليه
                next_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Go to next page']"))
                )

                # حفظ اسم أول منتج للتأكد من تغير الصفحة
                first_product_name = name

                driver.execute_script("arguments[0].click();", next_btn)

                # الانتظار حتى يتغير محتوى الصفحة (تغير اسم أول منتج)
                WebDriverWait(driver, 10).until(
                    lambda d: d.find_element(By.CLASS_NAME, "line-clamp-2").text != first_product_name
                )
                time.sleep(1)
            except Exception as e:
                print(f"No more pages or error: {e}")
                break

    driver.quit()
    return pd.DataFrame(all_products_data)

# -------------------- WRITER --------------------
def writer(df):
    service_account_json = os.environ.get("GOOGLE_KEY_JSON")
    with open("key.json", "w") as f:
        f.write(service_account_json)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file("key.json", scopes=scopes)
    client = gspread.authorize(creds)

    today_ss = client.open("Curva Today Market State")
    today_sheet = today_ss.get_worksheet(0)
    today_sheet.clear()
    set_with_dataframe(today_sheet, df)

    archive_ss = client.open("Curva Market Day-to-Day State")
    today_str = dt.datetime.now().strftime("%Y-%m-%d")
    try:
        day_sheet = archive_ss.worksheet(today_str)
        day_sheet.clear()
    except gspread.WorksheetNotFound:
        day_sheet = archive_ss.add_worksheet(
            title=today_str,
            rows=str(len(df)+10),
            cols=str(len(df.columns)+5)
        )
    set_with_dataframe(day_sheet, df)

# -------------------- EMAIL --------------------
def email_notifier():
    app_password = os.environ.get("EMAIL_APP_PASSWORD")
    sender_email = "tamanabdullah9@gmail.com"
    receiver_email = "ramyalimahmoud@gmail.com"
    today_str = dt.datetime.now().strftime("%Y-%m-%d (%A)")
    message = f"""سلام عليكم ورحمة الله وبركاته
صباحو يابو الريم
هذا ايميل تلقائي
تم إضافة بيانات اليوم لموقع كورفا
اليوم: {today_str}
"""
    yag = yagmail.SMTP(sender_email, app_password)
    yag.send(
        to=receiver_email,
        subject="تحديث بيانات كورفا — إرسال تلقائي",
        contents=message
    )
    print("Email sent successfully!")

# -------------------- RUN PIPELINE --------------------
def run_pipeline():
    df = scrapper()
    writer(df)
    email_notifier()
    print("Pipeline finished successfully!")

if __name__ == "__main__":
    run_pipeline()
