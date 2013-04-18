from django import forms
from django.forms.formsets import BaseFormSet
from django.forms.models import BaseInlineFormSet
from leagues.models import Description, Contestants, Results
from captcha.fields import CaptchaField

class DescriptionForm(forms.ModelForm):
    repeat = forms.CharField(label='Repeat password')
    
    """
    https://django-simple-captcha.readthedocs.org/en/latest/usage.html#define-the-form
    """
    captcha = CaptchaField()
    
    def clean(self):
        super(DescriptionForm,self).clean()
        if 'password' in self.cleaned_data and 'repeat' in self.cleaned_data:
            password = self.cleaned_data['password']
            repeat = self.cleaned_data['repeat']
            
            if password != repeat:
                self._errors['repeat'] = [u'Password didnt match']
                
        return self.cleaned_data
    
    class Meta:
        model = Description
        fields = ('name', 'password', 'repeat', 'rounds', 'captcha',)

class ContestantsForm(forms.ModelForm):
    name = forms.CharField(label='Team name')
    
    class Meta:
        model = Contestants
        fields = ('name',)
        #exclude = ('tournament', 'match', 'win', 'draw', 'loss', 'goal_for', 'goal_against', 'points')
        
class ResultsForm(forms.ModelForm):
    result1 = forms.IntegerField(label='Home')
    result2 = forms.IntegerField(label='Away')

    def clean(self):
        super(ResultsForm,self).clean()
        if 'result1' in self.cleaned_data and 'result2' in self.cleaned_data:
            result1 = self.cleaned_data['result1']
            result2 = self.cleaned_data['result2']
            
            if result1 > 99:
                self._errors['result1'] = [u'Max. 99!']
            elif result1 < 0:
                self._errors['result1'] = [u'Min. 0!']
                
            if result2 > 99:
                self._errors['result2'] = [u'Max. 99!']
            elif result2 < 0:
                self._errors['result2'] = [u'Min. 0!']
                
        return self.cleaned_data
    
    class Meta:
        model = Results
        fields = ('result1', 'result2',)
        #exclude = ('tournament', 'contestant1', 'contestant2', 'replay', 'updated')
        
class UploadForm(forms.Form):
    replay = forms.FileField()
    
    def clean_replay(self):
        max_size = 5*10**4
        file_name = self.cleaned_data['replay'].name
        
        if self.cleaned_data['replay'].size > max_size:
            self._errors['replay'] = [u'Max. file size: 50 kB']
        elif file_name.split('.')[1] != 'hbr':
            self._errors['replay'] = [u'You can only upload files with the .hbr extension!']
            
        return self.cleaned_data['replay']
        
"""
This class is used to make empty formset forms required
See http://stackoverflow.com/questions/2406537/django-formsets-make-first-required/4951032#4951032
"""
class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False
    
    """
    https://docs.djangoproject.com/en/dev/topics/forms/formsets/#custom-formset-validation
    """            
    def clean(self):
        """Checks that no two teams have the same name."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        names = []
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            name = form.cleaned_data['name']
            if name in names:
                raise forms.ValidationError("Teams must have different names!")
            names.append(name)
            
class Required2FormSet(BaseInlineFormSet):
                
    def clean(self):
        """Checks that no two teams have the same name."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        names = []
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            name = form.cleaned_data['name']
            if name in names:
                raise forms.ValidationError("Teams must have different names!")
            names.append(name)
