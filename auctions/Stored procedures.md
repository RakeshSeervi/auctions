# Stored procedures

### Python function to call stored procedures

This is a generic function used to call the stored procedure . It accepts a parameter which has the stored procedure
name .

    def callStoredProcedure(procedure, *args):
        with connection.cursor() as cursor:
            cursor.callproc(procedure, params=args)
            if cursor.description:
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
    delimiter ;

## 2. To Create listing

    delimiter //
    create procedure createListing(
    -> IN Title VARCHAR(64)  ,
    -> IN Description  LONGTEXT ,       
    -> IN ImageURL     VARCHAR(200) ,
    -> IN Creator_id   INT ,   
    -> IN BasePrice    INT ,
    -> IN Category     VARCHAR(11) ,  
    -> IN Timestamp    DATETIME ,   
    -> IN Active       INT     
    -> )
    -> begin
    -> insert into auctions_listing 
    -> values (default , Title , Description , ImageURL , Creator_id , BasePrice , Category , Timestamp , Active , NULL);
    -> select * from auctions_listing 
    -> order by id desc limit 1;
    -> end //
    delimiter ;

## 3. To get listing by id

     delimiter //
     create procedure getListingById(in listingId int)
    -> begin
    -> select * from auctions_listing
    -> where id=listingId;
    -> end //
    delimiter ;

## 4. To get last bid of a listing

    delimiter //
    create procedure getLastBid(in listingId int)
    -> begin
    -> select * from auctions_bid where bidObject_id=listingId order by timestamp desc limit 1;
    -> end//
    delimter ;

## 5. To place bid

    delimter //
    create procedure placeBid(in listingId int, in bid int, in bidderId int, in time datetime)    
    -> begin
    -> insert into auctions_bid (bidObject_id, bidValue, bidder_id, timestamp) values (listingId, bid, bidderId, time);
    -> end //
    delimiter ;
