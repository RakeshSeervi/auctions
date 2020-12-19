from django.db import connection

def callStoredProcedure(procedure):
    with connection.cursor() as cursor:
        cursor.callproc(procedure)
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]