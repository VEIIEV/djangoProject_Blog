from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView


class PostListView(ListView):
    """
     Альтернативное представление списка постов
    """

    # Вместо
    # определения атрибута queryset мы могли бы указать model=Post, и Django
    # сформировал бы для нас типовой набор запросов Post.objects.all()
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_list(request):
    post_lists = Post.published.all()
    # создаем объект класс Paginator  с числом объектов на 1 странице
    paginator = Paginator(post_lists, 3)
    # вытягиваем значение параметра page из GET запроса, если он отсутствует, выставляем дефолтное 1
    #     MultiValueDict????
    page_number = request.GET.get('page', 1)
    # получаем объекты для указанной страницы
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        posts= paginator.page(1)
    except PageNotAnInteger:
        posts = paginator.page(paginator.num_pages)

    print(posts.__dict__)
    return render(request, 'blog/post/list.html', {'posts': posts})


def post_detail(request, post, year, month, day):
    print('мы тут с ', request.user)
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    return render(request, 'blog/post/details.html', {'post': post})
