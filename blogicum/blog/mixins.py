from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse
from blog.models import Comment
from blog.form import CommentForm


class AuthorTestMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])


class UserTestMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object() == self.request.user


class UrlSuccesProfileMixin():
    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class UrlSuccesPostMixin():
    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class CommentUpdateMixin():
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
