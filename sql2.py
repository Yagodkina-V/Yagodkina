import pandas as pd
import sqlite3


class ConvertVacancy:
    ''' Класс ConvertVacancy превращает несколько полей о зарплате в одно и формирует таблицу в бд
    Attributes:
        file_name (DataFrame): исходный файл с вакансиями
    '''
    def __init__(self, file_name):
        '''
        Инициализирует класс ConvertVacancy
        :param file_name:  исходный файл с вакансиями
        '''
        self.file_name = pd.read_csv(file_name)

    def get_converted_currency_salary(self, currency, date):
        '''
        возвращает курс валюты
        :param currency: код валюты ('EUR' и т.д.)
        :param date: дата в формате год-месяц
        :return: курс валюты или None если отсутствуют данные
        '''
        sqlite_data = f"select {currency} from currency_values_03_22 where date = ?"
        try:
            return cursor.execute(sqlite_data, (date,)).fetchone()[0]
        except:
            return None

    def get_salary_row(self, row):
        '''
        Объединяет поля о зарплате в одно
        :param row: строка файла с вакансиями ( 1 вакансия)
        :return: сформированное поле о зарплате
        '''
        salary_from = row['salary_from']
        salary_to = row['salary_to']
        salary_currency = row['salary_currency']
        date = row['published_at'][:7]
        if pd.isnull(salary_currency) or (pd.isnull(salary_to) and pd.isnull(salary_from)):
            return None
        if salary_currency == 'RUR':
            conv = 1
        else:
            conv = self.get_converted_currency_salary(salary_currency, date)
        if not conv:
            return None
        salary_from = 0 if pd.isnull(salary_from) else salary_from
        salary_to = 0 if pd.isnull(salary_to) else salary_to
        if salary_to == 0 or salary_from == 0:
            average_salary = max(salary_to, salary_from)
        else:
            average_salary = 0.5 * (salary_to + salary_from)
        salary = round(average_salary * conv, 0)
        return salary

    def make_sql(self):
        '''
        создает новую таблицу в базе данных
        :return: таблица в бд
        '''
        data = self.file_name.copy()
        data['salary'] = data.apply(lambda x: self.get_salary_row(x), axis=1)
        data['published_at'] = data['published_at'][:7]
        data[['name', 'salary', 'area_name', 'published_at']].to_sql('YagodkinaVera',
                                                                     con=sqlite_connection, index=False)


sqlite_connection = sqlite3.connect('currency_values_03_22.db')
cursor = sqlite_connection.cursor()
file_name = 'vacancies_dif_currencies.csv'
result = ConvertVacancy(file_name)
result.make_sql()
