from django import forms

class SearchForm(forms.Form):
    song_id = forms.CharField(label='Song ID', required=False, max_length=100)
    title = forms.CharField(required=False, max_length=100)
    artist = forms.CharField(required=False, max_length=100)
