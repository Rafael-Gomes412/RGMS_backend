from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_published')
    prepopulated_fields = {'slug': ('title',)}  # Génère le slug automatiquement pendant que tu tapes le titre