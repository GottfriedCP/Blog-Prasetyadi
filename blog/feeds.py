from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Atom1Feed
from blog.models import Article
import datetime

class RssLatestArticlesFeed(Feed):
    title = "Prasetyadi.name feed"
    link = '/'
    description = "Latest blog posts from Prasetyadi.name"
    author_name = 'Gottfried Prasetyadi'
    author_email = 'g@prasetyadi.name'
    feed_copyright = 'Copyright (c) 2016-{}, Gottfried Prasetyadi'.format(datetime.datetime.now().year)

    def items(self):
        return Article.objects.filter(published=True)[:10000]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.summary

class AtomLatestArticlesFeed(RssLatestArticlesFeed):
    feed_type = Atom1Feed
    subtitle = RssLatestArticlesFeed.description
