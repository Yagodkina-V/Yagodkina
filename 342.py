import pandas as pd
from jinja2 import Environment, FileSystemLoader
import pdfkit


class Report:
    ''' Класс Report создает pdf-файл
    Attributes:
        file_name (DataFrame) : данные о вакансиях
        profession (str) : название выбранной профессии
    '''
    def __init__(self, file_name, profession):
        '''
        Инициализирует класс Report
        :param file_name(DataFrame) : данные о вакансиях
        :param profession(str) : название выбранной профессии
        '''
        self.file = pd.read_csv(file_name)
        self.profession = profession

    def get_analitic_by_year(self, data: pd.DataFrame):
        '''
        Возвращает данные о вакансиях за 1 год
        :param data: вакансии
        :return: количество вакансий, средняя зарплата, количество вакансий для выбранной профессии,
         количество вакансий по выбранной профессии за год
        '''
        prof_data = data[data['name'].str.contains(self.profession, case=False)]
        average_salary = round(data.apply(lambda x: x['salary'], axis=1).mean())
        prof_average_salary = round(prof_data.apply(lambda x: x['salary'], axis=1).mean())
        return data.shape[0], average_salary, prof_data.shape[0], prof_average_salary

    def get_file_analytic(self):
        '''
        Создает словари с аналитикой по годам
        :return: Возвращает 4 словаря
        '''
        self.file['year'] = self.file['published_at'].apply(lambda x: x[:4])
        years_vac = self.file.groupby(['year'])
        dict_salary, dict_count, dict_salary_prof, dict_count_prof = {}, {}, {}, {}
        for year, df in years_vac:
            count, average_salary, count_prof, prof_average_salary = self.get_analitic_by_year(df)
            dict_salary[year] = average_salary
            dict_count[year] = count
            dict_salary_prof[year] = prof_average_salary
            dict_count_prof[year] = count_prof
        return dict_salary, dict_count, dict_salary_prof, dict_count_prof

    def make_pdf(self):
        '''
        Создает pdf-файл
        :return: Возвращает pdf-файл с аналитикой по годам (с 2003 до 2022)
        '''
        salary, amount, this_vacancy_salary, this_vacancy_amount = self.get_file_analytic()
        template = Environment(loader=FileSystemLoader('other')).get_template('pdf_template.html')
        statistic = [[year, salary[year], this_vacancy_salary[year], amount[year], this_vacancy_amount[year]] for year in salary]
        pdf_template = template.render({'name': self.profession, 'statistic': statistic})
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdfkit.from_string(pdf_template, 'report.pdf', configuration=config, options={"enable-local-file-access": ""})


file_name = input('Введите название файла: ')
profession = input('Введите название профессии: ').lower()
result = Report(file_name, profession)
result.make_pdf()
