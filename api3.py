import pandas as pd
import grequests


class RequestsHH:
    ''' класс RequestsHH отправляет запросы к api hh.ru и формирует csv-файл из полученных вакансий.
    Attributes: head (list) : список заголовков для dataFrame
    '''
    def __init__(self, head):
        '''
        Инициализирует класс RequestsHH
        Attributes: head: head (list) : список заголовков для dataFrame
        '''
        self.head = head

    @staticmethod
    def makeRequests():
        '''
        Отправляет запросы на получение IT-вакансий за 12 декабря 2022
        :return: результат запросов
        '''
        urls = []
        urls += [
            f'https://api.hh.ru/vacancies?specialization=1&per_page=100&page={page}&date_from=2022-12-12T00:00:00&date_to=2022-12-12T08:00:00'
            for page in range(20)]
        urls += [
            f'https://api.hh.ru/vacancies?specialization=1&per_page=100&page={page}&date_from=2022-12-12T08:00:00&date_to=2022-12-12T16:00:00'
            for page in range(20)]
        urls += [
            f'https://api.hh.ru/vacancies?specialization=1&per_page=100&page={page}&date_from=2022-12-12T16:00:00&date_to=2022-12-13T00:00:00'
            for page in range(20)]
        requests = (grequests.get(url) for url in urls)
        return requests

    @staticmethod
    def parse_vac_for_csv(vac):
        '''
        Работает с каждой вакансией, разделяет ее на необходимые поля
        :param vac: одна вакансия из запроса
        :return: вакансия, разделенная по полям
        '''
        name, area_name, published_at, salary = vac['name'], vac['area']['name'], vac['published_at'], vac['salary']
        salary_from = salary['from'] if salary else None
        salary_to = salary['to'] if salary else None
        salary_currency = salary['currency'] if salary else None
        return name, salary_from, salary_to, salary_currency, area_name, published_at

    def make_csv(self):
        '''
        Создает csv-файл из вакансий, полученных ранее
        :return: csv-файл с вакансиями за 12 декабря 2022
        '''
        vac_list = []
        for req in grequests.map(self.makeRequests()):
            for vac in req.json()['items']:
                vac_list.append(self.parse_vac_for_csv(vac))
        pd.DataFrame(data=vac_list, columns=self.head).to_csv('vacancies_from_hh.csv', index=False)


head = ['name', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at']
result = RequestsHH(head)
result.make_csv()
