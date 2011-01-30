
from django.forms import models
from mezzanine.blog.models import Post, Comment


class CommentForm(models.ModelForm):
    """
    Model form for ``Comment`` against a ``BlogPost``.
    """

    class Meta:
        model = Comment
        fields = ("name", "email", "website", "body",)


class PostForm(models.ModelForm):
    """
    Model form for ``BlogPost`` that provides the quick blog panel in the
    admin dashboard.
    """

    class Meta:
        model = Post
        fields = ("title", "content", "status")

    def __init__(self):
        super(PostForm, self).__init__()
        self.fields["status"].widget = forms.HiddenInput()
