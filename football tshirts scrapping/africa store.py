import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
import pandas as pd
import yagmail
import datetime as dt
import os
import requests
from bs4 import BeautifulSoup


def scrapper():
    url = "https://www.africastoreas.com/products?data_from=best-selling"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return pd.DataFrame()

    soup = BeautifulSoup(response.content, "html.parser")
    products_container = soup.find("div", {"id": "filtered-products"})

    if not products_container:
        return pd.DataFrame()

    product_divs = products_container.find_all("div", class_="product")
    all_products_data = []

    for product in product_divs:
        title_tag = product.find("h6", class_="product__title")
        title = title_tag.get_text(strip=True) if title_tag else "N/A"

        price_tag = product.find("ins", class_="product__new-price")
        price = price_tag.get_text(strip=True).replace('EGP', '').strip() if price_tag else "0"

        link_tag = product.find("a", class_="text-capitalize")
        link = link_tag["href"] if link_tag else "N/A"

        all_products_data.append({
            "name": title,
            "current_price": price,
        })

    return pd.DataFrame(all_products_data)


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

    today_ss = client.open("Africa Store Today Market State")
    today_sheet = today_ss.get_worksheet(0)
    today_sheet.clear()
    set_with_dataframe(today_sheet, df)

    archive_ss = client.open("Africa Store Market Day-to-Day State")
    today_str = dt.datetime.now().strftime("%Y-%m-%d")
    try:
        day_sheet = archive_ss.worksheet(today_str)
        day_sheet.clear()
    except gspread.WorksheetNotFound:
        day_sheet = archive_ss.add_worksheet(
            title=today_str,
            rows=str(len(df) + 10),
            cols=str(len(df.columns) + 5)
        )
    set_with_dataframe(day_sheet, df)


def email_notifier():
    app_password = os.environ.get("EMAIL_APP_PASSWORD")
    sender_email = "tamanabdullah9@gmail.com"
    receiver_email = "ramyalimahmoud@gmail.com"
    sheet_link = "https://docs.google.com/spreadsheets/d/1P6vXn7emLrnfwxLeL9J3QMRN7LYBARrkHkOhMwZD0Bg/edit?usp=sharing"
    today_str = dt.datetime.now().strftime("%Y-%m-%d (%A)")

    message = f"""سلام عليكم ورحمة الله وبركاته
صباحو يابو الريم
هذا ايميل تلقائي
تم إضافة بيانات اليوم لموقع Africa Store
اليوم: {today_str}
رابط الملف: {sheet_link}
"""
    yag = yagmail.SMTP(sender_email, app_password)
    yag.send(
        to=receiver_email,
        subject="تحديث بيانات Africa Store — إرسال تلقائي",
        contents=message
    )
    print("Email sent successfully!")


def run_pipeline():
    df = scrapper()
    print(df)
    if not df.empty:
        writer(df)
        email_notifier()
        print("Pipeline finished successfully!")
    else:
        print("No data scraped.")


if __name__ == "__main__":
    run_pipeline()