from django.contrib import admin
from .models import Listing, User, Bid, Comment


class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title")


class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username")


class BidAdmin(admin.ModelAdmin):
    list_display = ('id', 'bidder', 'bidObject', 'bidValue')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'object')


# Register your models here.
admin.site.register(Listing, ListingAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)


# Customizing the admin page
admin.site.site_header = "Auctions Admin"
admin.site.site_title = "Auctions Admin Portal"
admin.site.index_title = "Welcome to  Auctions Admin Page"
