from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Article

def article_list(request):
    # On ne récupère que les articles cochés comme "publiés"
    articles = Article.objects.filter(is_published=True).order_by('-created_at')
    data = list(articles.values('id', 'title', 'slug', 'summary', 'created_at'))
    return JsonResponse(data, safe=False)

def article_detail(request, slug):
    # On cherche l'article grâce à son slug SEO
    article = get_object_or_404(Article, slug=slug, is_published=True)
    data = {
        'id': article.id,
        'title': article.title,
        'slug': article.slug,
        'content': article.content,
        'summary': article.summary,
        'created_at': article.created_at,
    }
    return JsonResponse(data)