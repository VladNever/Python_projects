import mysql.connector
from mysql.connector import errorcode
from datetime import date
import random

DB_NAME = 'SPA_Table'

TABLES = {}
TABLES['homepage_table'] = """
CREATE TABLE homepage_table ( 
    date DATE NOT NULL, 
    title VARCHAR(14) NOT NULL,
    quantity INT NOT NULL,
    distance INT NOT NULL
)   ENGINE = InnoDB
"""

def establish_connection():
    cnx = mysql.connector.connect(user='spauser', password='password')
    return cnx

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

def use_database(cnx):
    cursor = cnx.cursor()
    try:
        cursor.execute("USE {}".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(DB_NAME))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            print("Database {} created successfully.".format(DB_NAME))
            cnx.database = DB_NAME
        else:
            print(err)
            exit(1)
    cursor.close()

def create_table(cnx):
    cursor = cnx.cursor()
    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print("Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")
    cursor.close()

def insert_rows(cnx):
    cursor = cnx.cursor()
    title_tuple = ('Moskow', 'Arkhangelsk', 'Irkutsk', 'Krasnoyarsk', 'Omsk')
    add_row = ("""

    INSERT INTO homepage_table
    (date, title, quantity, distance)
    VALUES (%s, %s, %s, %s)
    
    """)

    for i in range(5):
        year = random.randint(2000, 2021)
        month = random.randint(1, 12)
        day = random.randint(1, 30)

        date_to = date(year, month, day).strftime("%Y.%m.%d")
        title =  title_tuple[random.randint(0, 4)]
        quantity = random.randint(1, 10)
        distance = random.randint(1, 100)

        row = (date_to, title, quantity, distance)    
        cursor.execute(add_row, row)
        cnx.commit()
    cursor.close()

def get_query(cnx, form_values):
    cursor = cnx.cursor()

    selected_column = form_values['selected_column']
    selected_condition = form_values['selected_condition']
    filtration_value = form_values['filtration_value']
    sorted_column = form_values['sorted_column']
    sorting_direction = form_values['sorting_direction']

    if selected_condition == 'contains':
        selected_condition = 'LIKE'
        filtration_value = r'%{value}%'.format(value=filtration_value)

    if sorting_direction == 'decreasing':
        sorting_direction = 'DESC'
    else:
        sorting_direction = 'ASC'

    if (
        selected_column == 'choose column' or 
        selected_condition == 'choose condition' or
        filtration_value == 'enter value'
        ):
        selected_rows = ("""

        SELECT * FROM homepage_table
        ORDER BY {sorted_column} {sorting_direction}

        """.format(sorted_column=sorted_column, sorting_direction=sorting_direction)
        )
    else:
        try:
            selected_rows = ("""

            SELECT * FROM homepage_table
            WHERE {column} {condition} '{value}'
            ORDER BY {sorted_column} {sorting_direction}


            """.format(column=selected_column, condition=selected_condition, value=filtration_value, 
            sorted_column=sorted_column, sorting_direction=sorting_direction)
            )
        except:
            query = [0,0,0,0]
            return query

    cursor.execute(selected_rows)
    query = []
    for [date, title, quantity, distance] in cursor:
        date = date.strftime("%Y.%m.%d")
        query.append([date, title, quantity, distance])
    return query

if __name__ == "__main__":
    cnx = establish_connection()
    use_database(cnx)
    create_table(cnx)
    insert_rows(cnx)
    cnx.close()