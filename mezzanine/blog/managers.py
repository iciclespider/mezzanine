
from django.db.models import Manager, Count
from mezzanine.core.managers import DisplayableManager

class BlogPostManager(DisplayableManager):
    """
    Extends ``DisplayableManager.published`` with annotated comment counts.
    """

    def published(self, *args, **kwargs):
        return super(BlogPostManager, self).published(*args, **kwargs) \
            .annotate(num_comments=Count("comments")).select_related(depth=1)


class CommentManager(Manager):
    """
    Provides filter for restricting comments that are not approved if
    ``COMMENTS_UNAPPROVED_VISIBLE`` is set to ``False``.
    """

    def visible(self, request):
        #settings.use_editable()
        if request.settings.COMMENTS_UNAPPROVED_VISIBLE:
            return self.all()
        return self.filter(approved=True)
