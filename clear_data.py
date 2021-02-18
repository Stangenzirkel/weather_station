import sqlite3


def clear_long_term_data():
    con = sqlite3.connect("ws_database.db")

    req = """
          DELETE
          FROM long_term_data
          """

    con.execute(req)
    con.commit()


def clear_short_term_data():
    con = sqlite3.connect("ws_database.db")

    req = """
          DELETE
          FROM short_term_data
          """

    con.execute(req)
    con.commit()


if __name__ == "__main__":
    clear_long_term_data()
    clear_short_term_data()


