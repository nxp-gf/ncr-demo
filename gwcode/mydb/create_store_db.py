# coding=utf-8
import sqlite3
import sys

# 连接
conn = sqlite3.connect('store.db')
conn.text_factory = str
c = conn.cursor()

# 创建表
c.execute('''DROP TABLE IF EXISTS STORE''')
c.execute('''CREATE TABLE STORE (ID INTEGER PRIMARY KEY AUTOINCREMENT, CameraID INT NOT NULL, PersonName TEXT NOT NULL, TimePersonIn datetime, TimePersonOut datetime);''')
# 提交！！！
conn.commit()

def get_db():
    db = sqlite3.connect('store.db')

    db.row_factory = sqlite3.Row
    return db

def get_day_time(time_from_user, modifier):
    db = get_db()
    startTime = db.execute("SELECT datetime(?,?)", (time_from_user,modifier))
    person_in = startTime.fetchall()
    start_day = person_in[0][0]
    return start_day

def add_test_record(testData):
	db = get_db()
	c = db.cursor()
	c.executemany('INSERT INTO STORE(CameraID, PersonName, TimePersonIn, TimePersonOut) VALUES (?,?,?,?)', testData)
	db.commit()
	db.close()

def build_test_data(CameraID, personName, TimePersonIn, TimePersonOut, num):
	testData = []
	for i in range(0, num):
		timeIn = get_day_time(TimePersonIn, '+' + str(i) + ' minute')
		timeOut = get_day_time(TimePersonOut, '+' + str(i) + ' minute')
		record = (CameraID, personName, timeIn, timeOut)
		testData.append(record)
	add_test_record(testData)

# 查询方式一
def query_test_db():
	db = get_db()
	record_cursor = db.execute("SELECT * FROM STORE")
	records = record_cursor.fetchall()
	for row in records:
		print(row)
	#for row in c.execute("SELECT * FROM STORE WHERE CameraID=(?) AND TimePersonIn between (?) and (?)", (1, "2019-02-19 00:00:01", "2019-02-19 12:00:00")):

if __name__ == "__main__":
	build_test_data(1,"abc1", "2019-02-19 08:00:00", "2019-02-19 08:59:59", 30)
	build_test_data(1,"abc2", "2019-02-19 09:00:00", "2019-02-19 09:59:59", 35)
	build_test_data(1,"abc1", "2019-02-19 10:00:00", "2019-02-19 10:59:59", 40)
	build_test_data(1,"abc2", "2019-02-19 11:00:00", "2019-02-19 11:59:59", 50)
	build_test_data(1,"abc2", "2019-02-19 12:00:00", "2019-02-19 12:59:59", 55)
	build_test_data(1,"abc1", "2019-02-19 13:00:00", "2019-02-19 13:59:59", 59)
	build_test_data(1,"abc1", "2019-02-19 14:00:00", "2019-02-19 14:59:59", 52)
	build_test_data(1,"abc1", "2019-02-19 15:00:00", "2019-02-19 15:59:59", 46)
	build_test_data(1,"abc2", "2019-02-19 16:00:00", "2019-02-19 16:59:59", 50)
	build_test_data(1,"abc1", "2019-02-19 17:00:00", "2019-02-19 17:59:59", 51)
	build_test_data(1,"abc2", "2019-02-19 18:00:00", "2019-02-19 18:59:59", 26)
	build_test_data(1,"abc1", "2019-02-19 19:00:00", "2019-02-19 19:59:59", 52)
	build_test_data(1,"abc1", "2019-02-19 20:00:00", "2019-02-19 20:59:59", 36)
	build_test_data(1,"abc2", "2019-02-19 21:00:00", "2019-02-19 21:59:59", 21)
	query_test_db()


