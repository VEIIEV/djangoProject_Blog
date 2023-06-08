from django import forms
from .models import Comment


# используется если НЕ происходит сохранение в БД ||Form
class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False,
                               widget=forms.Textarea)


# используется для сохранения формы в БД || ModelForm
class CommentForm(forms.ModelForm):
    class Meta:
        model=Comment
        fields= ['name', 'email', 'body']



