from django.shortcuts import render, get_object_or_404
from blog.models import Post, Category
from .const import POST_LIMIT


def index(request):
    """Обработчик домашней страницы"""
    post_list = Post.objects.published()[:POST_LIMIT]
    return render(request, 'blog/index.html',
                  {'post_list': post_list})


def post_detail(request, id):
    """post_deatail"""
    post = get_object_or_404(
        Post.objects.published(),
        id=id
    )
    return render(request, 'blog/detail.html', {'post': post})


def category_posts(request, category_slug):
    """Обработчик категорий"""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post = category.posts.published()

    return render(
        request,
        'blog/category.html',
        {'category': category, 'post_list': post}
    )
