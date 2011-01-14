from django.db import models
from django.contrib.auth.models import Group, User
from django.template.defaultfilters import slugify

class Menu(models.Model):
    name = models.SlugField(unique=True)
    parent = models.ForeignKey('self', null=True, blank=True)
    selected_slugs = ()
    parent_cat_selected = None

    def update_selection(self, slugs):
        u"""update self.parent_cat_selected
        """
        self.selected_slugs = slugs
        # selected parent category
        if self.parent:
            lsel = self.parent.category_set.filter(slug__in=slugs)
            if len(lsel) > 0:
                self.parent_cat_selected = lsel[0]

    def categories(self):
        cats = self.category_set.all().exclude(order__lt=1).order_by('order')
        # parent filter
        if self.parent:
            if len(self.selected_slugs) > 0:
                cats = cats.filter(parent__slug__in=self.selected_slugs)
            else:
                cats = cats.filter(parent__isnull=True)
        for cat in cats:
            if cat.slug in self.selected_slugs: cat.selected = True

        return cats

    def links(self):
        return self.link_set.all()

    def main_categories(self):
        return self.category_set.filter(order=0)

    def __unicode__(self):
        return self.name;

    def __str__(self):
       return self.name


class Category(models.Model):
    title = models.CharField(max_length = 100)
    short_title = models.CharField(max_length = 50, unique=True)
    menu = models.ForeignKey(Menu)
    order = models.SmallIntegerField(null=True, blank=True,
                                     help_text='0: main - <0: disabled')
    slug = models.SlugField(null=True, blank=True, unique=True, help_text='generated if not filled')
    path = models.CharField(max_length = 200, null=True, blank=True, help_text='should be generated')
    parent = models.ForeignKey('self', null=True, blank=True)
    template_name = models.CharField(max_length = 100, null=True, blank=True)
    role = models.ForeignKey(Group, null=True, blank=True)
    selected = False

    def select(self):
        self.selected = True

    def get_root(self):
        root = self
        while root.parent:
            root = root.parent
        return root

    def url(self):
        return '%s/' % self.path

    def children(self):
        return self.category_set.exclude(order__lt=0).order_by('order')

    def links(self):
        return self.link_set.all()

    def articles(self):
        l = list(self.article_set.all().exclude(slug='main').order_by('-creation'))
       # refs = self.refarticle_set.all()
       # if len(refs) > 0:
       #     l.append(refs)
        return l

    def main_articles(self):
        return self.article_set.filter(slug='main').order_by('-creation')

    def __unicode__(self):
        return self.title;

    def save(self):
        if not self.slug:
            self.slug = slugify(self.short_title)
        if not self.path:
            self.path = self.slug
            if self.parent: self.path = '%s/%s' % (self.parent.path, self.path)
        models.Model.save(self)
    
    class Meta:
        verbose_name_plural='Categories'

    def __str__(self):
       return self.title

class Article(models.Model):
    creation = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length = 100)
    slug = models.SlugField(null=True, blank=True, help_text='generated if not filled')
    path = models.CharField(max_length = 200, null=True, blank=True, help_text='should be generated')
    category = models.ForeignKey(Category)
    author = models.ForeignKey(User)
    text = models.TextField(null=True, blank=True)

    def summary(self):
        if len(self.text) > 100:
            return '%s ...' % self.text[0:100]

    def url(self):
        return '%s/' % self.path

    def date_creation(self):
        d = self.creation
        return '%02d/%02d/%d' % (d.day, d.month, d.year)

    def __unicode__(self):
        return self.title;

    def save(self):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.path:
            self.path = self.slug
        models.Model.save(self)


class Link(models.Model):
    category = models.ForeignKey(Category)
    menu = models.ForeignKey(Menu, null=True, blank=True)
    title = models.CharField(max_length = 100)
    url = models.CharField(max_length = 100)

    def html(self):
        return '<a href=%s>%s</a>' % (self.url, self.title)

    def __unicode__(self):
            return self.url;
        
class GitLog(models.Model):
    commit_id = models.CharField(max_length = 42, unique=True)
    autor     = models.CharField(max_length=140) 
    commit_date= models.DateTimeField()
    cmt  = models.TextField()
    files = models.IntegerField(max_length=10)
    insertions=models.IntegerField(max_length=10)
    deletions = models.IntegerField(max_length=10)
    
class ChromiaBuild(models.Model):
    version_id = models.CharField(max_length=42)
    md5sum     = models.CharField(max_length=34)
    build_date = models.DateTimeField()
    file_size  = models.IntegerField(max_length=10)
    package_file = models.CharField(max_length=100) 
       
    