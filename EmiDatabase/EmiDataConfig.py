import mysql.connector as SConection

baseConect = SConection.connect(host="localhost", user="root", passwd="", database="emidata")
Bpoint = baseConect.cursor(buffered=True)
