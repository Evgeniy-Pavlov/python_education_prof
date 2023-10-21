from django import forms

class ModifiedClearableFileInput(forms.ClearableFileInput):
    template_name = 'mainapp/widgets/modified_ClearableFileInput.html'