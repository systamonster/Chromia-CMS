from django.shortcuts import render_to_response
from models import Menu, Category, Article, GitLog

def get_path(request, path='home', template='page.html', prefix='/'):
    if path:
        cat = Category.objects.filter(path=path)
        if cat.count() == 0:
            article = Article.objects.get(path=path)
            articles = [article,]
            cat = article.parent
            context = {'articles':articles}
        else:
            cat = cat[0]
            articles = cat.articles()
            context = {'category':cat, 'articles':articles}
        select_list = [cat.slug,]
        cat_parent = cat.parent
        while cat_parent:
            select_list.append(cat_parent.slug)
            cat_parent = cat_parent.parent
    else:
        context = {}
        select_list = ()
    # root nenus
    menus = Menu.objects.all()
    for menu in menus:
        menu.update_selection(select_list)
        context[menu.name] = menu
    
    if path=="download":
        gitlog = GitLog.objects.all()
        context["gitlog"] = gitlog    
        
    context['prefix'] = prefix
    context['user'] = request.user
    return render_to_response(template, context)


def plan(request, template='plan.html', prefix='/'):
    categories = Category.objects.filter(parent__isnull=True, order__gt=0).order_by('order')
    context = {'categories':categories, 'prefix':prefix}
    # root nenus
    menus = Menu.objects.all()
    for menu in menus:
        context[menu.name] = menu
    return render_to_response(template, context)
