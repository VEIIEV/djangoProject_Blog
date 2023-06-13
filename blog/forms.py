from django import forms
from .models import Comment


# cleaned_data -- словарь, который хранит информацию из формы, прошедшую валидацию

# используется если НЕ происходит сохранение в БД ||Form
class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False,
                               widget=forms.Textarea)

    # форма для реализации поиска постов на сайте
class SearchForm(forms.Form):
    query = forms.CharField()


# используется для сохранения формы в БД || ModelForm
class CommentForm(forms.ModelForm):
    class Meta:
        model=Comment
        fields= ['name', 'email', 'body']


