import pandas as pd
import xmltodict
import grequests


class AnaliticsCurr:
    '''Класс AnaliticsCurr формирует отчет в формате csv-файла
    Attributes:
        data (str) - строки файла с заполненным полем валюты
    '''
    def __init__(self, data):
        ''' Инициализирует класс AnaliticsCurr
        Attributes:
            data (str) - строки csv-файла
        '''
        self.data = data[pd.notnull(data['salary_currency'])]

    def d_m_y_date(self, date):
        '''
        Изменяет формат даты
        :param date: дата в исходном формате
        :return: возвращает дату в формате день-месяц-год
        '''
        return f'{date[8:]}/{date[5:7]}/{date[:4]}'

    def change_date(self, date):
        '''
        Обрезает дату
        :param date: исходный формат даты
        :return: дату в формате год-месяц
        '''
        return f'{date[6:]}-{date[3:5]}'

    def get_count_currency(self):
        '''
        Считает сколько раз упоминается каждаю валюта
        :return: словарь (значение - количество упоминаний, ключ - валюта)
        '''
        return self.data['salary_currency'].value_counts().to_dict()

    def get_frequrency(self):
        '''
        Считает частоту для каждой валюты
        :return: словврь (ключ- валюта, значение - частота)
        '''
        amount_data = len(self.data.index)
        freq_currency_dict = {currency: amount / amount_data for currency, amount in self.get_count_currency().items()}
        return freq_currency_dict

    def get_popular_currency(self):
        '''
        Создает список нименованний валют, которые упоминаются больше 5000 раз и не являются рублями
        :return: список валют
        '''
        list_curr = []
        for k, v in self.get_count_currency().items():
            if v > 5000 and k != 'RUR':
                list_curr.append(k)
        return list_curr

    def get_dates(self):
        '''
        Находит диапазон между самой старой вакансией и самой новой
        :return: диапазон между 2 датами
        '''
        years_series = pd.to_datetime(self.data['published_at'].apply(lambda x: x[:10]))
        dad, son = self.d_m_y_date(str(years_series.min())[:10]), self.d_m_y_date(str(years_series.max())[:10])
        return pd.date_range(start=dad, end=son, freq='M').strftime('%d/%m/%Y').tolist()

    def requests(self):
        '''
        Создает список запросов к цб по датам
        :return: список запросов по дате
        '''
        list_curr = [f'https://www.cbr.ru/scripts/XML_daily.asp?date_req={date}' for date in self.get_dates()]
        return list_curr

    def make_res_dict(self):
        '''
        Сопоставляет дату и курс валют
        :return: словарь (ключи - дата и наименования валют, значения - дата(год-месяц), курс валют)
        '''
        list_currency = self.get_popular_currency()
        dict_result = {'date': []}
        dict_result.update({currency: [] for currency in list_currency})
        for request in grequests.map(grequests.get(url) for url in self.requests()):
            data = xmltodict.parse(request.text)['ValCurs']
            dict_result['date'] = dict_result['date'] + [self.change_date(data['@Date'])]
            currency_value = {currency: 0 for currency in list_currency}
            for currency in data['Valute']:
                if currency['CharCode'] in list_currency:
                    currency_value[currency['CharCode']] = round(float(currency['Value'].replace(',', '.')) /
                                                                 float(currency['Nominal']), 6)
            for k, v in currency_value.items():
                dict_result[k] = dict_result[k] + [v]
        return dict_result

    def make_csv(self):
        '''
        Создает csv-файл с помощью pandas
        :return: csv-файл
        '''
        pd.DataFrame(self.make_res_dict()).to_csv(path_or_buf='currency_from_2003_to_2022.csv', index=False, encoding='utf-8-sig')


file_name = 'vacancies_dif_currencies.csv'
currency_count = AnaliticsCurr(pd.read_csv(file_name))
currency_count.make_csv()
