# Импортируем необходимые библиотеки
import pandas as pd
import requests
import zipfile
import tempfile
import xlsxwriter

def get_world_bank_gdp_data(country_code, indicator_code):
    # Получение данных ВВП с сайта Всемирного банка
    url = f"http://api.worldbank.org/v2/en/country/{country_code}/indicator/{indicator_code}?downloadformat=csv"
    response = requests.get(url)

    if response.status_code == 200:
        # Создание временного файла для хранения архива с данными
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip:
            temp_zip.write(response.content)
            temp_zip.flush()

            # Чтение архива и получение данных
            with zipfile.ZipFile(temp_zip.name, 'r') as zf:
                with zf.open(zf.namelist()[1]) as f:
                    data = pd.read_csv(f, skiprows=4)
                    return data
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

gdp_data = get_world_bank_gdp_data("RUS", "NY.GDP.MKTP.CD")

if gdp_data is not None:
    writer = pd.ExcelWriter("ВВП_Россия.xlsx", engine="xlsxwriter")

    # Удаление столбца "Unnamed: 66"
    gdp_data = gdp_data.drop(columns=['Unnamed: 66'])

    # Переименовываем столбцы и преобразуем года в даты
    gdp_data = gdp_data.rename(columns={
        'Country Name': 'Страна',
        'Country Code': 'Код страны',
        'Indicator Name': 'Индикатор',
        'Indicator Code': 'Код индикатора'
    })

    # Удаление столбцов с годами до 1988 и переименование оставшихся
    for col in gdp_data.columns[4:]:
        if int(col) < 1988:
            gdp_data = gdp_data.drop(columns=[col])
        else:
            gdp_data = gdp_data.rename(columns={col: f"{col} год/USD млрд"})

    # Запись данных в файл Excel
    gdp_data.to_excel(writer, sheet_name="ВВП Россия", index=False)

    # Получение рабочего листа
    worksheet = writer.sheets["ВВП Россия"]

    # Создание формата с рамкой
    border = writer.book.add_format({'border': 1})
    
    # Цикл для автовыравнивания и применения форматов
    for i, column in enumerate(gdp_data.columns):
        column_width = max(gdp_data[column].astype(str).map(len).max(), len(column))
        if i >= 4:
            # Применение числового формата для столбцов с данными
            column_format = writer.book.add_format({'num_format': '0.00', 'border': 1})
            worksheet.set_column(i, i, column_width + 1, column_format)
        else:
        # Применение формата с рамкой для остальных столбцов
            worksheet.set_column(i, i, column_width + 1, border)

writer.close()

print("Данные успешно записаны в Excel-файл")