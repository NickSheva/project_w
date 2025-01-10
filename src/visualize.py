"""Visualize what you need"""
import pandas as pd
import plotly.express as px

def visualize_csv(file_path) -> None:
    """
    Визуализирует данные из указанного CSV файла с помощью Plotly.
    Args:
        file_path (str): Путь к файлу CSV.
    """
    try:
        # Загрузка данных
        df = pd.read_csv(file_path)

        # Пример подсчета количества товаров по брендам
        data = df['title'].value_counts().reset_index()
        data.columns = ['Brand', 'Count']  # Переименование колонок

        # Построение круговой диаграммы
        fig = px.pie(
            data,
            names='Brand',
            values='Count',
            title="Количество товаров по брендам",
            hole=0.4,             # Для донат-диаграммы
            width=1600,           # Ширина графика
            height=800,          # Высота графика
            color_discrete_sequence=px.colors.qualitative.G10,
            # color_discrete_sequence=px.colors.sequential.RdBu
        )

        # Настройка отображаемой информации
        fig.update_traces(
            textposition='inside',
            # Отображение названия категории и количества
            textinfo='label+value+percent',
            # Размер текста
            textfont_size=9,
            insidetextorientation='horizontal',  # horizontal, radial, tangential, auto
        )
        fig.update_layout(margin=dict(t=50, b=50, l=50, r=50),
                          # Minimum text message value
                          uniformtext_minsize=15,
                          # 3 modes: [False, 'hide', 'show']
                          uniformtext_mode='show',
                          )
        # Показ графика
        fig.show()

    except FileNotFoundError:
        print(f"Файл {file_path} не найден.")
    except ValueError as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    # Укажите путь к файлу CSV
    CSV_FILE = "products_table_clocks_today.csv"

    # Визуализация данных
    visualize_csv(CSV_FILE)
