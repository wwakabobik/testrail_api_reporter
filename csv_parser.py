import csv
from datetime import datetime
from os.path import exists


class CSVParser:
    """ Parser for CSV files """
    def __init__(self, filename=None, debug=True):
        """
        Default init

        :param filename: filename for csv file
        :param debug: debug output, enabled or not
        """
        if debug:
            print("\nPlotly Reporter init")
        self.__debug = debug
        self.__filename = filename

    def save_history_data(self, filename=None, report=None, debug=None):
        """
        Save history data to CSV

        :param filename: file name of output file, required
        :param report: report with distribution in CaseStat format
        :param debug: debug output, enabled or not
        :return:
        """
        debug = debug if debug is not None else self.__debug
        filename = filename if filename else self.__filename
        if not filename:
            raise ValueError("Filename for save report data is not provided, save history data aborted!")
        if not report:
            raise ValueError("Report couldn't be found, save history data aborted!")
        date = datetime.today().strftime('%Y-%m-%d')
        last_date = ''
        mode = 'r' if exists(filename) else 'w'
        try:
            with open(filename, mode) as csvfile:
                if mode == 'r':
                    for row in reversed(list(csv.reader(csvfile))):
                        last_date = '{0}-{1}-{2}'.format(row[0], row[1], row[2])
                        break
        except FileNotFoundError:
            raise ValueError("Can't open report file, save history data aborted!")
        if last_date != date:
            if debug:
                print('Saving data in {0} for {1}'.format(filename, date))
            with open(filename, 'a+', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

                writer.writerow([datetime.today().strftime('%Y'),
                                datetime.today().strftime('%m'),
                                datetime.today().strftime('%d'),
                                report.get_total(),
                                report.get_automated(),
                                report.get_not_automated(),
                                report.get_na()])
        else:
            if debug:
                print('Data already stored for today, skipping save')

    def load_history_data(self, filename=None, debug=None):
        """
        Load history data to CSV

        :param filename: file name of output file, required
        :param debug: debug output, enabled or not
        :return: list with results
        """
        debug = debug if debug is not None else self.__debug
        filename = filename if filename else self.__filename
        if not filename:
            raise ValueError("Filename for load report data is not provided, save history data aborted!")
        timestamps = []
        totals = []
        automateds = []
        not_automateds = []
        nas = []
        if debug:
            print('Loading history data from {}'.format(filename))
        try:
            with open(filename, 'r') as csvfile:
                for row in (csv.reader(csvfile)):
                    timestamps.append(datetime(year=int(row[0]), month=int(row[1]), day=int(row[2])))
                    totals.append(row[3])
                    automateds.append(row[4])
                    not_automateds.append(row[5])
                    nas.append(row[6])
        except FileNotFoundError:
            raise ValueError("Can't open report file, load history data aborted!")
        return [timestamps, totals, automateds, not_automateds, nas]
