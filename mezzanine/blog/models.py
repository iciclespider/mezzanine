
from calendar import month_name
from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.template import RequestContext, Template
from django.template.defaultfilters import truncatewords_html
from django.template.loader import get_template
from hashlib import md5
from mezzanine.blog.managers import BlogPostManager, CommentManager
from mezzanine.configuration import global_settings
from mezzanine.core.fields import HtmlField
from mezzanine.core.models import Displayable, Ownable, Content, Slugged
from mezzanine.pages.models import Page
from mezzanine.utils.views import paginate, set_cookie

class Blog(Page):

    summary = HtmlField(blank=True)
    _posts_per_page = models.PositiveSmallIntegerField("Posts per Page", null=True, blank=True)
    _max_paging_links = models.PositiveSmallIntegerField("Max Paging Links", null=True, blank=True)
    post_style = HtmlField("Post Style", widget_rows=20, blank=True)
    post_template = HtmlField("Post Template", widget_rows=40, blank=True)

    class Meta(Page.Meta, Content.Meta):
        abstract = False
        verbose_name = "Blog"
        verbose_name_plural = "Blogs"

    @property
    def posts_per_page(self):
        if self._posts_per_page:
            return self._posts_per_page
        return self.settings.BLOG_POSTS_PER_PAGE

    @property
    def max_paging_links(self):
        if self._max_paging_links:
            return self._max_paging_links
        return self.settings.BLOG_MAX_PAGING_LINKS

    @property
    def default_template(self):
        return self.settings.TEMPLATE_BLOGPAGE

    def render(self, request):
        return self.render_blog(request)

    def get_child_response(self, request, slug, url):
        if url:
            url = url.split('/')
        else:
            url = []
        #if slug == 'tag':
        #    if len(url) != 1:
        #        raise Http404
        #    return self.list(request, tag=url[0])
        if slug == 'category':
            if len(url) != 1:
                raise Http404
            return self.render_blog(request, category=url[0])
        if slug == 'author':
            if len(url) != 1:
                raise Http404
            return self.render_blog(request, author=url[0])
        if slug == 'archive':
            if len(url) > 2:
                raise Http404
            if len(url) == 1:
                return self.render_blog(request, year=url[0])
            return self.render_list(request, year=url[0], month=url[1])
        if len(url) != 0:
            raise Http404
        posts = self.posts.published(for_user=request.user)
        post = get_object_or_404(posts, slug=slug)
        return post.render(request)

    def render_blog(self, request, year=None, month=None, author=None, category=None):
        posts = self.posts.published(for_user=request.user)
        #if tag is not None:
        #    tag = get_object_or_404(Keyword, slug=tag)
        #    blog_posts = blog_posts.filter(keywords=tag)
        if year is not None:
            if not year.isdigit():
                raise Http404
            posts = posts.filter(publish_date__year=year)
            if month is not None:
                if not month.isdigit():
                    raise Http404
                posts = posts.filter(publish_date__month=month)
                month = month_name[int(month)]
        if category is not None:
            try:
                category = self.categories.get(slug=category)
            except Category.DoesNotExist:
                raise Http404
            posts = posts.filter(category=category)
        if author is not None:
            author = get_object_or_404(User, username=author)
            posts = posts.filter(user=author)
        posts = paginate(posts,
                         request,
                         self.posts_per_page,
                         self.max_paging_links)
        context = {"displayable": self,
                   "posts": posts,
                   "year": year,
                   "month": month,
                   "category": category,
                   "author": author,
                   }
        return HttpResponse(self.get_template().render(RequestContext(request, context)))

    def get_post_template(self):
        if self.post_template:
            return Template(self.detail_template, name='"%s" Blog Post template' % self.head_title)
        return get_template(self.settings.TEMPLATE_BLOGPOST)


