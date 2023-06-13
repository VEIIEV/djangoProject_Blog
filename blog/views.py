from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from taggit.models import Tag
from django.contrib.postgres.search import SearchVector
from django.contrib import messages

import djangoProject.settings
from .forms import EmailPostForm, CommentForm, SearchForm
from .models import Post


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


def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    # создаем объект класс Paginator  с числом объектов на 1 странице
    paginator = Paginator(post_list, 3)
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
    return render(request, 'blog/post/list.html', {'posts': posts,
                                                   'tag': tag})


def post_detail(request, post, year, month, day):
    print('мы тут с ', request.user)
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    # Список активных комментариев к этому посту
    comments = post.comments.filter(active=True)
    # Форма для комментирования пользователями
    form = CommentForm()

    # список схожих постов
    # values_list возвращает кортеж со значением заданных полей
    post_tags_ids = post.tags.values_list('id', flat=True)
    # модификатор __in -- значение должно быть в указанном списке кортоже квересете
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    # annotate создает переменную в который хранит результат
    # агрегированного выражения над 'tag'
    # названием переменной выступает ключ -- same_tags
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'blog/post/details.html', {'post': post,
                                                      'comments': comments,
                                                      'form': form,
                                                      'similar_posts': similar_posts})


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
            # form.cleaned_data returns a dictionary of validated form input fields and their values, where string primary keys are returned as objects.
            #
            # form.data returns a dictionary of un-validated form input fields and their values in string format (i.e. not objects).
            cd = form.cleaned_data
            # непосредственно отправка письма
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = f"{cd['name']} recommends you read {post}"
            message = f"Mail send by {cd['email']}\n\n" \
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
                                                    'form': form,
                                                    'sent': sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    comment = None
    #  Создается экземпляр формы, используя переданные на обработку POSTданные

    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Метод save() создает экземпляр модели, к которой форма привязана,
        # и сохраняет его в базе данных. Если вызывать его, используя commit=False,
        # то экземпляр модели создается, но не сохраняется в базе данных. Такой
        # подход позволяет видоизменять объект перед его окончательным сохранением.

        comment = form.save(commit=False)
        print(comment.__dict__)
        comment.post = post
        comment.save()
    return render(request, 'blog/post/comment.html',
                  {'post': post,
                   'form': form,
                   'comment': comment})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            # cleaned_data -- словарь, который хранит информацию из формы, прошедшую валидацию
            query = form.cleaned_data['query']
            results = Post.published.annotate(search=SearchVector('title', 'body')
                                              ).filter(search=query)
    return render(request,
                  'blog/post/search.html',
                  {'form': form,
                   'query': query,
                   'results': results})

# создал вьюшку редирект на главную страницу если введен некорректный url
def redir_to_main_page(request, id):
    messages.add_message(request, messages.INFO, 'you were redirected on main page')
    return redirect('blog:post_list')