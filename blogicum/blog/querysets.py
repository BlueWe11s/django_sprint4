from django.utils import timezone
from django.db.models import Count
from django.db import models


class PostsQuerySet(models.QuerySet):
    def post_select_related(self):
        return self.select_related("location", "category", "author")

    def published(self):
        return self.filter(
            is_published=True, category__is_published=True,
            pub_date__lt=timezone.now()
        ).post_select_related()

    def annotate_comments(self):
        return self.annotate(comment_count=Count('comments'))
