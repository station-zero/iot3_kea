import sqlite3
from datetime import datetime
list_of_ids = []

dbcon = sqlite3.connect('database.db')
cursor = dbcon.cursor()
cursor.execute("SELECT *, ROW_NUMBER() OVER(ORDER BY Id) AS NoId FROM data")
rows = cursor.fetchall()


year = datetime.now().strftime('%Y')
month = datetime.now().strftime('%m')
day = datetime.now().strftime('%d')

month = int(month) -1
if month == 0:
    month = 12
    year = int(year) - 1

date_to_compare = str(year) + str(month) + str(day)

file_name = "test_" + str(year) + "_"  + str(month) + "_" + str(day) + ".txt"

with open("backup/" + file_name, 'w') as file:
    for row in rows:
        date = str(row[4]).split("-")
        date_data = date[0].replace("/","")

        if int(date_data) <  int(date_to_compare):
            file.write(str(row) + "\n")
            list_of_ids.append(row[7])


for id in list_of_ids:

    sql = "DELETE FROM data WHERE ROWID=?"

    cursor.execute(sql,(id,))
    dbcon.commit()

dbcon.close()
