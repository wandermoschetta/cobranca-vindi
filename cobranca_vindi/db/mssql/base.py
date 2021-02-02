import pyodbc

from cobranca_vindi import setup

class Query(object):
  
    def _connect(self):
        return pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER={db_path};'
                              'DATABASE={db_name};UID={db_user};PWD={db_pass}').format(setup.db_path,setup.db_name,
                              setup.db_user, setup.db_pass)


    def __init__(self):
        self.conn = self._connect()
        self.cursor = self.conn.cursor()
        self.params = ""


    def select(self, sql):
        if sql != "":
            try:
                self.cursor.execute(sql)
            except ValueError:
                print("Error in the Statement SQL: {0}".format(sql))
            else:
                row = self.cursor.fetchall()
                return row
        else:
            return "Comando SQL não informado"


    def insert(self, sql):
        if sql != "":
            try:
                self.cursor.execute(sql)
            except ValueError:
                print("Error in the Statement SQL: {0}".format(sql))
            else:
                self.conn.commit()
                inserted_row = '[OK] Inserted data '
                return inserted_row
        else:
            return "Comando SQL não informado"


    def update(self, sql):
        if sql != "":
            try:
                self.cursor.execute(sql)
            except ValueError:
                print("Error in the Statement SQL: {0}".format(sql))
            else:
                self.conn.commit()
                updated_row = '[OK] Updated data '
                return updated_row
        else:
            return "Comando SQL não informado"


    def filter(self, **params):
        self.params = params
        if params.__len__() > 0:
            print(params)
        for key in params:
            print(params[key])
