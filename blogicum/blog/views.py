from typing import Any
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http.request import HttpRequest as HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    DetailView,
    DeleteView,
)
from .form import CommentForm, PostForm, ProfileEditForm
from .models import Category, Comment, Post
# from .utils import get_post_data
from .const import POST_IN_PAGE


User = get_user_model()


class IndexListView(ListView):
    model = Post
    paginate_by = POST_IN_PAGE
    template_name = "blog/index.html"

    def get_queryset(self):
        return (
            self.model.objects.select_related("location", "author", "category")
            .published()
            .annotate(comment_count=Count("comments"))
            .order_by("-pub_date")
        )


class CategoryListView(ListView):
    model = Post
    paginate_by = POST_IN_PAGE
    template_name = "blog/category.html"

    def get_queryset(self):
        category = get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True
        )

        return (
            category.posts.select_related("location", "author", "category")
            .filter(is_published=True, pub_date__lte=timezone.now())
            .annotate(comment_count=Count("comments"))
            .order_by("-pub_date")
        )


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"

    def get_object(self, queryset=None):
        return get_object_or_404(
            Post.objects.published(),
            pk=self.kwargs["id"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = self.object.comments.select_related("author")
        return context


class PostDeleteView(LoginRequiredMixin, DeleteView, UserPassesTestMixin):
    model = Post
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", id=self.kwargs["post_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse("blog:profile", kwargs={"username": self.request.user})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = get_object_or_404(
            Category.objects.values("id", "title", "description"),
            slug=self.kwargs["category_slug"],
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = "blog/create.html"
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:profile", kwargs={"username": self.request.user})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = "blog/create.html"
    form_class = PostForm
    pk_url_kwarg = "post_id"

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse(
            "blog:post_detail",
            kwargs={"id": self.kwargs["post_id"]}
        )

    def handle_no_permission(self):
        return redirect("blog:post_detail", id=self.args["post_id"])


class ProfileListView(ListView):
    model = Post
    paginate_by = POST_IN_PAGE
    template_name = "blog/profile.html"

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        return (
            self.model.objects.select_related("author")
            .filter(author__id=user.id)
            .annotate(comment_count=Count("comments"))
            .order_by("-pub_date")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = get_object_or_404(
            User,
            username=self.kwargs["username"]
        )
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView, UserPassesTestMixin):
    template_name = "blog/user.html"
    form_class = ProfileEditForm

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse("blog:profile", args=[self.request.user.username])


class CommentCreateView(LoginRequiredMixin, CreateView):
    comment = None
    model = Comment
    form_class = CommentForm
    template_name = "blog/comment.html"

    def dispatch(self, request, *args, **kwargs):
        self.comment = get_object_or_404(
            Post,
            pk=kwargs.get('post_id'),
            category__is_published=True
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.comment
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:post_detail",
                       kwargs={"id": self.kwargs["post_id"]})


class CommentUpdateView(LoginRequiredMixin, UpdateView, UserPassesTestMixin):
    model = Comment
    form_class = CommentForm
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse(
            "blog:post_detail", kwargs={"post_id": self.kwargs.get("post_id")}
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView, UserPassesTestMixin):
    model = Comment
    pk_url_kwarg = "comment_id"
    template_name = "blog/comment.html"

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse(
            "blog:post_detail", kwargs={"post_id": self.kwargs.get("post_id")}
        )
