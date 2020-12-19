# Stored procedures


### Python function to call stored procedures
This is a generic function used to call the stored procedure . It accepts a parameter which has the stored procedure name .  

    def callStoredProcedure(procedure):
        with connection.cursor() as cursor:
            cursor.callproc(procedure)
            columns = [col[0] for col in cursor.description]
            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
            

## 1. To get all the active listings 
     delimiter //
     create procedure getAllActiveListings()
    -> begin
    -> select * from auctions_listing
    -> where active=True
    -> order by timestamp
    -> desc; end //
    
