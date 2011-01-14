from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from models import Menu, Category, Article, GitLog, ChromiaBuild


def redirect_external(request):
    r=request.META['PATH_INFO'].split("/redirect/")[1]
    return  HttpResponseRedirect(r)
    

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
    
    if path=="log":
        context["autors"]  = GitLog.objects.distinct().values("autor").order_by("autor")
        if request.POST and not request.POST['autor'] =="ALL":
            context["autor_selected"] = request.POST['autor']
            context["gitlog"] = GitLog.objects.all().filter(autor=request.POST['autor'])
        else:
            context["gitlog"] = GitLog.objects.all()         
        
        
    if path =="download":
        builds = ChromiaBuild.objects.all()
        context["builds"] = builds
        
    if path =="home":
        builds = ChromiaBuild.objects.all().order_by("-build_date")
        context["last_build"] = builds[0]
        
    
        
         
    context['prefix'] = prefix
    context['user'] = request.user
    return render_to_response(template, context)
