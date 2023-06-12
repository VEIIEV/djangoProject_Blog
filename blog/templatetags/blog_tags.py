from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown

from blog.models import Post

# переменная которая нужна для регистрации шаблонных тегов и фильтров
register = template.Library()


# декоратор регистрирует функцию как простой тег
# django будет использовать имя функции как имя тега
# пример задачи имени register.simple_tag(name='totalPost')
@register.simple_tag
def total_posts():
    return Post.published.count()


@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(
        total_comments=Count('comments')
    ).exclude(total_comments=0).order_by('-total_comments')[:count]


# "Шаблонный тег включения" возвращает словарь переменных
# которые будут помещены в шаблон.
# В теге указывается файл шаблон, который будет отрисовываться

@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


# создание фильтров
@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))
