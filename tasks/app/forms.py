from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.forms import CharField, DateInput, Select
from .models import Task


User = get_user_model()

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password1',
            'password2'
        )

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'name',
            'description',
            'due_date',
            'assignee'
        ]
        widgets = {
            'due_date':
                DateInput(attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
                ),
            'assignee': Select(attrs={
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assignee'].queryset = User.objects.filter(is_superuser=False).order_by('username')


class SearchTaskForm(forms.Form):
    statuses = (
        ("pending", "pending"),
        ("done", "done"),
        ("canceled", "canceled")
    )
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    creator = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False
    )
    assignee = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        choices=Task.statuses,
        required=False
    )
    keywords = CharField(max_length=255, required=False, help_text='List keywords separated by spaces, that are present in name or description')
    widgets = {
        'start_date':
            DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }
            ),
        'end_date':
            DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }
            )
    }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date <= start_date:
            self.add_error('end_date', 'End date cannot be earlier than start date')

        return cleaned_data

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['creator'].queryset = User.objects.filter(is_superuser=False).order_by('username')
    #     self.fields['assignee'].queryset = User.objects.filter(is_superuser=False).order_by('username')
