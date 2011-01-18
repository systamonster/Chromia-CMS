#
# Copyright (C) 2011 Kirill Gordeev <kirill.gordeev@gmail.com>
# Copyright (C) 2011 David Criado <dccirujeda@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

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
