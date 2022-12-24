import pandas as pd


class ConvertVacancy:
    ''' Класс ConvertVacancy превращает несколько полей о зарплате в одно и формирует csv-файл
    Attributes:
        file_name (DataFrame): исходный файл с вакансиями
        convert_file (DataFrame): файл с валютами с 2003 до 2022
    '''
    def __init__(self, file_name, convert_file):
        '''
        Инициализирует класс ConvertVacancy
        :param file_name:  исходный файл с вакансиями
        :param convert_file: файл с валютами с 2003 до 2022
        '''
        self.file_name = pd.read_csv(file_name)
        self.convert_file = pd.read_csv(convert_file)

    def get_converted_currency_salary(self, currency, date):
        '''
        возвращает курс валюты
        :param currency: код валюты ('EUR' и т.д.)
        :param date: дата в формате год-месяц
        :return: курс валюты или None если отсутствуют данные
        '''
        try:
            res_conv = self.convert_file[self.convert_file['date'] == date][currency].values
        except:
            return None
        if len(res_conv) > 0:
            return res_conv[0]
        else:
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
        average_salary = 0
        if salary_to == 0 or salary_from == 0:
            average_salary = max(salary_to, salary_from)
        else:
            average_salary = 0.5 * (salary_to + salary_from)
        salary = round(average_salary * conv, 0)
        return salary

    def make_csv_100(self):
        '''
        создает csv-файл на 100 вакансий
        :return: csv-файл
        '''
        data = self.file_name.copy()
        data = data.head(100)
        data['salary'] = data.apply(lambda x: self.get_salary_row(x), axis=1)
        data[['name', 'salary', 'area_name', 'published_at']].to_csv('vacancies_with_converted_currency.csv', index=False)


file_name = 'vacancies_dif_currencies.csv'
convert_file = 'currency_from_2003_to_2022.csv'
result = ConvertVacancy(file_name, convert_file)
result.make_csv_100()
