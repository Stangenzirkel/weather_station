import sys
import datetime as dt
import sqlite3
import schedule
import time


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + dt.timedelta(n)


def day_exists(time_from_epoch):
    con = sqlite3.connect("ws_database.db")

    req = """
          SELECT *
          FROM long_term_data
          WHERE time_from_epoch = ?
          """

    cur = con.cursor()
    result = list(cur.execute(req, (time_from_epoch, )))

    return len(result)


def format_data_one_day(date):
    con = sqlite3.connect("ws_database.db")
    day_start_time = int(dt.datetime.combine(date, dt.time()).timestamp())
    day_end_time = day_start_time + 86400

    req = """
          SELECT max_t, min_t, time_from_epoch
          FROM short_term_data
          WHERE ? < time_from_epoch < ?
          """

    cur = con.cursor()
    result = list(cur.execute(req, (day_start_time, day_end_time)))
    max_t = max(result, key=lambda x: int(x[0]))[0]
    min_t = min(result, key=lambda x: int(x[1]))[1]

    if not day_exists(day_start_time):
        req = """
              INSERT INTO long_term_data(max_t, min_t, time_from_epoch)
              VALUES(?,?,?)
             """

        con.execute(req, (max_t, min_t, day_start_time))
        con.commit()

    req = """
          DELETE FROM short_term_data
          WHERE ? < time_from_epoch < ?
          """

    cur.execute(req, (day_start_time, day_end_time))
    con.commit()


def end_day_format_data():
    con = sqlite3.connect("ws_database.db")
    day_start_time = int(dt.datetime.combine(dt.datetime.now().date() - dt.timedelta(days=1), dt.time()).timestamp())
    day_end_time = day_start_time + 86400

    req = """
          SELECT max_t, min_t, time_from_epoch
          FROM short_term_data
          WHERE ? < time_from_epoch < ?
          """

    cur = con.cursor()
    result = list(cur.execute(req, (day_start_time, day_end_time)))
    max_t = max(result, key=lambda x: int(x[0]))[0]
    min_t = min(result, key=lambda x: int(x[1]))[1]

    if not day_exists(day_start_time):
        req = """
              INSERT INTO long_term_data(max_t, min_t, time_from_epoch)
              VALUES(?,?,?)
              """

        con.execute(req, (max_t, min_t, day_start_time))
        con.commit()


def format_data():
    print("Data formatting...")
    con = sqlite3.connect("ws_database.db")

    req = """
          SELECT MIN(time_from_epoch) AS min
          FROM short_term_data
          """

    cur = con.cursor()
    result = list(cur.execute(req))

    start_date = dt.datetime.fromtimestamp(result[0][0]).date()
    end_date = dt.datetime.now().date() - dt.timedelta(days=1)

    if start_date < end_date:
        for single_date in daterange(start_date, end_date):
            try:
                print(single_date.ctime())
                format_data_one_day(single_date)

            except Exception:
                pass

    end_day_format_data()
    print("Data formatting complete")


if __name__ == "__main__":
    schedule.every().day.at("00:00").do(format_data)

    while True:
        schedule.run_pending()
        time.sleep(5)

