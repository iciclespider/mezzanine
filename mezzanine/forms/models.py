
from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models
from mezzanine.configuration import global_settings
from mezzanine.core.fields import HtmlField
from mezzanine.core.models import Orderable, Content
from mezzanine.pages.models import Page


FIELD_CHOICES = (
    ("CharField", "Single line text"),
    ("CharField/django.forms.Textarea", "Multi line text"),
    ("EmailField", "Email"),
    ("BooleanField", "Check box"),
    ("MultipleChoiceField/django.forms.CheckboxSelectMultiple",
        "Check boxes"),
    ("ChoiceField", "Drop down"),
    ("MultipleChoiceField", "Multi select"),
    ("ChoiceField/django.forms.RadioSelect", "Radio buttons"),
    ("FileField", "File upload"),
    ("DateField/django.forms.extras.SelectDateWidget", "Date"),
    ("DateTimeField", "Date/time"),
    ("CharField/django.forms.HiddenInput", "Hidden"),
)


class Form(Page, Content):
    """
    A user-built form.
    """

    button_text = models.CharField("Button text", max_length=50,
        default="Submit")
    response = HtmlField("Response")
    send_email = models.BooleanField("Send email", default=False,
        help_text="If checked, the person entering the form will be sent an email")
    email_from = models.EmailField("From address", blank=True,
        help_text="The address the email will be sent from")
    email_copies = models.CharField("Send copies to", blank=True,
        help_text="One or more email addresses, separated by commas",
        max_length=200)
    email_subject = models.CharField("Subject", max_length=200, blank=True)
    email_message = models.TextField("Message", blank=True)

    class Meta:
        verbose_name = "Form Page"
        verbose_name_plural = "Form Pages"

    @property
    def default_template(self):
        return self.settings.TEMPLATE_FORMPAGE

    def get_context(self, request):
        from mezzanine.forms.forms import FormForForm
        sent = False
        if request.method == 'POST':
            form = FormForForm(self, request.POST, request.FILES)
            if form.is_valid():
                entry = form.save()
                fields = ["%s: %s" % (v.label, form.format_value(form.cleaned_data[k]))
                          for (k, v) in form.fields.items()]
                subject = self.email_subject
                if not subject:
                    subject = "%s - %s" % (self.title, entry.entry_time)
                body = "\n".join(fields)
                if self.email_message:
                    body = "%s\n\n%s" % (self.email_message, body)
                email_from = self.email_from or settings.DEFAULT_FROM_EMAIL
                email_to = form.email_to()
                if email_to and self.send_email:
                    msg = EmailMessage(subject, body, email_from, [email_to])
                    msg.send()
                email_from = email_to or email_from  # Send from the email entered.
                email_copies = [e.strip() for e in self.email_copies.split(",") if e.strip()]
                if email_copies:
                    msg = EmailMessage(subject, body, email_from, email_copies)
                    for f in form.files.values():
                        f.seek(0)
                        msg.attach(f.name, f.read())
                    msg.send()
                sent = True
        else:
            form = FormForForm(self)
        return {"form": form, "sent": sent}


class FieldManager(models.Manager):
    """
    Only show visible fields when displaying actual form..
    """
    def visible(self):
        return self.filter(visible=True)


class Field(Orderable):
    """
    A field for a user-built form.
    """

    form = models.ForeignKey("Form", related_name="fields")
    label = models.CharField("Label",
        max_length=global_settings.FORMS_LABEL_MAX_LENGTH)
    field_type = models.CharField("Type", choices=FIELD_CHOICES,
        max_length=55)
    required = models.BooleanField("Required", default=True)
    visible = models.BooleanField("Visible", default=True)
    choices = models.CharField("Choices", max_length=1000, blank=True,
        help_text="Comma separated options where applicable. If an option "
            "itself contains commas, surround the option with `backticks`.")
    default = models.CharField("Default value", blank=True,
        max_length=global_settings.FORMS_FIELD_MAX_LENGTH)
    help_text = models.CharField("Help text", blank=True, max_length=100)

    objects = FieldManager()

    class Meta:
        verbose_name = "Field"
        verbose_name_plural = "Fields"
        order_with_respect_to = "form"

    def __unicode__(self):
        return self.label

    def get_choices(self):
        """
        Parse a comma separated choice string into a list of choices taking
        into account quoted choices.
        """
        choice = ""
        (quote, unquote) = ("`", "`")
        quoted = False
        for char in self.choices:
            if not quoted and char == quote:
                quoted = True
            elif quoted and char == unquote:
                quoted = False
            elif char == "," and not quoted:
                choice = choice.strip()
                if choice:
                    yield choice, choice
                choice = ""
            else:
                choice += char
        choice = choice.strip()
        if choice:
            yield choice, choice


class FormEntry(models.Model):
    """
    An entry submitted via a user-built form.
    """

    form = models.ForeignKey("Form", related_name="entries")
    entry_time = models.DateTimeField("Date/time")

    class Meta:
        verbose_name = "Form entry"
        verbose_name_plural = "Form entries"


class FieldEntry(models.Model):
    """
    A single field value for a form entry submitted via a user-built form.
    """

    entry = models.ForeignKey("FormEntry", related_name="fields")
    field_id = models.IntegerField()
    value = models.CharField(max_length=global_settings.FORMS_FIELD_MAX_LENGTH)

    class Meta:
        verbose_name = "Form field entry"
        verbose_name_plural = "Form field entries"
