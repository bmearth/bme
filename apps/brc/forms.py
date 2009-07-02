from django import forms
from django.utils.translation import ugettext_lazy as _
from brc.models import Year, PlayaEvent
from swingtime.conf import settings as swingtime_settings
from swingtime.models import Event, Occurrence
from swingtime.forms import timeslot_options
from swingtime import utils
from datetime import datetime, date, time


MINUTES_INTERVAL = swingtime_settings.TIMESLOT_INTERVAL.seconds // 60
SECONDS_INTERVAL = utils.time_delta_total_seconds(swingtime_settings.DEFAULT_OCCURRENCE_DURATION)

#-------------------------------------------------------------------------------
def timeslot_options(
    interval=swingtime_settings.TIMESLOT_INTERVAL,
    start_time=swingtime_settings.TIMESLOT_START_TIME,
    end_delta=swingtime_settings.TIMESLOT_END_TIME_DURATION,
    fmt=swingtime_settings.TIMESLOT_TIME_FORMAT
):
    '''
    Create a list of time slot options for use in swingtime forms.
    
    The list is comprised of 2-tuples containing a 24-hour time value and a 
    12-hour temporal representation of that offset.
    
    '''
    dt = datetime.combine(date.today(), time(0))
    dtstart = datetime.combine(dt.date(), start_time)
    dtend = dtstart + end_delta
    options = []

    while dtstart <= dtend:
        options.append((str(dtstart.time()), dtstart.strftime(fmt)))
        dtstart += interval
    
    return options

#-------------------------------------------------------------------------------
def timeslot_offset_options(
    interval=swingtime_settings.TIMESLOT_INTERVAL,
    start_time=swingtime_settings.TIMESLOT_START_TIME,
    end_delta=swingtime_settings.TIMESLOT_END_TIME_DURATION,
    fmt=swingtime_settings.TIMESLOT_TIME_FORMAT
):
    '''
    Create a list of time slot options for use in swingtime forms.
    
    The list is comprised of 2-tuples containing the number of seconds since the
    start of the day and a 12-hour temporal representation of that offset.
    
    '''
    dt = datetime.combine(date.today(), time(0))
    dtstart = datetime.combine(dt.date(), start_time)
    dtend = dtstart + end_delta
    options = []

    delta = utils.time_delta_total_seconds(dtstart - dt)
    seconds = utils.time_delta_total_seconds(interval)
    while dtstart <= dtend:
        options.append((delta, dtstart.strftime(fmt)))
        dtstart += interval
        delta += seconds
    
    return options

default_timeslot_options = timeslot_options()
default_timeslot_offset_options = timeslot_offset_options()

class PlayaSplitDateTimeWidget(forms.MultiWidget):
    '''
    A Widget that splits datetime input into a SelectDateWidget for dates and
    Select widget for times.
    
    '''
    #---------------------------------------------------------------------------
    def __init__(self, choices, attrs=None):
        widgets = (
            forms.Select(choices=choices, attrs=attrs), 
            forms.Select(choices=default_timeslot_options, attrs=attrs)
        )
        super(PlayaSplitDateTimeWidget, self).__init__(widgets, attrs)

    #---------------------------------------------------------------------------
    def decompress(self, value):
        if value:
            return [value.date(), value.time().replace(microsecond=0)]
        
        return [None, None]


#===============================================================================
class PlayaEventForm(forms.ModelForm):
    '''
    A simple form for adding and updating Event attributes

    '''

    #===========================================================================
    class Meta:
        model = PlayaEvent
        fields = ['type', 'description', 'url', 'contact_email', 'hosted_by_camp', 'located_at_art']
        exclude = ('creator', 'slug', 'location_point', 'location_track')

    #---------------------------------------------------------------------------
    def __init__(self, *args, **kws):
        super(PlayaEventForm, self).__init__(*args, **kws)
        self.fields['description'].required = False


    
    
class PlayaEventOccurrenceForm(forms.Form):

  def __init__(self, *args, **kws):
      super(PlayaEventOccurrenceForm, self).__init__(*args, **kws)
      # Because we'd like to have the Date be selected from a pulldown of 
      # valid dates, we needed a way to pass the year to the form, then
      # to populate the select widget.
      # 
      # The year object is passed in as an "initial" dict from the view.
      #
      # I couldn't figure out a way to pass the choices in if the widget
      # for the day field was set in the day field definition, so what worked
      # was to define the widget and the choices altogether right here.
      #
      # If the format of the pulldown needs to be changed, it should be
      # changed here as well. This is uglier than it should be.
      # -cjs
      #
      year = self.initial.get('year', None)
      if year:
        playa_day_choices=[(d, d.strftime('%A, %B %d')) for d in year.daterange()]
        self.fields['start_time'].widget=PlayaSplitDateTimeWidget(choices=playa_day_choices)
        self.fields['end_time'].widget=PlayaSplitDateTimeWidget(choices=playa_day_choices)


  start_time=forms.DateTimeField(
    label='Start: ',
  )
  
  end_time=forms.DateTimeField(
    label='End: '
  )

  def clean(self):
    cleaned_data = self.cleaned_data
    start=cleaned_data.get('start_time')
    end = cleaned_data.get('end_time')
    
    if end < start:
      raise forms.ValidationError("Event cannot end before it starts!")
    
    # Always return the full collection of cleaned data.
    return cleaned_data
    
  def save(self, event):
    event.add_occurrences(
      self.cleaned_data['start_time'], 
      self.cleaned_data['end_time'],
    )