from django.contrib.syndication.views import Feed
from .models import Post


class AllPostRssFeed(Feed):
    title = "存在与虚无"
    link = "/"
    description = "存在与虚无个人日志"

    def items(self):
        return Post.objects.all()

    def item_title(self, item):
        return '[%s] %s' % (item.category, item.title)

    def item_description(self, item):
        return item.body
