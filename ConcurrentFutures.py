import itertools
import multiprocessing
from collections import ChainMap
from concurrent import futures

import pandas as pd
import os
import cProfile


def multiprocessing_file(csv_file, profession):
    """ Метод для мультипроцессорности
    Args:
        csv_file (str): Название файла с исходным данными
        profession (str): Вводимое название профессии
        queue (any): Очередь процесса
    """
    data_frame = pd.read_csv(csv_file)
    data_frame['salary'] = data_frame[['salary_from', 'salary_to']].mean(axis=1)
    data_frame['published_at'] = data_frame['published_at'].apply(lambda current: int(current[:4]))
    data_frame_vacancy = data_frame[data_frame['name'].str.contains(profession)]
    years_data = data_frame['published_at'].unique()
    dynamics_salary_by_year = {year: [] for year in years_data}
    dynamics_count_by_year = {year: 0 for year in years_data}
    dynamics_job_salary_year = {year: [] for year in years_data}
    dynamics_job_count_year = {year: 0 for year in years_data}
    for year in years_data:
        dynamics_salary_by_year[year] = int(data_frame[data_frame['published_at'] == year]['salary'].mean())
        dynamics_count_by_year[year] = len(data_frame[data_frame['published_at'] == year])
        dynamics_job_salary_year[year] = int(data_frame_vacancy[data_frame_vacancy['published_at'] == year]['salary'].mean())
        dynamics_job_count_year[year] = len(data_frame_vacancy[data_frame_vacancy['published_at'] == year].index)
    return [dynamics_salary_by_year, dynamics_count_by_year, dynamics_job_salary_year, dynamics_job_count_year]


def single_processing_file(file):
    """ Метод для мультипроцессорности
    Args:
        file (str): Путь к файлу с исходными данными
    Returns:
        list: Возвращает динамики по городам
    """
    data_frame = pd.read_csv(file)
    data_frame['published_at'] = data_frame['published_at'].apply(lambda x: int(x[:4]))
    data_frame['salary'] = data_frame[['salary_from', 'salary_to']].mean(axis=1)
    data_frame['count'] = data_frame.groupby('area_name')['area_name'].transform('count')
    data_frame_normal = data_frame[data_frame['count'] > 0.01 * len(data_frame)]
    cities = list(data_frame_normal['area_name'].unique())
    dynamics_job_salary_city = {}
    dynamics_job_count_city = {}
    for city in cities:
        data_frame_salary = data_frame_normal[data_frame_normal['area_name'] == city]
        dynamics_job_salary_city[city] = int(data_frame_salary['salary'].mean())
        dynamics_job_count_city[city] = round(len(data_frame_salary) / len(data_frame), 4)
    return [dynamics_job_salary_city, dynamics_job_count_city]


def user_data(file, profession):
    """ Метод для получения данных пользователя и начала работы основной программы
    Args:
        file (str): Название файла с исходным данными, которое ввёл пользователь
        profession (str): Название профессии, которое ввёл пользователь
    """
    data = []
    executor = futures.ProcessPoolExecutor()
    for file_name in os.listdir(file):
        file_csv_name = os.path.join(file, file_name)
        result_data = executor.submit(multiprocessing_file, file_csv_name, profession).result()
        data.append(result_data)
    second = single_processing_file('startData\\vacancies_by_year.csv')
    result_list = list(zip(*data))
    print(f'Динамика уровня зарплат по годам: {dict(sorted(dict(ChainMap(*result_list[0])).items(), key=lambda x: x[0]))}')
    print(f'Динамика количества вакансий по годам: {dict(sorted(dict(ChainMap(*result_list[1])).items(), key=lambda x: x[0]))}')
    print(f'Динамика уровня зарплат по годам для выбранной профессии: {dict(sorted(dict(ChainMap(*result_list[2])).items(), key=lambda x: x[0]))}')
    print(f'Динамика количества вакансий по годам для выбранной профессии: {dict(sorted(dict(ChainMap(*result_list[3])).items(), key=lambda x: x[0]))}')
    print(f'Уровень зарплат по городам (в порядке убывания): {dict(itertools.islice(sorted(second[0].items(), key=lambda x: x[1], reverse=True), 10))}')
    print(f'Доля вакансий по городам (в порядке убывания): {dict(itertools.islice(sorted(second[1].items(), key=lambda x: x[1], reverse=True), 10))}')


if __name__ == '__main__':
    profiler = cProfile.Profile()
    profiler.enable()
    user_data(input('Введите название файла: '), input('Введите название профессии: '))
    profiler.disable()
    profiler.print_stats(sort='cumtime')