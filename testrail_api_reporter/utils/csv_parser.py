# -*- coding: utf-8 -*-
""" CSV parser for TestRail API Reporter """

import csv
from datetime import datetime
from os.path import exists
from typing import List

from .logger_config import setup_logger, DEFAULT_LOGGING_LEVEL


class CSVParser:
    """Parser for CSV files"""

    def __init__(self, filename=None, logger=None, log_level=DEFAULT_LOGGING_LEVEL):
        """
        Default init

        :param filename: filename for csv file
        :param logger: logger object, optional
        :param log_level: logging level, optional, by default is logging.DEBUG
        """
        if not logger:
            self.___logger = setup_logger(name="CSVParser", log_file="CSVParser.log", level=log_level)
        else:
            self.___logger = logger
        self.___logger.debug("Initializing CSV Parser")
        self.__filename = filename

    def save_history_data(self, filename=None, report=None):
        """
        Save history data to CSV

        :param filename: file name of output file, required
        :param report: report with distribution in CaseStat format
        :return:
        """
        filename = filename if filename else self.__filename
        if not filename:
            raise ValueError("Filename for save report data is not provided, save history data aborted!")
        if not report:
            raise ValueError("Report couldn't be found, save history data aborted!")
        date = datetime.today().strftime("%Y-%m-%d")
        last_date = ""
        mode = "r" if exists(filename) else "w"
        with open(filename, mode, encoding="utf-8") as csvfile:
            if mode == "r":
                for row in reversed(list(csv.reader(csvfile))):
                    last_date = f"{row[0]}-{row[1]}-{row[2]}"
                    break
        if last_date != date:
            self.___logger.debug("Last date in file: %s for %s", filename, last_date)
            with open(filename, "a+", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)

                writer.writerow(
                    [
                        datetime.today().strftime("%Y"),
                        datetime.today().strftime("%m"),
                        datetime.today().strftime("%d"),
                        report.get_total(),
                        report.get_automated(),
                        report.get_not_automated(),
                        report.get_not_applicable(),
                    ]
                )
        else:
            self.___logger.debug("Data already stored for today, skipping save")

    def load_history_data(self, filename=None) -> List:
        """
        Load history data to CSV

        :param filename: file name of output file, required
        :return: list with results
        """
        filename = filename if filename else self.__filename
        if not filename:
            raise ValueError("Filename for load report data is not provided, save history data aborted!")
        timestamps = []
        totals = []
        automated = []
        not_automated = []
        nas = []
        self.___logger.debug("Loading history data from %s", filename)
        try:
            with open(filename, "r", encoding="utf-8") as csvfile:
                for row in csv.reader(csvfile):
                    timestamps.append(datetime(year=int(row[0]), month=int(row[1]), day=int(row[2])))
                    totals.append(row[3])
                    automated.append(row[4])
                    not_automated.append(row[5])
                    nas.append(row[6])
        except FileNotFoundError:
            raise ValueError(f"Can't open report file '{filename}', load history data aborted!") from FileNotFoundError
        return [timestamps, totals, automated, not_automated, nas]
