from typing import List, Tuple

from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime


class BoibExtractor:

    BOIB_URL = "http://www.caib.es/eboibfront/ca/"
    SUB_SECTION_URL = "/seccio-ii-autoritats-i-personal/473"
    BASELINE_BOIB_ID = 10922

    def __init__(self):
        pass

    def extract_boibs(self, init_date: str) -> pd.DataFrame:
        """
        Extract the BOIB publications in a given time ranege.

        :param init_date:
        :param end_date:
        :return:
        """
        init_date = pd.to_datetime(init_date)
        boib_date, ref_num = self._get_last_boib_info()
        boibs = []
        while boib_date > init_date:
            boib_df, boib_date = self._extract_boib_data(ref_num)
            if boib_date > init_date:
                boibs.append(boib_df)
            ref_num -= 1
        final_df = self._merge_boibs(boibs)
        self._export_data(final_df)
        return final_df

    def _get_last_boib_info(self) -> Tuple[datetime, int]:
        response = requests.get(self.BOIB_URL)
        link_last = self._extract_url_last_boib(response.text)
        last_date = self._extract_date_from_url(response.text)
        ref_num = int(link_last.split("/")[-1])
        return last_date, ref_num

    def _extract_url_last_boib(self, html: str) -> str:
        soup = BeautifulSoup(html, 'lxml')
        element = soup.find("a", string="Darrer número")
        url = element["href"]
        return url

    def _extract_date_from_url(self, html: str) -> datetime:
        soup = BeautifulSoup(html, 'lxml')
        element = soup.find("a", class_="fijo")
        text = element.text
        no_tabs = text.replace("\n", "").replace("\t", "").replace(" ", "")
        date_str = no_tabs.split("-")[-1]
        # TODO: Transform date in catalan to datetime
        
    def _extract_boib_data(self, ref_num: int) -> Tuple[pd.DataFrame, datetime]:
        pass

    def _merge_boibs(self, boibs: List[pd.DataFrame]) -> pd.DataFrame:
        pass

    def _export_data(self, dataframe: pd.DataFrame):
        pass