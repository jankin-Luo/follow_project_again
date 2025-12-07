import csv, os
from conf.setting import DIR_PATH
from common.readyaml import logs


def read_csv_date(file_name):
    with open(os.path.join(DIR_PATH, 'data', file_name), 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        data = list(csv_reader)
        return data


if __name__ == '__main__':
    print(read_csv_date('test_data.csv'))
