from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Post
from django.core.paginator import Paginator


def post_list(request):
    post_lists = Post.published.all()
    # создаем объект класс Paginator  с числом объектов на 1 странице
    paginator = Paginator(post_lists(), 3)
    # вытягиваем значение параметра page из GET запроса, если он отсутствует, выставляем дефолтное 1
    #     MultiValueDict????
    page_number = request.GET.get('page', 1)
    # получаем объекты для указанной страницы
    posts = paginator.page(page_number)
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
