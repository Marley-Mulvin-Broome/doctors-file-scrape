#!/usr/bin/env python3

from bs4 import BeautifulSoup
import xlsxwriter
import requests

from dataclasses import dataclass

root_url = "https://doctorsfile.jp"

# 複数の対象URL
urls = [
    "https://doctorsfile.jp/search/ms72_pv1169_pv1170_pv1171_pv1172_pv1173_pv1174_pv1175_pv1176_pv1177_pv1178_pv1179_pv1180_pv1181_pv1182_pv1183_pv1184_pv1185_pv1186_pv1187_pv1188_pv1189_pv1190_pv1191_pv1192_pv1193_pv1194_pv1195_pv1196_pv1197_pv1198_pv1199_pv1200_pv1201_pv1202_pv1203_pv1204/"
    ]

pages = [ 1 ]

@dataclass
class Hospital:
    name: str
    address: str
    phone: str
    station: str
    department: str

    def write_to_worksheet(self, worksheet, row):
        worksheet.write(f'A{row}', self.name)
        worksheet.write(f'B{row}', self.address)
        worksheet.write(f'C{row}', self.phone)
        worksheet.write(f'D{row}', self.station)
        worksheet.write(f'E{row}', self.department)

    def __str__(self):
        return f"{self.name}, {self.address}, {self.phone}, {self.station}, {self.department}"

    def __repr__(self):
        return self.__str__()

def scrape_data(url, worksheet, row):
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # `result__name`(病院名)と`result-data__list`(住所、電話番号、最寄り駅、科)を取得
    names = soup.find_all(class_='result__name')
    data_lists = soup.find_all(class_='result-data')

    # データを出力
    for name, data_list in zip(names, data_lists):
        name = name.get_text(strip=True)

        data_items = data_list.find_all('li')

        # 1 - 住所
        # 2 - 電話番号
        # 3 - 最寄り駅
        # 4 - 科
        if (len(data_items) < 4):
            print(f"Skippping {name}")
            continue

        address = data_items[0].get_text(strip=True)
        phone = data_items[1].get_text(strip=True)
        station = data_items[2].get_text(strip=True)
        department = data_items[3].get_text(strip=True)

        hospital = Hospital(name, address, phone, station, department)

        hospital.write_to_worksheet(worksheet, row)

        row += 1

        print("Scraped " + str(hospital))

    pages = soup.find_all(class_='pagination__number')

    try:
        for page in pages:
            page_number = page.get_text(strip=True)

            if page_number in pages or page.get('href') is None:
                continue

            pages.append(page_number)

            next_url = f"{root_url}{page['href']}"

            
            scrape_data(next_url, worksheet, row)
    except KeyboardInterrupt as e:
        return
    except Exception as e:
        print("Fuck " + e)
        return


workbook = xlsxwriter.Workbook('hospitals.xlsx')
worksheet = workbook.add_worksheet()

worksheet.write('A1', '病院名')
worksheet.write('B1', '住所')
worksheet.write('C1', '電話番号')
worksheet.write('D1', '最寄り駅')
worksheet.write('E1', '科')

# 各URLからデータをスクレイピング
for idx, url in enumerate(urls):
    try:
        scrape_data(url, worksheet, idx + 2)
    except KeyboardInterrupt as e:
        print("Exiting early...")
    except Exception as e:
        print("Fuck (2)" + e)

workbook.close()