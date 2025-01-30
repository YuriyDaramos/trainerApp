from django import forms

from trainer.models import TrainerSchedule, TrainerDescription, Category, Service


class AddTrainerService(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["category", "duration", "price", "level"]

    level = forms.ChoiceField(choices=Service.LEVEL_CHOICES, label="Level")

    def __init__(self, *args, **kwargs):  # redef __init__ for real-time update choices list
        super().__init__(*args, **kwargs)
        self.fields["category"].choices = [(cat.id, cat.name) for cat in Category.objects.all()]


class SetWorkingHours(forms.ModelForm):
    class Meta:
        model = TrainerSchedule
        fields = ["datetime_start", "datetime_end"]

    datetime_start = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
                                         required=True)
    datetime_end = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
                                       required=True)


class EditTrainerService(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["category", "duration", "price", "level", "delete"]

    level = forms.ChoiceField(choices=Service.LEVEL_CHOICES, label="Level")
    delete = forms.BooleanField(required=False, label="Delete this service?")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["category"].choices = [(cat.id, cat.name) for cat in Category.objects.all()]


class SetDescription(forms.ModelForm):
    class Meta:
        model = TrainerDescription
        fields = ["text"]


