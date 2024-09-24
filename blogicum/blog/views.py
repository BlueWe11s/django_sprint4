from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    DetailView,
    DeleteView,
)
from .form import CommentForm, PostForm, ProfileEditForm
from .models import Category, Comment, Post
from blogicum.settings import POST_IN_PAGE


User = get_user_model()


class AuthorTestMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])


class UrlSuccesProfileMixin():
    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class UrlSuccesPostMixin():
    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class IndexListView(ListView):
    model = Post
    paginate_by = POST_IN_PAGE
    template_name = 'blog/index.html'

    def get_queryset(self):
        return (
            Post.objects
            .published()
            .annotate_comments()
            .order_by('-pub_date')
        )


class CategoryListView(ListView):
    model = Post
    paginate_by = POST_IN_PAGE
    template_name = 'blog/category.html'

    def get_queryset(self):
        category = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_published=True
        )

        return (
            category.posts.post_select_related()
            .published()
            .annotate_comments()
            .order_by('-pub_date')
        )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        self.author = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.request.user == self.author.author:
            return get_object_or_404(
                Post.objects,
                pk=self.kwargs['post_id']
            )

        return get_object_or_404(
            Post.objects.published(),
            pk=self.kwargs['post_id']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class PostDeleteView(LoginRequiredMixin, AuthorTestMixin,
                     UrlSuccesProfileMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class PostCreateView(LoginRequiredMixin, UrlSuccesProfileMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, AuthorTestMixin,
                     UrlSuccesPostMixin, UpdateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'


class ProfileListView(ListView):
    model = Post
    paginate_by = POST_IN_PAGE
    template_name = 'blog/profile.html'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return (
            self.model.objects.select_related('author')
            .filter(author__id=user.id)
            .annotate_comments()
            .order_by('-pub_date')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return context


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin,
                        UrlSuccesProfileMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = ProfileEditForm

    def test_func(self):
        return self.get_object() == self.request.user

    def get_object(self, queryset=None):
        return self.request.user

    def handle_no_permission(self):
        return super().handle_no_permission()


class CommentCreateView(LoginRequiredMixin, UrlSuccesPostMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.comment = get_object_or_404(
            Post,
            pk=kwargs.get('post_id'),
            category__is_published=True
        )
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.comment
        return super().form_valid(form)


class CommentUpdateView(LoginRequiredMixin, AuthorTestMixin,
                        UrlSuccesPostMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'


class CommentDeleteView(LoginRequiredMixin, AuthorTestMixin,
                        UrlSuccesPostMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
