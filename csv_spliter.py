import csv
import os


def quick_quit(message):
    """Метод для выдачи ошибки и выхода из программы.

    Args:
        message (str): Текст сообщение об ошибке
    """
    print(message)
    exit()


def csv_spliter(file_name):
    """
    Выполняет разделение входного файла в формате csv на отдельные файлы этого же формата по годам.
    Сохраняет новые файлы в папку vacancies_data

    Args:
        file_name: Название входного файла
    """
    vacancies_by_year_split = {}
    vacancies_reader = csv.reader(open(file_name, encoding='utf_8_sig'))
    vacancies_data = [row for row in vacancies_reader]
    if len(vacancies_data) == 0:
        quick_quit('Пустой файл')
    vacancies_dict = [dict(zip(vacancies_data[0], value)) for value in vacancies_data[1:]]
    for current_vacancy in vacancies_dict:
        if vacancies_by_year_split.get(current_vacancy['published_at'][:4]) is None:
            vacancies_by_year_split[current_vacancy['published_at'][:4]] = []
            vacancies_by_year_split[current_vacancy['published_at'][:4]].append(current_vacancy)
        else:
            vacancies_by_year_split[current_vacancy['published_at'][:4]].append(current_vacancy)

    os.mkdir('vacancies_data')
    for year in vacancies_by_year_split.keys():
        with open(f'vacancies_data\{year}.csv', mode="w", encoding='utf_8_sig') as add_file:
            headers = vacancies_data[0]
            file_writer = csv.DictWriter(add_file, delimiter=",",
                                         lineterminator="\r", fieldnames=headers)
            file_writer.writeheader()
            file_writer.writerows(vacancies_by_year_split[year])

csv_spliter('startData\\vacancies_by_year.csv')