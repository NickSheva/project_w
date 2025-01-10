"""Search brand Cartier in EXCEL"""
import pandas as pd


# Извлечение данных из XLSX
XLSX_FILE = "products_table_jewellery.xlsx"
df_xlsx = pd.read_excel(XLSX_FILE)

# Фильтрация данных только для бренда "Cartier"
cartier_df_xlsx = df_xlsx[df_xlsx['title'] == "Cartier"]

# Отображение данных на экране
print("Данные из EXCEL файла для Cartier:")
print(cartier_df_xlsx)