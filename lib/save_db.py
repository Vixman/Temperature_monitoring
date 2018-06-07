import MySQLdb as mdb

con = mdb.connect("localhost",
                    "pi_insert",
                    "raspberry",
                    "Temp_monitoring");
cursor = con.cursor()

    
sql = "INSERT INTO temp_monitor(temperature, sensor) \VALUES ('%s', '%s')" % \
(122122, 'sensor1')
cursor.execute(sql)
sql = []
con.commit()
con.close()
