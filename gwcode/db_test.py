import sqlite3
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

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

def get_person_new_in(next_time, this_time):
    new_in = next_time - this_time
    if new_in < 0:
        new_in = 0
    return new_in

def query_overall_person_count(time_from_user):
    db = get_db()
    startTime = get_day_time(time_from_user, 'start of day')
    person_in_cursor = db.execute("SELECT * FROM STORE WHERE CameraID=(?) AND TimePersonIn between (?) and (?)", (1, startTime, time_from_user))
    person_in = person_in_cursor.fetchall()
    person_in_count = len(person_in)
    person_out_cursor = db.execute("SELECT * FROM STORE WHERE CameraID=(?) AND TimePersonOut between (?) and (?)", (2, startTime, time_from_user))
    person_out = person_out_cursor.fetchall()
    person_out_count = len(person_out)
    db.commit()
    current_person = person_in_count - person_out_count
    db.close()
    return current_person

def query_overall_person_in_count(time_from_user):
    db = get_db()
    startTime = get_day_time(time_from_user, 'start of day')
    person_in_cursor = db.execute("SELECT * FROM STORE WHERE CameraID=(?) AND TimePersonIn between (?) and (?)", (1, startTime, time_from_user))
    person_in = person_in_cursor.fetchall()
    person_in_count = len(person_in)
    db.commit()
    db.close()
    return person_in_count

def query_overall_person_multicount(time_from_user):
    db = get_db()
    person_count = []
    current_person = query_overall_person_count(time_from_user)
    person_count.append(current_person)
    for i in range(1, 5):
        user_time = get_day_time(time_from_user, '-' + str(i) + ' minute')
        count = query_overall_person_count(user_time)
        person_count.append(count)
    db.commit()
    db.close()
    return person_count

# Metrics here temporary defined to be hours
def query_overall_history_hour_person_count(start_time, length):
    time_next = get_day_time(start_time, '+' + str(1) + ' hour')
    start_count = query_overall_person_count(start_time) + get_person_new_in(query_overall_person_in_count(time_next), query_overall_person_in_count(start_time))
    person_count = []
    person_count.append(start_count)
    for i in range(1, length):
        user_time = get_day_time(start_time, '+' + str(i) + ' hour')
        time_next = get_day_time(user_time, '+' + str(1) + ' hour')
        count = query_overall_person_count(user_time) + get_person_new_in(query_overall_person_in_count(time_next), query_overall_person_in_count(user_time))
        person_count.append(count)
    return person_count

def query_shelf_person_count(shelfid, time_from_user):
    db = get_db()
    startTime = get_day_time(time_from_user, 'start of day')
    person_in_cursor = db.execute("SELECT * FROM STORE WHERE CameraID=(?) AND TimePersonIn !=0 AND TimePersonIn between (?) and (?)", (shelfid, startTime, time_from_user))
    person_in = person_in_cursor.fetchall()
    person_in_count = len(person_in)
    person_out_cursor = db.execute("SELECT * FROM STORE WHERE CameraID=(?) AND TimePersonOut !=0 AND TimePersonOut between (?) and (?)", (shelfid, startTime, time_from_user))
    person_out = person_out_cursor.fetchall()
    person_out_count = len(person_out)
    db.commit()
    current_person = person_in_count - person_out_count
    db.close()
    return current_person

def query_shelf_person_multicount(shelfid, time_from_user):
    current_count = query_shelf_person_count(shelfid, time_from_user)
    current_multi_count = []
    current_multi_count.append(current_count)
    for i in range(1, 5):
        user_time = get_day_time(time_from_user, '-' + str(i) + ' minute')
        count = query_shelf_person_count(shelfid, user_time)
        current_multi_count.append(count)
    return current_multi_count

def query_shelf_person_in_count(shelfid, time_from_user):
    db = get_db()
    startTime = get_day_time(time_from_user, 'start of day')
    person_in_cursor = db.execute("SELECT * FROM STORE WHERE CameraID=(?) AND TimePersonOut !=0 AND TimePersonIn between (?) and (?)", (shelfid, startTime, time_from_user))
    person_in = person_in_cursor.fetchall()
    person_in_count = len(person_in)
    db.commit()
    db.close()
    return person_in_count

def query_shelf_history_hour_person_count(shelfid, start_time, length):
    time_next = get_day_time(start_time, '+' + str(1) + ' hour')
    start_count = query_shelf_person_count(shelfid, start_time) + get_person_new_in(query_shelf_person_in_count(shelfid, time_next), query_shelf_person_in_count(shelfid, start_time))
    person_count = []
    person_count.append(start_count)
    for i in range(1, length):
        user_time = get_day_time(start_time, '+' + str(i) + ' hour')
        time_next = get_day_time(user_time, '+' + str(1) + ' hour')
        count = query_shelf_person_count(shelfid, user_time) + get_person_new_in(query_shelf_person_in_count(shelfid, time_next), query_shelf_person_in_count(shelfid, user_time))
        person_count.append(count)
    return person_count

def db_test():
    print(query_overall_person_multicount("2019-02-19 23:00:00"))
    print(query_overall_history_hour_person_count("2019-02-19 08:00:00", 10))

    print(query_shelf_person_multicount(1, "2019-02-19 10:00:00"))
    print(query_shelf_history_hour_person_count(1, "2019-02-19 08:00:00", 10))

if __name__ == "__main__":
    db_test()
