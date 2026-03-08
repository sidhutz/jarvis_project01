import csv
import sqlite3

con = sqlite3.connect("jarvis.db")
cursor = con.cursor()


query = "CREATE TABLE IF NOT EXISTS sys_command(id integer primary key, name VARCHAR(100), path VARCHAR(1000))"
cursor.execute(query)

# query = "INSERT INTO sys_command VALUES (null,'Cap Cut', 'C:\\Users\\Hp\\AppData\\Local\\CapCut\\Apps\\CapCut.exe')"
# cursor.execute(query)
# con.commit()

# query = "CREATE TABLE IF NOT EXISTS web_command(id integer primary key, name VARCHAR(100), url VARCHAR(1000))"
# cursor.execute(query)

# query = "INSERT INTO web_command VALUES (null,'youtube', 'https://www.youtube.com/')"
# cursor.execute(query)
# con.commit()

# cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (id integer primary key, name VARCHAR(200), mobile_no VARCHAR(255), email VARCHAR(255) NULL, address VARCHAR(255) NULL)''')

# desired_columns_indices = [0, 1]

# with open('contacts.csv', 'r', encoding='utf-8') as csvfile:
#     csvreader = csv.reader(csvfile)

#     next(csvreader)  # header skip

#     for row in csvreader:
#         if len(row) >= 2 and row[0] and row[1]:  # empty check
#             name = row[0].strip()
#             mobile = row[1].strip()

#             cursor.execute('''
#                 INSERT INTO contacts (name, mobile_no)
#                 VALUES (?, ?)
#             ''', (name, mobile))

# con.commit()
# con.close()

# query = 'kunal'
# query = query.strip().lower()

# cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
# results = cursor.fetchall()
# print(results[0][0])

