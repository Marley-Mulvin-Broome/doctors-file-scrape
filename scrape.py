#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor

from bs4 import BeautifulSoup
import xlsxwriter
import requests
from atomics import atomic, INT

from hospital_factory import HospitalFactory

root_url = "https://doctorsfile.jp"
output_file = "hospitals.xlsx"

# 複数の対象URL
urls = [
    "https://doctorsfile.jp/search/ms1/"
    ]

visited_pages = { 1: "" }

all_hospitals = []

current_hospitals = atomic(width=4, atype=INT)
max_hospitals = atomic(width=4, atype=INT)

def get_progress_bar(current_value, max_value, progress_width) -> str:
    progress = current_value / max_value
    filled_width = int(progress * progress_width)
    bar = '#' * filled_width + '-' * (progress_width - filled_width)
    percentage = int(progress * 100)
    return f"{current_value}/{max_value} [{bar}] {percentage}%"


def scrape_data(url, thread_pool):
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    page_info = HospitalFactory.from_html(soup, root_url)

    # Thread safe bc only writing, not reading data which may be written at the same time
    all_hospitals.extend(page_info.hospitals)

    max_hospitals.store(page_info.total_count)

    current_hospitals.add(len(page_info.hospitals))

    print(get_progress_bar(current_hospitals.load(), max_hospitals.load(), 10), end="\r")

    for page in page_info.pages_links:
        if page[0] in visited_pages.keys():
            continue
        
        visited_pages[page[0]] = page[1]

        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.submit(scrape_data, page[1], executor)

        executor.shutdown(wait=True)


# 各URLからデータをスクレイピング
for idx, url in enumerate(urls):
    try:
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.submit(scrape_data, url, executor)

            executor.shutdown(wait=True)

    except KeyboardInterrupt as e:
        print("Exiting early...")

print(f"Writing to '{output_file}'")

workbook = xlsxwriter.Workbook('hospitals.xlsx')
worksheet = workbook.add_worksheet()

worksheet.write('A1', '病院名')
worksheet.write('B1', '住所')
worksheet.write('C1', '電話番号')
worksheet.write('D1', '最寄り駅')
worksheet.write('E1', '科')

for idx, hospital in enumerate(all_hospitals):
    hospital.write_to_worksheet(worksheet, idx + 1)

workbook.close()