
from django.db.models import Manager


class CommentManager(Manager):
    """
    Provides filter for restricting comments that are not approved if
    ``COMMENTS_UNAPPROVED_VISIBLE`` is set to False.
    """

    def visible(self, request):
        if request.settings.COMMENTS_UNAPPROVED_VISIBLE:
            return self.all()
        return self.filter(approved=True)
