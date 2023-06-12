from django.contrib.sitemaps import Sitemap
from .models import Post

#файл для создания sitemap
class PostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9


    def items(self):
        return Post.published.all()

    def lastmod(self, obj):
        return obj.updated
