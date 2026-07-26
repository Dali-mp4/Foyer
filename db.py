import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="Dali",
        password="Dali2710",
        database="foyer_management"
    )
