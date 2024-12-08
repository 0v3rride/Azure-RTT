import pymssql
import pymysql 
import re
from rich.table import Table
from rich.console import Console

# https://learn.microsoft.com/en-us/sql/connect/ado-net/sql/azure-active-directory-authentication?view=sql-server-ver16
# https://learn.microsoft.com/en-us/azure/azure-sql/database/authentication-aad-overview?view=azuresql

def ParseConnectionString(connectionString):
    connectionData = {
        "server": None,
        "database": None,
        "user": None,
        "password": None
    }

    for data in str(connectionString).split(";"):
        if re.search("Server=.*", data, re.IGNORECASE):
            serverPart = data.split("=")[1].split(":")[1]

            if re.search(".*,.*", serverPart, re.IGNORECASE):
                connectionData["server"] = serverPart.split(",")[0]
        elif re.search("User ID=.*", data, re.IGNORECASE):
            connectionData["user"] = data.split("=")[1]
        elif re.search("Password=.*", data, re.IGNORECASE):
            connectionData["password"] = data.split("=")[1]
        elif re.search("Initial Catalog=.*", data, re.IGNORECASE):
            connectionData["database"] = data.split("=")[1]
    
    return connectionData

def ExecuteQuery(cursor, query):
    cursor.execute(query)

    table = Table()
  
    for header in cursor.description:
        table.add_column(header[0])

    for row in cursor:
        table.add_row(*[str(item) for item in row]) 
            

    Console().print(table)


def DumpAll(cursor):
    dbInfo = {

    }

    # get database names
    databaseNames = []

    cursor.execute("select * from sys.databases")

    for row in cursor:
        values = []
        values.append(row[0])
        databaseNames.append(values)

    # get table names
    for db in databaseNames:
        tableNames = []
        cursor.execute(f"select table_name from information_schema.tables where table_catalog = '{db[0]}'")

        if cursor:
            for table in cursor:
                tableNames.append(table[0])
            
            dbInfo.update({db[0]: tableNames})
        else:
            pass
    
    # dump all tables in all dbs
    for db, tables in dbInfo.items():
        if len(tables) > 0:
            for table in tables:
                try:
                    cursor.execute(f"select * from {db}.dbo.{table}")
                    
                    table = Table(title=f"Database: {db} - Table: {table}")
            
                    for header in cursor.description:
                        table.add_column(header[0])

                    for row in cursor:
                        table.add_row(*[str(item) for item in row]) 
                    
                    Console().print(table)
                except:
                    pass

def Shell(cursor):
    try:
        while(True):
            table = Table()
            query = input("Query >> ")

            if query == "exit":
                exit()
            
            cursor.execute(query)

            for header in cursor.description:
                table.add_column(header[0])

            for row in cursor:
                table.add_row(*[str(item) for item in row]) 
                
            Console().print(table)
    except Exception as e:
        pass
    except KeyboardInterrupt as ki:
        exit()


def main(connectionstring, servername, database, user, password, query, dumpall, interactive, accesstoken, useragent):

    response = None

    try:
        connection = None

        connectionData = {
            "server": None,
            "database": None,
            "user": None,
            "password": None
        }


        if connectionstring:
            connectionData = ParseConnectionString(connectionstring)
        else:
            connectionData["server"] = servername
            connectionData["database"] = database
            connectionData["user"] = user
            connectionData["password"] = password

        # https://pymssql.readthedocs.io/en/stable/azure.html
        try:
            connection = pymssql.connect(
                server=connectionData["server"],
                database=connectionData["database"],
                user=connectionData["user"],
                password=connectionData["password"]
            )

            cursor = connection.cursor()

            if query:
                ExecuteQuery(cursor, query)
            elif dumpall:
                DumpAll(cursor)
            elif interactive:
                Shell(cursor)

            connection.close()
        except pymssql.exceptions.OperationalError as oe:
            response = oe.args[0][1].decode("utf-8")

    except Exception as e:
        response = e
    finally:
        return response