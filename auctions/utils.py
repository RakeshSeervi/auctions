from django.db import connection

def callStoredProcedure(procedure, *args):
    with connection.cursor() as cursor:
        cursor.callproc(procedure, params=args)
        if(cursor.description):
            columns = [col[0] for col in cursor.description]
            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        
