

import sqlite3
import pandas as pd


class SQL_handling:
    def __init__(self, connection: sqlite3.Connection, game_id: int):
        self.game_id = game_id
        self.conn = connection

    # Inserts new rows into SQL table

    def sql_insert(self, sql_list: list[tuple]) -> None:
        cur = self.conn.cursor()
        for tup in sql_list:
            cur.execute(f"INSERT INTO game_{self.game_id} VALUES (?, ?, ?, ?, ?, ?)", tup)


    # Clears the SQL table corresponding to game_id
    def clear_table(self) -> None:
        cur = self.conn.cursor()
        cur.execute(f"DELETE FROM game_{self.game_id}")

    
    # Converts a SQL table to csv document
    def convert_csv(self, folder_path: str) -> None:
        game_log = pd.read_sql_query(f"SELECT * FROM game_{self.game_id}", self.conn)
        game_log.to_csv(folder_path + f"game_{self.game_id}_log", index = False)
