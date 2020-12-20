# Stored procedures


### Python function to call stored procedures
This is a generic function used to call the stored procedure . It accepts a parameter which has the stored procedure name .  

    def callStoredProcedure(procedure getOne = False):
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
    


## 3. To Create listing 
    delimiter //
    create procedure createListing(
    -> IN Title VARCHAR(64)  ,
    -> IN Description  LONGTEXT ,       
    -> IN ImageURL     VARCHAR(200) ,
    -> IN Creator_id   INT ,   
    -> IN BasePrice    INT ,
    -> IN Category     VARCHAR(11) ,  
    -> IN Timestamp    DATETIME ,   
    -> IN Active       INT,      
    -> )
    -> begin
    -> insert into auctions_listing 
    -> values (default , Title , Description , ImageURL , Creator_id , BasePrice , Category , Timestamp , Active , NULL);
    -> select * from auctions_listing 
    -> order by id desc limit 1;
    -> end //
