from typing import Tuple
from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag

from hospital import Hospital

@dataclass
class PageInfo:
    hospitals: list[Hospital]
    pages_links: list[Tuple[int, str]]
    total_count: int


class HospitalFactory:
    @staticmethod
    def from_html(soup: BeautifulSoup, root_url: str) -> PageInfo:
        total_results = 0

        try:
            total_results = int(soup.find(class_="search__count").find("strong").get_text(strip=True).replace(',', ''))
        except Exception as e: 
            print("Failed getting total results " + repr(e))

        result_tags = soup.find_all(class_="result")

        hospitals = []

        for result_tag in result_tags:
            hospitals.append(HospitalFactory.from_result_tag(result_tag))

        page_tags = soup.find_all("a", class_="pagination__number")

        pages = []

        for page_tag in page_tags:
            # Current page, and others that don't have links are useless
            if page_tag.get('href') is None:
                continue

            page_number = int(page_tag.get_text(strip=True))

            page_url = f"{root_url}{page_tag['href']}"

            pages.append((page_number, page_url))

        return PageInfo(hospitals, pages, total_results)
    
    @staticmethod
    def from_result_tag(result_tag: Tag) -> Hospital:
        name = result_tag.find("a", class_="result__name").get_text(strip=True)

        data = result_tag.find("ul", class_="result-data")

        data_items = data.find_all("li")

        address = "未定"
        phone = "未定"
        nearest_station = "未定"
        department = "未定"

        if len(data_items) >= 4:
            department = data_items[3].get_text(strip=True)
        if len(data_items) >= 3:
            nearest_station = data_items[2].get_text(strip=True)
        if len(data_items) >= 2:
            phone = data_items[1].get_text(strip=True)
        if len(data_items) >= 1:
            address = data_items[0].get_text(strip=True)

        return Hospital(name, address, phone, nearest_station, department)