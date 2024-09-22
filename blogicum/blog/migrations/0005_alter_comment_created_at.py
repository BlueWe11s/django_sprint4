# Generated by Django 3.2.16 on 2024-09-22 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0004_alter_comment_created_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="comment",
            name="created_at",
            field=models.DateTimeField(
                auto_created=True,
                auto_now_add=True,
                help_text="Идентификатор страницы для URL; разрешены символы латиницы, цифры, дефис и подчёркивание.",
                verbose_name="Добавлено",
            ),
        ),
    ]