class Category(Slugged):
    """
    A category for grouping blog posts into a series.
    """

    blog = models.ForeignKey(Blog, related_name='categories')

    class Meta(Slugged.Meta):
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Post(Displayable, Ownable, Content):

    blog = models.ForeignKey(Blog, related_name='posts')
    category = models.ForeignKey(Category, related_name="posts",
        blank=True, null=True)

    objects = BlogPostManager()

    class Meta(Displayable.Meta, Ownable.Meta, Content.Meta):
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ("-publish_date",)
        unique_together = ("blog", "slug")

    @property
    def url(self):
        return self.blog.url + self.slug + '/'

    @property
    def head_title(self):
        return self.blog.head_title + '/' + super(Post, self).head_title

    def render(self, request):
        from mezzanine.blog.forms import CommentForm
        commenter_cookie_prefix = "mezzanine-blog-"
        commenter_cookie_fields = ("name", "email", "website")
        comment_data = {}
        for f in commenter_cookie_fields:
            comment_data[f] = request.COOKIES.get(commenter_cookie_prefix + f, "")
        saved = False
        if request.method == "POST":
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = self
                comment.by_author = (request.user == self.user and
                                     request.user.is_authenticated)
                comment.ip_address = request.META.get("HTTP_X_FORWARDED_FOR",
                                                      request.META["REMOTE_ADDR"])
                comment.replied_to_id = request.POST.get("replied_to")
                comment.save()
                saved = True
        else:
            comment_data = {}
            for f in commenter_cookie_fields:
                comment_data[f] = request.COOKIES.get(commenter_cookie_prefix + f, "")
            form = CommentForm(initial=comment_data)
        context = {"displayable": self,
                   "form": form,
                   "saved": saved,
                   }
        response = HttpResponse(self.blog.get_post_template().render(RequestContext(request, context)))
        if saved:
            cookie_expires = 60 * 60 * 24 * 90
            for f in commenter_cookie_fields:
                cookie_name = commenter_cookie_prefix + f
                cookie_value = request.POST.get(f, "")
                set_cookie(response, cookie_name, cookie_value, cookie_expires)
        return response

    @property
    def current_comments(self):
        return self.comments.filter(approved=True)


class Comment(models.Model):
    """
    A comment against a blog post.
    """

    post = models.ForeignKey(Post, related_name="comments")
    name = models.CharField("Name", max_length=100, help_text="required")
    email = models.EmailField("Email",
        help_text="required (not published)")
    email_hash = models.CharField("Email hash", max_length=100, blank=True)
    body = models.TextField("Comment")
    website = models.URLField("Website", blank=True, help_text="optional")
    approved = models.BooleanField("Approved",
        default=global_settings.COMMENTS_DEFAULT_APPROVED)
    by_author = models.BooleanField("By the blog author", default=False)
    ip_address = models.IPAddressField("IP address", blank=True, null=True)
    time_created = models.DateTimeField("Created at", default=datetime.now)
    replied_to = models.ForeignKey("self", blank=True, null=True,
        related_name="comments")

    objects = CommentManager()

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ("time_created",)

    def __unicode__(self):
        return self.body

    #def get_absolute_url(self):
    #    return "%s#comment-%s" % (self.blog_post.get_absolute_url(), self.id)

    def save(self, *args, **kwargs):
        if not self.email_hash:
            self.email_hash = md5(self.email).hexdigest()
        super(Comment, self).save(*args, **kwargs)

    ################################
    # Admin listing column methods #
    ################################

    def intro(self):
        return truncatewords_html(self.body, 20)
    intro.short_description = "Comment"

    def avatar_link(self):
        from mezzanine.blog.templatetags.blog_tags import gravatar_url
        return "<a href='mailto:%s'><img style='vertical-align:middle;" \
            "margin-right:3px;' src='%s' />%s</a>" % (self.email,
            gravatar_url(self.email_hash), self.name)
    avatar_link.allow_tags = True
    avatar_link.short_description = ""

    def admin_link(self):
        return "<a href='%s'>%s</a>" % (self.get_absolute_url(), "View on site")
    admin_link.allow_tags = True
    admin_link.short_description = ""
