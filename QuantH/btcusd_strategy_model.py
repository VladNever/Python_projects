import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas as pd

class Model:
    def __init__(self):
        self.user = 'postgres'
        self.password = 'password'
        self.host = 'localhost'
        self.database_name = 'strategydb'
        self.create_database(self)
        self.create_tables(self)

    @staticmethod
    def create_database(self):
        try:
            # Подключение к существующей базе данных
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          )
            # Команда 'CREATE DATABASE' не может выполняться в блоке 
            # транзакций. Для этого необходимо выполнить следующую команду:                              
            connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)                                          
            # Курсор для выполнения операций с базой данных
            cursor = connection.cursor()
            sql_create_database = 'CREATE DATABASE {0}'.format(self.database_name)
            cursor.execute(sql_create_database)
            print("База данных создана")
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Соединение с PostgreSQL закрыто")
    @staticmethod
    def create_tables(self):
        try:
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          database=self.database_name
                                          )
            cursor = connection.cursor()

            # SQL-запрос для создания новой таблицы
            create_table_query = '''CREATE TABLE positions
                                    (
                                    id SERIAL PRIMARY KEY,     
                                    date TIMESTAMP,
                                    order_side VARCHAR(5),
                                    order_quantity REAL,
                                    position_qnt REAL,
                                    price REAL,
                                    pos_id INTEGER
                                    ); 
                                  '''
            # Выполнение команды: это создает новую таблицу
            cursor.execute(create_table_query)
            connection.commit()

            print("Все таблицы успешно созданы")
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Соединение с PostgreSQL закрыто")        

    def insert_rows(self, date, order_side, order_quantity, position_qnt, price, pos_id):
        try:
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          database=self.database_name
                                          )
            cursor = connection.cursor()

            # SQL-запрос для создания новой таблицы
            insert_query = '''INSERT INTO positions (date, order_side, order_quantity, position_qnt, price, pos_id)
                                VALUES ('{0}', '{1}', {2}, {3}, {4}, {5}); 
                            '''.format(date, order_side, order_quantity, position_qnt, price, pos_id)
            cursor.execute(insert_query)
            connection.commit()

            print("Запись успешно добавлена")
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Соединение с PostgreSQL закрыто")          
    
    def get_positions_result(self):
        try:
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          database=self.database_name
                                          )
            cursor = connection.cursor()

            # SQL-запрос для получения данных по позициям
            query = '''SELECT MAX(date) as position_closed_date, pos_id,  SUM(-order_quantity*price) as pos_profit_lose
                                    FROM positions
                                    GROUP BY pos_id
                                    HAVING COUNT(*) > 1
                                    ORDER BY pos_id;; 
                                '''

            cursor.execute(query)
            positions_results = cursor.fetchall()
            print("Данные получены")
            return positions_results
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Соединение с PostgreSQL закрыто")           

    def get_avg_entry_price(self):
        try:
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          database=self.database_name
                                          )
            cursor = connection.cursor()

            # SQL-запрос для получения данных о средней цене входа
            query = '''SELECT AVG(price) AS avg_entry_price FROM positions 
                        WHERE position_qnt != 0;
                    '''

            cursor.execute(query)
            avg_entry_price = cursor.fetchone()
            print("Данные получены")
            return avg_entry_price
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Соединение с PostgreSQL закрыто")     

    def get_avg_exit_price(self):
        try:
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          database=self.database_name
                                          )
            cursor = connection.cursor()

            # SQL-запрос для получения данных о средней цене выхода
            query = '''SELECT AVG(price) AS avg_exit_price FROM positions 
                        WHERE position_qnt = 0;
                    '''

            cursor.execute(query)
            avg_entry_price = cursor.fetchone()
            print("Данные получены")
            return avg_entry_price
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Соединение с PostgreSQL закрыто")  

    def get_bot_profit_lose(self):
        try:
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          database=self.database_name
                                          )
            cursor = connection.cursor()

            # SQL-запрос для получения данных о средней цене выхода
            query = '''SELECT SUM(-order_quantity*price) as bot_profit_lose
                        FROM positions
                    '''

            cursor.execute(query)
            bot_profit_lose = cursor.fetchone()
            print("Данные получены")
            return bot_profit_lose
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Соединение с PostgreSQL закрыто")  

if __name__ == "__main__":
    strategydb = Model()
    # test
    # strategydb.insert_rows('2021-06-30 20:00:00', 'BUY', 0.1, 0.1, 34823.386719, 1)