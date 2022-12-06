from unittest import TestCase, main
from main import DataSet, Vacancy, Salary, Report


class SalaryTests(TestCase):
    def test_salary_type(self):
        self.assertEqual(type(Salary(10.0, 20.4, 'RUR')).__name__, 'Salary')

    def test_str_salary_from(self):
        self.assertEqual(Salary('10.15555555', 20.9, 'RUR').salary_from, 10)

    def test_float_salary_to(self):
        self.assertEqual(Salary(10.666666, '20.0', 'RUR').salary_to, 20)


class ReportTests(TestCase):
    def test_years_salary(self):
        self.assertEqual(Report({'2007': 10000, '2020': 50500}, {}, {}, {}, [], []).dct_years_salary['2020'], 50500)

    def test_amount(self):
        self.assertEqual(Report({}, {'2007': 120, '2020': 50}, {}, {}, [], []).dct_years_count['2007'], 120)

class DataSetTests(TestCase):
    def test_file_name(self):
        self.assertEqual(DataSet('vacancies_by_year.csv', 'Аналитик').file_name, 'vacancies_by_year.csv')

    def test_profession_name(self):
        self.assertEqual(DataSet('vacancies_by_year.csv', 'Аналитик').profession_name, 'Аналитик')


if __name__ == '__main__':
    main()
