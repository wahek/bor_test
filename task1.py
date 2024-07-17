import json

import pandas

FILE_NAME = 'test_task1/files/Прайс-лист AGC 2024.03.04 Опт.xlsx'
PULL_SHEETS = ["Автостекло. Аксессуары. Клей", "Российский автопром"]
PULL_COLUMNS = ["Вид стекла", "Еврокод", "Код AGC", "Старый Код AGC", "Наименование", "ОПТ"]
CATALOG = {
    "Автостекло. Аксессуары. Клей": "Иномарки",
    "Российский автопром": "Отечественные"
}
SERIAL_NAME_DICT = {
    "Вид стекла": "category",
    "Еврокод": "eurocode",
    "Код AGC": "art",
    "Старый Код AGC": "oldcode",
    "Наименование": "name",
    "ОПТ": "price"
}
ALTER_COL_NAME = "ОПТ"
ALTER_COL_VALUE = ("*", "Фиксированная")
ADD_COL_NAME = "catalog"


class Table:
    def __init__(self, filename: str = FILE_NAME,
                 pull_sheets: list | str = None,
                 pull_columns: list | str = None,
                 skip: int = 4) -> None:
        self.filename = filename
        self.pull_sheets = pull_sheets if pull_sheets is not None else PULL_SHEETS
        self.pull_columns = pull_columns if pull_columns is not None else PULL_COLUMNS
        self.skip = skip
        self.data: pandas.DataFrame | dict = self.load_data()

    def load_data(self) -> pandas.DataFrame | dict:
        return pandas.read_excel(self.filename, sheet_name=self.pull_sheets, skiprows=self.skip)

    def parse_data(self) -> None:
        """
        Метод для заполнения фрейма непустыми данными (операемся на еврокод)
        """
        if isinstance(self.data, dict):
            for sheet_name, df in self.data.items():
                self.data[sheet_name] = df[df['Еврокод'].notna()][self.pull_columns]
        else:
            self.data = self.data[self.pull_columns]


class Serializer:
    """Сериализатор для перегона DataFrame в json, и последующей записи в файл"""
    def __init__(self, catalog: str, filename: str = None) -> None:
        self.catalog = CATALOG[catalog]
        self.filename = filename if filename is not None else CATALOG[catalog]
        self.data = {}

    def to_json(self, data: pandas.DataFrame) -> list[dict]:
        """
        Перевод DataFrame в json, с изменением названий столбцов в зависимости от словаря ALTER_COL_NAME
        и значений из ALTER_COL_VALUE
        """
        res_json = []
        for index, row in data.iterrows():
            current_item = {ADD_COL_NAME: self.catalog}
            for name, value in row.items():
                if name == ALTER_COL_NAME and value == ALTER_COL_VALUE[0]:
                    current_item[SERIAL_NAME_DICT[name]] = ALTER_COL_VALUE[1]
                else:
                    current_item[SERIAL_NAME_DICT[name]] = value

            res_json.append(current_item)
        self.data = res_json
        return res_json

    def save_json(self) -> None:
        with open(self.filename + '.json', 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    tables = Table()
    tables.parse_data()

    if isinstance(tables.data, dict):
        for name, df in tables.data.items():
            current_data = Serializer(name)
            current_data.to_json(df)
            current_data.save_json()
    else:
        current_data = Serializer(tables.data.columns[0])
        current_data.save_json()
