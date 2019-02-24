from django import forms
from .models import Article, Category, Tag

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ['date_modified']
        widgets = {
            'view_count': forms.NumberInput(attrs={'min': '0'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        fields = ['name']
        model = Category

class TagForm(forms.ModelForm):
    class Meta:
        fields = ['name']
        model = Tag
