from django.contrib import admin
from models import *

class ArticleAdmin(admin.ModelAdmin):
    date_hierarchy = 'updated'
    list_display = ('title', 'category', 'author', 'creation', 'updated')
admin.site.register(Article, ArticleAdmin)


class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
admin.site.register(Menu, MenuAdmin)


class CategoryAdmin(admin.ModelAdmin):
    save_as=True
    list_display = ('short_title', 'title', 'menu', 'order', 'parent')
    list_filter = ('menu', 'parent')
admin.site.register(Category, CategoryAdmin)


#class LinkAdmin(admin.ModelAdmin):
#    list_display = ('title', 'menu', 'category', 'url')
#admin.site.register(Link, LinkAdmin)
