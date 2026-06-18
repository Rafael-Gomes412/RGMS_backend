from django.urls import path
from .views import article_list, article_detail

urlpatterns = [
    path('api/blog/', article_list, name='article_list'),
    path('api/blog/<slug:slug>/', article_detail, name='article_detail'),
]