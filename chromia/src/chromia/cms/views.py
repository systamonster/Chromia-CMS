from django.shortcuts import render_to_response
from django.conf import settings
from django.http import HttpResponseRedirect
from models import Menu, Category, Article, GitLog, ChromiaBuild
from django.core.cache import cache
from datetime import datetime
import twitter
import re
  
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
            data = GitLog.objects.all().filter(autor=request.POST['autor'])
        else:
            data = GitLog.objects.all()
            
        result =[]
        for log in data:
            log.cmt=log.cmt.replace("\n",",").replace("-","").replace(", ,",",")
            bug = re.findall('[#][0-9]{1,8}', log.cmt)
            if len(bug)>0:
                log.cmt = log.cmt.replace(bug[0],"<a target=\"_blank\" href=\"%s\">%s</a>"
                                          %(settings.BUGZILLA_LINK+bug[0][1:] ,bug[0]) )
            result.append(log)
            
        context["gitlog"] =result         
        
    if path =="download":
        builds = ChromiaBuild.objects.all()
        context["builds"] = builds
        
    if path =="home":
        builds = ChromiaBuild.objects.all().order_by("-build_date")
        context["last_build"] = builds[0]
    
    #Twitter Bug 278    
    tweets = cache.get( 'tweets' )
    if tweets:
        context["tweets"]=tweets 
    else:
        try:
            tweets = twitter.Api().GetUserTimeline(settings.TWITTER_USER)
            if len(tweets)>0:
                tweets = tweets[:settings.TWITTER_TWITS]
                for tweet in tweets:
                    tweet.created_at = datetime.strptime( tweet.created_at, "%a %b %d %H:%M:%S +0000 %Y" )
 
                cache.set( 'tweets', tweets, settings.TWITTER_CACHE )
                context["tweets"]=tweets 
        except:
            "error twitter"
    context["twitter_user"] = settings.TWITTER_USER 
        
         
    context['prefix'] = prefix
    context['user'] = request.user
    return render_to_response(template, context)
