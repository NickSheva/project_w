"""Search Cartier"""
import pandas as pd

# Загрузка данных из csv
CSV_FILE = "products_table_jewellery.csv"
df_csv = pd.read_csv(CSV_FILE)

# Фультрация данных только для бренда "Cartier"
cartier_df_csv = df_csv[df_csv['title']=='Cartier']


# Отображение данных на экране
print("Данные из CSV файла для Cartier:")
print(cartier_df_csv)






# Извлечение данных из XLSX
XLSX_FILE = "products_table_jewellery.xlsx"
df_xlsx = pd.read_excel(XLSX_FILE)

# Фильтрация данных только для бренда "Cartier"
cartier_df_xlsx = df_xlsx[df_xlsx['title'] == "Cartier"]

# Отображение данных на экране
print("Данные из EXCEL файла для Cartier:")
print(cartier_df_xlsx)
