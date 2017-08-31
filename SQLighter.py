import sqlite3


class SQLighter:
    def __init__(self, database):
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def get_all(self):
        """ Получаем все строки """
        with self.connection:
            return self.cursor.execute('SELECT * FROM pics').fetchall()

    def get_image(self, photo_path):
        with self.connection:
            return self.cursor.execute('SELECT * FROM pics WHERE path = ?', (photo_path,)).fetchone()

    def add_photo(self, path, small_id, full_id):
        with self.connection:
            self.cursor.execute('INSERT INTO pics (path, small_id, full_id) VALUES (?, ?, ?)',
                                (path, small_id, full_id))
            self.connection.commit()

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()
