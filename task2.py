import pandas


class JsonDataCatalog:
    ALTER_COLUMNS_NAME = {'price': 'client_price'}
    ALTER_COLUMNS_VALUE = {'ветровое': (1000, .05), 'заднее': (800, .07), 'боковое': (0, .1)}

    def __init__(self, filename: str):
        self.filename = filename
        self.data = self.__fill_data()

    def __fill_data(self):
        with open(self.filename, 'r', encoding='utf-8') as f:
            return pandas.read_json(f)

    def rename_columns(self):
        self.data.rename(columns=self.ALTER_COLUMNS_NAME, inplace=True)

    def __apply_value(self, depend_col: tuple, alter_col: tuple, exception_value: str):
        """Передаём значение зависимых столбцов и значения для замены:
        ('Название столбца', 'Значение от которого зависим')
        """
        mask = (self.data[depend_col[0]] == depend_col[1]) & (self.data[alter_col[0]] != exception_value)
        self.data.loc[mask, alter_col[0]] = \
            (self.data.loc[mask, alter_col[0]] + self.ALTER_COLUMNS_VALUE[alter_col[1]][0]) * \
            (1 + self.ALTER_COLUMNS_VALUE[alter_col[1]][1])

    def apply_value(self, depend_col: str = 'category',
                    alter_col: str = 'client_price',
                    exception_value: str = 'Фиксированная'):
        """
        Метод для изменения значений в alter_col в зависимости от значения в depend_col
        Значения для изменений хранить в словарях внутри класса
        """
        for item in self.ALTER_COLUMNS_VALUE.keys():
            self.__apply_value((depend_col, item), (alter_col, item), exception_value)

    def save_xlsx(self, filename: str):
        self.data.to_excel(filename + '.xlsx')


if __name__ == '__main__':
    catalog = JsonDataCatalog('Иномарки.json')
    catalog.rename_columns()
    catalog.apply_value()
    print(catalog.data)
    catalog.save_xlsx('Иномарки')
    catalog1 = JsonDataCatalog('Отечественные.json')
    catalog1.rename_columns()
    catalog1.apply_value()
    catalog.save_xlsx('Отечественные')
