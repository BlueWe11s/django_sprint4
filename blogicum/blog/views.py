from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
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
from .mixins import (AuthorTestMixin, UrlSuccesProfileMixin,
                     UrlSuccesPostMixin, CommentUpdateMixin, UserTestMixin)


User = get_user_model()


class IndexListView(ListView):
    model = Post
    paginate_by = POST_IN_PAGE
    template_name = 'blog/index.html'

    def get_queryset(self):
        return (
            Post.objects
            .published()
            .annotate_comments()
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
        )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        self.author = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.request.user == self.author.author:
            return self.author

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
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return context


class ProfileUpdateView(LoginRequiredMixin, UserTestMixin,
                        UrlSuccesProfileMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = ProfileEditForm

    def get_object(self, queryset=None):
        return self.request.user


class CommentCreateView(LoginRequiredMixin, UrlSuccesPostMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.save()
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])


class CommentUpdateView(LoginRequiredMixin, AuthorTestMixin,
                        UrlSuccesPostMixin, CommentUpdateMixin, UpdateView):
    pass


class CommentDeleteView(LoginRequiredMixin, AuthorTestMixin,
                        UrlSuccesPostMixin, CommentUpdateMixin, DeleteView):
    pass
