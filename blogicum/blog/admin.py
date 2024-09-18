from django.contrib import admin  # type: ignore

from .models import Category, Location, Post


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_published",
        "created_at",
    )
    list_editable = ("is_published",)
    search_fields = ("name",)
    list_filter = (
        "name",
        "is_published",
        "created_at",
    )
    list_display_links = ("name",)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "category",
        "location",
        "is_published",
        "created_at",
    )
    list_editable = (
        "is_published",
        "location",
        "category",
    )
    search_fields = (
        "title",
        "text",
    )
    list_filter = (
        "category",
        "is_published",
        "location",
        "author",
    )
    list_display_links = ("title",)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "slug", "is_published", "created_at")
    list_editable = ("is_published",)
    search_fields = (
        "title",
        "description",
        "slug",
    )
    list_filter = (
        "title",
        "is_published",
        "created_at",
    )
    list_display_links = ("title", "slug")


admin.site.empty_value_display = "-- Не задано --"
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
