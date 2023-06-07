from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from django.http import Http404

import djangoProject.settings
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm


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
        posts = paginator.page(1)
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

# представлени для 1)отображает изначальные данные на странице
#                  2)обработка представленных для валидации данных
def post_share(request, post_id):
    # функция сокращенного доступа для извлечения поста с id==post_id
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    sent = False
    # 2)
    if request.method == "POST":
        #  Когда пользователь заполняет форму и  передает ее методом POST
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # форма снова прорисовывается в  шаблоне,
            # включая переданные данные. Ошибки валидации будут отображены
            # в шаблоне.
            # в cd = dict  в котором  находятся данные из формы,
            # где ключи =  названия формы и значение = содержание
            cd = form.cleaned_data
            #непосредственно отправка письма
            post_url=request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject=f"{cd['name']} recommends you read {post}"
            message= f"Mail send by {cd['email']}\n\n"\
                    f"Read {post.title} at {post_url}\n\n" \
                    f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, djangoProject.settings.EMAIL_HOST_USER,
                      [cd['to']])
            sent = True
    # 1)
    else:
        # Указанный экземпляр формы
        # будет использоваться для отображения пустой формы в шаблоне
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form})
