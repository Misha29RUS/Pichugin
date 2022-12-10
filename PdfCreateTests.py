from unittest import TestCase

from PdfCreate import Vacancy
from PdfCreate import Total
from PdfCreate import csv_reader


class VacancyTests(TestCase):
    vacancy = {
        'name': 'Программист',
        'salary_from': '40000.0',
        'salary_to': '55000.0',
        'salary_currency': 'RUR',
        'area_name': 'Москва',
        'published_at': '2012-04-09T13:49:00+0400',
    }

    def test_name_vacancy(self):
        self.assertEqual(Vacancy(self.vacancy).job_name, 'Программист')

    def test_published_vacancy(self):
        self.assertEqual(Vacancy(self.vacancy).year, 2012)

    def test_type_vacancy(self):
        self.assertEqual(type(Vacancy(self.vacancy)).__name__, 'Vacancy')

    def test_area_vacancy(self):
        self.assertEqual(Vacancy(self.vacancy).area_name, 'Москва')

    def test_salary_vacancy(self):
        self.assertEqual(Vacancy(self.vacancy).salary, 47500)


class TotalTests(TestCase):
    vacancy = [Vacancy({
        'name': 'Программист',
        'salary_from': '40000.0',
        'salary_to': '55000.0',
        'salary_currency': 'RUR',
        'area_name': 'Москва',
        'published_at': '2012-04-09T13:49:00+0400',
    })]

    def test_get_data(self):
        test_param = Total()
        test_param.get_data(self.vacancy, 'Специалист')
        self.assertEqual(test_param.dynamics_count_by_year.count_dict, {2012: 1})
        self.assertEqual(test_param.dynamics_job_count_city.count_dict, {'Москва': 1})
        self.assertEqual(test_param.dynamics_job_count_year.count_dict, {2012: 0})
        self.assertEqual(test_param.dynamics_job_salary_city.salary_dictionary, {'Москва': [47500]})
        self.assertEqual(test_param.dynamics_job_salary_year.salary_dictionary, {2012: [0]})
        self.assertEqual(test_param.dynamics_salary_by_year.salary_dictionary, {2012: [47500]})


class CsvReaderTests(TestCase):
    test_param = csv_reader('vacancy_test_data.csv')

    def test_csv_reader(self):
        self.assertEqual(len(self.test_param), 3)
        self.assertEqual(self.test_param[0]['name'], 'Специалист')
        self.assertEqual(self.test_param[1]['area_name'], '<html>Санкт-Петербург</html>')
