from django.forms import ModelForm

from .models import PhoneNumberRequestLog


class PhoneNumberRequestForm(ModelForm):
    class Meta:
        model = PhoneNumberRequestLog
        fields = [
            'user_id',
        ]

    def __init__(self, *args, **kwargs):
        super(PhoneNumberRequestForm, self).__init__(*args, **kwargs)
        self.fields['user_id'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter user ID',
            'spellcheck': 'false',
        })
