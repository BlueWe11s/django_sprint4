from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
     path('', views.IndexListView.as_view(), name='index'),
     path('posts/<int:id>/', views.PostDetailView.as_view(),
          name='post_detail'),
     path('category/<slug:category_slug>/',
          views.CategoryPostsListView.as_view(),
          name='category_posts'),
     path('profile/<slug:username>/',
          views.ProfileListView.as_view(),
          name='profile'),
     path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
     path('edit_profile/',
          views.ProfileUpdateView.as_view(),
          name='edit_profile'),
     path('posts/<post_id>/edit',
          views.PostUpdateView.as_view(), name='edit_post'),
     path('posts/<post_id>/delete', views.PostDeleteView.as_view(), name='delete_post'),
     path('<int:pk>/comment', views.CommentCreateView.as_view(), name='add_comment'),
]
