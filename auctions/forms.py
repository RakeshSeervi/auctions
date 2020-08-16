from django import forms
from .models import Listing, Bid, Comment


class NewListing(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'basePrice', 'imageURL', 'category']

        widgets = {
            'description': forms.Textarea(attrs={'rows': '3', "cols": "40"}),
        }

class EmptyForm(forms.Form):
    pass


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bidValue']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']

        widgets = {
            'body': forms.Textarea(attrs={'rows': 3, 'cols': 40, 'placeholder': 'Your comment here...'})
        }