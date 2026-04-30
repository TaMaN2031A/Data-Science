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
    url = "https://iii-amigos.com/collections/all?sort_by=best-selling"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return pd.DataFrame()

    soup = BeautifulSoup(response.content, "html.parser")
    product_cards = soup.find_all("hdt-card-product")

    all_products_data = []

    for card in product_cards:
        title_tag = card.find("a", class_="hdt-card-product__title")
        title = title_tag.get_text(strip=True) if title_tag else "N/A"

        reg_price_tag = card.find("hdt-compare-at-price")
        reg_price = reg_price_tag.find("span", class_="hdt-money").get_text(strip=True).replace('LE',
                                                                                                '').strip() if reg_price_tag else "N/A"

        sale_price_tag = card.find("hdt-price")
        sale_price = sale_price_tag.find("span", class_="hdt-money").get_text(strip=True).replace('LE',
                                                                                                  '').strip() if sale_price_tag else "N/A"

        sold_out_badge = card.find("hdt-badge", attrs={"is": "sold_out"})
        status = "Sold Out" if (sold_out_badge or "hdt-pr-sold_out" in card.get("class", [])) else "In Stock"

        size_elements = card.find_all("span", class_="hdt-size-list-item")
        available_sizes = [s.get_text(strip=True) for s in size_elements if not s.has_attr("unavailable")]
        sizes_str = ", ".join(available_sizes) if available_sizes else "None"

        all_products_data.append({
            "Name": title,
            "Regular Price": reg_price,
            "Sale Price": sale_price,
            "Status": status,
            "Available Sizes": sizes_str
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

    spreadsheet_id = "1Xvb0sdDFJcqNzsA7b22uG_Bn1jz7aMgSz18uVfiv3xM"
    archive_ss = client.open_by_key(spreadsheet_id)
    today_str = dt.datetime.now().strftime("%Y-%m-%d")

    try:
        day_sheet = archive_ss.worksheet(today_str)
        day_sheet.clear()
    except gspread.WorksheetNotFound:
        day_sheet = archive_ss.add_worksheet(
            title=today_str,
            rows=str(len(df) + 20),
            cols="10"
        )
    set_with_dataframe(day_sheet, df)


def email_notifier():
    app_password = os.environ.get("EMAIL_APP_PASSWORD")
    sender_email = "tamanabdullah9@gmail.com"
    receiver_email = "ramyalimahmoud@gmail.com"
    sheet_link = "https://docs.google.com/spreadsheets/d/1Xvb0sdDFJcqNzsA7b22uG_Bn1jz7aMgSz18uVfiv3xM/edit?usp=sharing"
    today_str = dt.datetime.now().strftime("%Y-%m-%d (%A)")

    message = f"""سلام عليكم ورحمة الله وبركاته
صباحو يابو الريم
هذا ايميل تلقائي
تم إضافة بيانات اليوم لموقع iii-amigos
اليوم: {today_str}
رابط الملف: {sheet_link}
"""
    yag = yagmail.SMTP(sender_email, app_password)
    yag.send(
        to=receiver_email,
        subject="تحديث بيانات iii-amigos — إرسال تلقائي",
        contents=message
    )


def run_pipeline():
    df = scrapper()
    if not df.empty:
        writer(df)
        email_notifier()
    else:
        print("No data scraped.")


if __name__ == "__main__":
    run_pipeline()