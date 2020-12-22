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
    begin
        select * from auctions_listing
            where active=True
                order by timestamp desc; 
    end //
    delimiter ;

## 2. To Create listing

    delimiter //
    create procedure createListing(
    IN Title VARCHAR(64)  ,
    IN Description  LONGTEXT ,       
    IN ImageURL     VARCHAR(200) ,
    IN Creator_id   INT ,   
    IN BasePrice    INT ,
    IN Category     VARCHAR(11) ,  
    IN Timestamp    DATETIME ,   
    IN Active       INT     
    )
    begin
        insert into auctions_listing 
            values (default , Title , Description , ImageURL , Creator_id , BasePrice , Category , Timestamp , Active , NULL);
        select * from auctions_listing 
            order by id desc limit 1;
    end //
    delimiter ;

## 3. To get listing by id

    delimiter //
    create procedure getListingById(in listingId int)
    begin
        select * from auctions_listing
            where id=listingId;
    end //
    delimiter ;

## 4. To get last bid of a listing

    delimiter //
    create procedure getLastBid(in listingId int)
    begin
        select * from auctions_bid 
            where bidObject_id=listingId 
                order by timestamp desc 
                    limit 1;
    end//
    delimter ;

## 5. To place bid

    delimter //
    create procedure placeBid(in listingId int, in bid int, in bidderId int, in time datetime)    
    begin
        insert into auctions_bid (bidObject_id, bidValue, bidder_id, timestamp) 
            values (listingId, bid, bidderId, time);
    end //
    delimiter ;

## 6. To close bid

    delimter //
    create procedure closeBid(in listingId int)
    begin
        update auctions_listing 
            set active=False 
                where id=listingId;
    end //
    delimiter ;

## 7. To add watcher

    delimiter //
    create procedure addWatcher (in listingId int, in userId int)
    begin
        insert into auctions_watcher values (default, listingId, userId);
    end //
    delimiter ;

## 8. To remove watcher

    delimiter //
    create procedure removeWatcher (in listingId int, in userId int)
    begin
        delete from auctions_watcher 
            where listing_id=listingId and user_id=userId;
    end//
    delimiter ;

## 9. To get watchlist by user Id
 
    delimiter //
    create procedure getWatchlist (in userId int)
    begin
        select * from auctions_listing where active=True and id in  (select listing_id from auctions_watcher 
            where user_id=userId);
    end//
    delimiter ;

## 10. To add a comments to a listing 

    delimiter //
    create procedure addComment (in listingId int,in comment varchar(200) , in userId int)
    begin
        insert into auctions_comment values (default, userId , comment , listingId , NOW());
    end //
    delimiter ;

## 11. To get the comments of a listing 

    delimiter //
    create procedure getCommentsByListingId(in listingId int)
    begin 
        select * from auctions_comment 
            where object_id=listingId;
    end//
    delimiter;

## 12. To get listing by user and category

    delimiter //
    create procedure getListingByUser(in userId int , in cat varchar(20))
    begin
        if cat is NULL then
        select * from auctions_listing
            where creator_id=userId
            order by timestamp desc; 

        else
        select * from auctions_listing
            where creator_id=userId and category=cat
            order by timestamp desc ;

        end if;
    end //

    delimiter ;

# Trigger

## To update winner

    delimiter //
    create trigger updateWinner 
    before update 
    on auctions_listing 
    for each row 
    begin 
        if new.active=False then 
            set new.winner_id = (
                select bidder_id from auctions_bid 
                    where bidObject_id=old.id 
                        order by bidValue desc 
                            limit 1); 
        end if; 
    end//
    delimiter ;
