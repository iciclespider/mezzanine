
from django import forms
from mezzanine.pages.models import Page
from mezzanine.settings import registry
from mezzanine.settings.models import Settings

FIELD_TYPES = {
    bool: forms.BooleanField,
    int: forms.IntegerField,
}

class SettingsForm(forms.ModelForm):
    """
    Form for settings - creates a field for each setting in 
    ``mezzanine.settings`` that is marked as editable.
    """
    class Meta:
        model = Settings

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        # Load the editable settings.
        self.editables = self.instance.editables()
        for name in sorted(self.editables):
            value = getattr(self.instance, name)
            # Create the form field based on the type of the setting.
            setting = registry[name]
            field_class = FIELD_TYPES.get(setting["type"], forms.CharField)
            self.fields[name] = field_class(label=name, initial=value,
                            help_text=setting["description"], required=False)

    def save(self, commit=True):
        obj = super(SettingsForm, self).save(commit)
        # Save each of the settings to the DB.
        for (name, value) in self.cleaned_data.items():
            if name in self.editables:
                setattr(self.instance, name, value)
        return obj
