from django.utils import timezone
from django.db import models


class PostsQuerySet(models.QuerySet):
    def published(self):
        return self.filter(
            is_published=True, category__is_published=True, pub_date__lt=timezone.now()
        ).select_related("location", "category", "author")
