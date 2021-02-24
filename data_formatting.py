import sys
import datetime as dt
import sqlite3
import schedule
import time
from clear_data import clear_short_term_data


def format_data():
    print("data formatting...")
    time = int(dt.datetime.now().timestamp())

    try:
        con = sqlite3.connect("ws_database.db")

        req = """
              SELECT tmp, hmd, prs, time_from_epoch
              FROM short_term_data
              WHERE (time_from_epoch - ?) < 86400
              """

        cur = con.cursor()
        result = list(cur.execute(req, (time,)))

        max_tmp = max(result, key=lambda x: float(x[0]))[0]
        min_tmp = min(result, key=lambda x: float(x[0]))[0]
        hmd = min(result, key=lambda x: float(x[1]))[1]
        prs = min(result, key=lambda x: float(x[2]))[2]

        req = """
              INSERT INTO long_term_data(max_tmp, min_tmp, hmd, prs, time_from_epoch)
              VALUES(?,?,?,?,?)
              """

        con.execute(req, (max_tmp, min_tmp, hmd, prs, time, time))
        con.commit()

        req = """
              DELETE
              FROM short_term_data
              WHERE (time_from_epoch - ?) > 86400
              """

        cur.execute(req, (time,))
        con.commit()

        print('data formatting success')

    except Exception as error:
        print(error.__class__.__name__ + ': ' + error)


if __name__ == "__main__":
    schedule.every().day.at("00:00").do(format_data)

    while True:
        schedule.run_pending()
        time.sleep(0.5)

