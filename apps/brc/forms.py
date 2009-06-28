from django import forms
from django.utils.translation import ugettext_lazy as _
from brc.models import PlayaEvent
from schedule.models import Occurrence
import datetime
import time


class SpanForm(forms.ModelForm):

    start = forms.DateTimeField(widget=forms.SplitDateTimeWidget)
    end = forms.DateTimeField(widget=forms.SplitDateTimeWidget, help_text = _("The end time must be later than start time."))

    def clean_end(self):
        if self.cleaned_data['end'] <= self.cleaned_data['start']:
            raise forms.ValidationError(_("The end time must be later than start time."))
        return self.cleaned_data['end']


class PlayaEventForm(SpanForm):
    def __init__(self, hour24=False, *args, **kwargs):
        super(PlayaEventForm, self).__init__(*args, **kwargs)
    
    end_recurring_period = forms.DateTimeField(help_text = _("This date is ignored for one time only events."), required=False)
    
    class Meta:
        model = PlayaEvent
	fields = ['title', 'year', 'start', 'end', 'rule', 'type', 'description', 'url', 'contact_email', 'hosted_by_camp', 'located_at_art']
        exclude = ('creator', 'created_on', 'calendar', 'slug', 'location_point', 'location_track')
        

class OccurrenceForm(SpanForm):
    
    class Meta:
        model = Occurrence
        exclude = ('original_start', 'original_end', 'event', 'cancelled')
