# импорт необходимых библиотек
import pandas as pd 
import requests 
from io import StringIO 
import time 
from datetime import datetime 
import xlsxwriter 

# Функция для получения данных об акциях из сервиса Yahoo Finance
def get_yahoo_stock_data(ticker, start_date, end_date, cookie, crumb): 
    start_date_unix = int(pd.Timestamp(start_date).timestamp()) 
    end_date_unix = int(pd.Timestamp(end_date).timestamp()) 

# Формирование URL-адреса для получения данных об акциях из сервиса Yahoo Finance
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={start_date_unix}&period2={end_date_unix}&interval=1d&events=history&crumb={crumb}"
    headers = {# Определение заголовков HTTP-запроса
        "user-agent": "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)",
        "cookie": f"B={cookie};",
        "referer": f"https://finance.yahoo.com/quote/{ticker}/history?p={ticker}" 
    }

    response = requests.get(url, headers=headers) # Выполнение HTTP-запроса и сохранение ответа в переменную response

    if response.status_code == 200: 
        data = pd.read_csv(StringIO(response.text)) 
        return data 
    else: 
        print(f"Error fetching data for {ticker}: {response.status_code}") # Если ответ содержит ошибку, то вывести сообщение об ошибке
        return None # Возврат пустого значения (None)
    
# Задаем значения cookie и crumb
cookie = "YOUR_COOKIE_VALUE" 
crumb = "YOUR_CRUMB_VALUE" 

# Создаем словарь с тикерами акций и их названиями
tickers = { 
    'GAZP.ME': 'Газпром', 
    'SBER.ME': 'Сбербанк' 
}

# Задаем начальную и конечную даты для получения данных об акциях
start_date = "2020-01-01" 
end_date = datetime.today().strftime("%Y-%m-%d") 

# Получаем данные о валютной паре RUB/USD
rub_usd_ticker = "RUB=X" 
rub_usd_data = get_yahoo_stock_data(rub_usd_ticker, start_date, end_date, cookie, crumb) 

# Переименование столбцов полученных данных для валютной пары RUB/USD.
if rub_usd_data is not None: 
    rub_usd_data = rub_usd_data.rename(columns={ 
        "Date": "Дата (руб.)", #
        "Close": "Закрытие (руб.)", #
    })
    
# Выбор только столбцов с датой и закрытием курса валютной пары RUB/USD.
    rub_usd_data = rub_usd_data[["Дата (руб.)", "Закрытие (руб.)"]] 

# Начало итерации по словарю с тикерами и названиями компаний.
    for ticker, company_name in tickers.items(): 
        # Получение исторических данных для текущей компании.
        stock_data = get_yahoo_stock_data(ticker, start_date, end_date, cookie, crumb) 
        # Задержка в 3 секунды между запросами, чтобы избежать блокировки со стороны сервера.
        time.sleep(3)  

        if stock_data is not None: 
        # Переименование столбцов полученных данных для текущей компании.
            stock_data = stock_data.rename(columns={ 
                "Date": "Дата (руб.)",
                "Open": "Открытие (руб.)",
                "High": "Максимальная (руб.)",
                "Low": "Мининимальная (руб.)",
                "Close": "Закрытие (руб.)",
                "Adj Close": "Скорректированное закрытие (руб.)",
                "Volume": "Объем (шт.)",
            })

            # Объединение данных для текущей компании с данными для валютной пары RUB/USD по столбцу с датой.
            stock_data = stock_data.merge(rub_usd_data, on='Дата (руб.)', how='left') 

            # Создание объекта записи в Excel-файл с помощью модуля pd.ExcelWriter.
            writer = pd.ExcelWriter(f'{company_name}.xlsx', engine='xlsxwriter') 

            # Запись данных DataFrame в лист Excel-файла.
            stock_data.to_excel(writer, sheet_name=company_name, index=False) 

            # Получение ссылки на лист Excel-файла для настройки ширины столбцов.
            worksheet = writer.sheets[company_name] 

            # Автоматическое изменение ширины столбцов на основе содержимого ячеек.
            for i, column in enumerate(stock_data.columns):
                column_width = max(stock_data[column].astype(str).map(len).max(), len(column))
                worksheet.set_column(i, i, column_width + 1)
            # Закрытие объекта записи в Excel-файл.
            writer.close()
        else:
            # Вывод сообщения об ошибке, если данные не были получены.
            print(f"Ошибка получения данных для {ticker}")

# Вывод сообщения об завершении программы            
print("Данные успешно записаны в Excel-файл")