import hashlib, uuid
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from markdownx.models import MarkdownxField

# Create your models here.
class Article(models.Model):
    """A blog post."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=1000, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True, help_text='Will be generated automatically if left blank.')
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, blank=True, null=True)
    tag = models.ManyToManyField('Tag', blank=True)
    author = models.CharField(max_length=500, default='G. Prasetyadi', help_text='Default is owner "G. Prasetyadi".')
    date_created = models.DateTimeField(default=timezone.now, help_text='YYYY-MM-DD HH:mm:ss')
    date_modified = models.DateTimeField(auto_now=True, editable=False)
    view_count = models.IntegerField(default=0)
    comment_enabled = models.BooleanField('Allow comments?', default=True)
    published = models.BooleanField('Publish now?', default=True)
    featured = models.BooleanField('Feature on home page?', default=True, help_text='Include on Latest Article.')
    summary = models.TextField(max_length=500)
    content = MarkdownxField()

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return self.title

    def save(self):
        if self.slug is None:
            self.slug = slugify(self.title)
        super().save()

    def get_absolute_url(self):
        """Return absolute url for viewing the article."""
        return reverse('blog:article', args=[str(self.date_created.year), str(self.slug)])

    def get_edit_url(self):
        """Return url for editing the article."""
        return reverse('blog:edit', args=[str(self.date_created.year), str(self.slug)])

class Category(models.Model):
    """An article's category."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    def save(self):
        if self.name is not None:
            self.name = slugify(str(self.name))
        super().save()

    def get_absolute_url(self):
        """Return url for listing all articles with this category."""
        return reverse('blog:category', args=[str(self.name)])

    def get_edit_url(self):
        """Return url for editing this category."""
        return reverse('blog:category-edit', args=[str(self.name)])

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'

class Tag(models.Model):
    """An article's tag."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    def save(self):
        if self.name is not None:
            self.name = slugify(str(self.name))
        super().save()
    
    def get_absolute_url(self):
        """Return url for listing all articles with this tag."""
        return reverse('blog:tag', args=[str(self.name)])

    def get_edit_url(self):
        """Return url for editing this tag."""
        return reverse('blog:tag-edit', args=[str(self.name)])

    class Meta:
        ordering = ['name']
