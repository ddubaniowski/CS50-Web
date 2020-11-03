from django import forms
from crispy_forms.helper import FormHelper

CATEGORY_CHOICES = (
    ('Not specified', 'Not specified'),
    ('Beauty', 'Beauty'),
    ('Clothing', 'Clothing'),
    ('Food', 'Food'),
    ('Sports', 'Sports'),
    ('Toys', 'Toys'),
    )

# new listing form
class NewListingForm(forms.Form):
    title = forms.CharField(label='Title', max_length=64)
    description = forms.CharField(label='Description', max_length=1000, empty_value="Describe the item your are listing.", widget=forms.Textarea)
    # start_bid = forms.DecimalField(label='Starting bid [$]', max_digits=12, decimal_places=2)
    start_bid = forms.FloatField()
    image_url = forms.URLField(label='Image URL', required=False)
    category = forms.CharField(label='Category', required=False, widget=forms.Select(choices=CATEGORY_CHOICES))
    helper = FormHelper()

# bid form
class BidForm(forms.Form):
    bid = forms.FloatField()
    helper = FormHelper()

# comment form
class CommentForm(forms.Form):
    comment = forms.CharField(max_length=500, widget=forms.Textarea)
    helper = FormHelper()