import os
import pandas as pd


class PriceAnalyzer:
    def __init__(self, all_files_dir):
        print("Введите слово, по которому хотите найти товар.\nДля выхода, введите exit.")
        key_word = input()
        self.key_word = key_word
        self.all_files_dir = all_files_dir
        self.sorted_files_list = []
        # колонки в таблице, которые программа будет читать, остальные игнорировать
        self.cols_to_read = ["название", "продукт", "товар", "наименование", "цена", "розница", "фасовка", "масса",
                             "вес"]
        # --- --- --- ---

        # значения, которые могут встретиться программе в каждой из колонок, которые она будет приводить к одному виду
        self.product_names_column = ["название", "продукт", "товар", "наименование"]
        self.price_names_column = ["цена", "розница"]
        self.weight_names_column = ["фасовка", "масса", "вес"]
        # --- --- --- ---

        # дата фреймы, отсортированные по ключевому слову (для слияния в один)
        self.all_needed_dataframes = []
        # --- --- --- ---

        # дата фрейм, который нужно конвертировать в html и путь к html файлу
        self.df_to_html = None
        self.to_html_output_file = None
        # --- --- --- ---

    def load_prices(self):
        # сортировка файлов в указанной папке по ключевому слову "price" и сохранение их в список для обработки
        for file_name in (os.listdir(self.all_files_dir)):
            if "price" in file_name:
                self.sorted_files_list.append(f"{self.all_files_dir}/{file_name}")
        # --- --- --- ---

    def export_to_html(self):
        html_body_pt_1 = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
"""
        html_body_pt_2 = """
</body>
</html>
        """
        try:
            with open(self.to_html_output_file, "w", encoding="utf-8") as file:
                file.write(html_body_pt_1 + self.df_to_html + html_body_pt_2)
        except FileNotFoundError:
            print("К сожалению указанного файла не найдено")

    def find_text(self):
        if self.key_word != "exit":
            self.load_prices()
            for file_path in self.sorted_files_list:
                with open(file_path, encoding="utf-8") as file:
                    df = (pd.read_csv(file, sep=","))

                    # сортировка только по необходимым колонкам и удаление ненужных
                    columns = list(df.columns)
                    for col in columns:
                        if col not in self.cols_to_read:
                            columns.remove(col)
                    df = df[columns]
                    df.drop(df.columns[df.columns.str.contains(
                        'unnamed', case=False)], axis=1, inplace=True)
                    # --- --- --- ---

                    #  приведение имён столбцов к общему виду
                    columns = list(df.columns)
                    for idx in range(len(columns)):
                        if columns[idx] in self.product_names_column:
                            columns[idx] = "Наименование"
                        elif columns[idx] in self.price_names_column:
                            columns[idx] = "цена"
                        elif columns[idx] in self.weight_names_column:
                            columns[idx] = "вес"
                    df.columns = columns
                    # --- --- --- ---

                    # перестановка порядка столбцов
                    columns = list(df.columns)
                    if columns[0] != "Наименование":
                        columns[0] = "Наименование"
                    if columns[1] != "цена":
                        columns[1] = "цена"
                    if columns[2] != "вес":
                        columns[2] = "вес"
                    df = df[columns]
                    # --- --- --- ---

                    # добавление столбцов "файл" и "цена за кг"
                    file_name_column = []
                    for i in range(len(df)):
                        file_name_column.append(file.name[11:])
                    df.insert(3, "файл", file_name_column, True)
                    kilogram_price_count = round(df.eval('цена / вес').reset_index(drop=True), 1)
                    df.insert(4, "цена за кг.", list(kilogram_price_count), True)
                    # --- --- --- ---

                    # сортировка данных по ключевому слову без учёта регистра
                    key_word_df = df[df['Наименование'].str.contains(self.key_word, case=False)]
                    self.all_needed_dataframes.append(key_word_df)
                    # --- --- --- ---

            # комбинирование полученных по ключевому слову данных, сортировка по возрастанию "цены за кг." и
            # установление индекса в качестве номера
            combined_df = pd.concat([df for df in self.all_needed_dataframes], ignore_index=True)
            sorted_df = combined_df.sort_values(by='цена за кг.')
            sorted_df.index = range(1, len(combined_df) + 1)
            sorted_df.index.name = '№'
            # --- --- --- ---

            # отображение искомых данных
            if sorted_df.empty:
                print(f'Значений по ключевому слову "{self.key_word}" не найдено')
                return True
            else:
                # снятие ограничения максимального количества отображаемых строк и ширины столбцов
                with pd.option_context("display.max_rows", None, "display.max_columns", None):
                    print(sorted_df)
                # --- --- --- ---

                print("Конвертировать полученные данные в HTML файл? (Да/Нет)")
                to_html_choice = input()
                if to_html_choice.lower() == 'да':
                    self.df_to_html = sorted_df.to_html()
                    print("Пожалуйста, укажите путь к файлу (пример: to_html_dir/output.html), "
                          "в который требуется загрузить "
                          "данные\nДля отмены "
                          "действия введите back")
                    html_path_file = input()
                    if html_path_file != "back":
                        if ".html" in html_path_file:
                            self.to_html_output_file = html_path_file
                            self.export_to_html()
                        else:
                            print("Некорректный формат файла")
                    return True
                else:
                    return True
            # --- --- --- ---
        else:
            print("Анализатор завершил свою работу")
            return False


if __name__ == '__main__':
    while True:
        app = PriceAnalyzer("prices_dir")
        if not app.find_text():
            break
