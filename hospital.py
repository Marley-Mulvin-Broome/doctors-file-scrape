from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag
from xlsxwriter.worksheet import Worksheet


@dataclass
class Hospital:
    name: str
    address: str
    phone: str
    station: str
    department: str

    def write_to_worksheet(self, worksheet: Worksheet, row, starting_column = 0):
        worksheet.write(row, starting_column, self.name)
        worksheet.write(row, starting_column + 1, self.address)
        worksheet.write(row, starting_column + 2, self.phone)
        worksheet.write(row, starting_column + 3, self.station)
        worksheet.write(row, starting_column + 4, self.department)

    def __str__(self):
        return f"{self.name}, {self.address}, {self.phone}, {self.station}, {self.department}"

    def __repr__(self):
        return self.__str__()