from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _


User = get_user_model()


class CustomUserCreationForm(UserCreationForm):

    def clean_username(self):
        """ Ensures a unique username accounting for character case."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username):
            raise forms.ValidationError(_('This username is already in use. Please try again.'))
        else:
            return username

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')


class CustomUserChangeProfileForm(forms.ModelForm):

    def clean_pgp_key(self):
        """ Ensures pgp key headers are present."""
        key = self.cleaned_data.get('pgp_key')
        if key == "":
            return key
        elif key.startswith(
        '-----BEGIN PGP PUBLIC KEY BLOCK-----'
        ) and key.__contains__(
        '-----END PGP PUBLIC KEY BLOCK-----'
        ):
            return key
        else:
            raise forms.ValidationError(_(
        'That is not a valid PGP public key. Please try again or just delete the invalid key.'
            ))

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'pgp_key',
        )
        widgets = {'pgp_key': forms.Textarea(attrs={'rows': 40, 'cols': 70})}
