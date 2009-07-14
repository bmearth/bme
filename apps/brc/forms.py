import logging
from django import forms
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from brc.models import Year, PlayaEvent, ArtInstallation, ThemeCamp
from swingtime.conf import settings as swingtime_settings
from swingtime.models import Event, Occurrence, EventType, Note
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
	fmt=swingtime_settings.TIMESLOT_TIME_FORMAT):
	
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
	fmt=swingtime_settings.TIMESLOT_TIME_FORMAT):

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
	A Widget that splits datetime input into a custom Select for dates and
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
class MultipleIntegerField(forms.MultipleChoiceField):
    '''
    A form field for handling multiple integers.
    
    '''
    
    #---------------------------------------------------------------------------
    def __init__(self, choices, size=None, label=None, widget=None):
        if widget is None:
            widget = forms.SelectMultiple(attrs={'size' : size or len(choices)})
        super(MultipleIntegerField, self).__init__(
            required=False,
            choices=choices,
            label=label,
            widget=widget,
        )

class PlayaModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


#===============================================================================
class PlayaEventForm(forms.ModelForm):
	'''
	A simple form for adding and updating Event attributes
	'''
	
	curr_year='2009'
	year = Year.objects.filter(year=curr_year)[0]
	playa_day_choices=[(d, d.strftime('%A, %B %d')) for d in year.daterange()]
	playa_day_choices_short=[(d, d.strftime('%A %d')) for d in year.daterange()]

	title  = forms.CharField(required=True, max_length=40, label='Title')
	print_description  = forms.CharField(required=True, max_length=150, label='Print Description', help_text="Print description for publication in the What Where When. 150 characters max.", widget=widgets.Textarea(attrs={'rows':'5', 'cols':'40'}))
	description  = forms.CharField(required=True, max_length=2000, label='Online Description', widget=widgets.Textarea(attrs={'rows':'5', 'cols':'40'}))
	event_type = forms.ModelChoiceField(queryset=EventType.objects.all(), empty_label=None, label='Event Type')
	url  = forms.URLField(required=False, verify_exists=True, label='URL')
	contact_email = forms.EmailField(required=False, label='Contact email')
	other_location = forms.CharField(required=False, label='Other Location', max_length=150)
	hosted_by_camp = PlayaModelChoiceField(required=False, label='Hosted By Camp',queryset=ThemeCamp.objects.filter(year=year).extra(select={'lower_name': 'lower(name)'}).order_by('lower_name'))
	located_at_art = PlayaModelChoiceField(required=False, label='Located at Art Installation', queryset=ArtInstallation.objects.filter(year=year).extra(select={'lower_name': 'lower(name)'}).order_by('lower_name'))
	start_time=forms.DateTimeField(label='Start', required=True, widget=PlayaSplitDateTimeWidget(choices=playa_day_choices))
	check_location=forms.BooleanField(required=False, label='Check Playa Info for camp location', initial=False)
	end_time=forms.DateTimeField(label='End', required=True, widget=PlayaSplitDateTimeWidget(choices=playa_day_choices))
	all_day=forms.BooleanField(required=False, label='All Day Event')
	repeats=forms.BooleanField(required=False, label='Repeats', help_text='If your event repeats at different times on different days, check the days on which it repeats, and edit the times on the following page.')
	repeat_days = MultipleIntegerField(playa_day_choices_short, label='Repeat Days',widget=forms.CheckboxSelectMultiple)
	list_online=forms.BooleanField(required=False, label='List Event Online', initial=True)
	list_contact_online=forms.BooleanField(required=False, label='List Contact Info Online', initial=True)

	def __init__(self, *args, **kws):
		super(PlayaEventForm, self).__init__(*args, **kws)

		# This is irrelevant now because we dont allow editing of the occurrences when editing event metadata, but kept here for now
		if(kws['instance'] is not None):
			# Set the initial form values properly for recurring events
			if(Occurrence.objects.filter(event=self.instance).count()>1):
				self.initial.setdefault('repeats', True)
				repeat_days = []
				for day in self.year.daterange():
					if(Occurrence.objects.filter(event=self.instance, start_time__day=day.day).count()>0):	
						repeat_days.append(day)
				self.initial.setdefault('repeat_days', repeat_days)
			else:
				# Single Event
				occurrence = Occurrence.objects.get(event=self.instance)
				logging.debug(str(occurrence))
				self.initial.setdefault('start_time', occurrence.start_time)
				self.initial.setdefault('end_time', occurrence.end_time)

	def clean(self):
		start=self.cleaned_data['start_time']
		end = self.cleaned_data['end_time']

		if self.cleaned_data['all_day']:
			pass 
		elif self.instance:
			pass
		elif end < start:
			raise forms.ValidationError("Event cannot end before it starts!")
		elif end == start:
			raise forms.ValidationError("Event cannot start and end at the same time!")


		if(self.cleaned_data['hosted_by_camp'] and self.cleaned_data['located_at_art']):
			raise forms.ValidationError("Your Event can be located at EITHER a camp or an art installation (but not both)")
		
		if((self.cleaned_data['hosted_by_camp'] is None) and (self.cleaned_data['located_at_art'] is None) and (len(self.cleaned_data['other_location'].strip())<1)):
			raise forms.ValidationError("Your Event must be located at a Camp, or an Art Installation or some Other Location (cant be nowhere)")
		
		# Always return the full collection of cleaned data.
		return self.cleaned_data

	def save(self, year, user, playa_event_id):
		if(playa_event_id is not None):
			existing_event = True
			logging.debug("existing_event = True")
			playa_event = self.instance
		else:
			existing_event = False
			logging.debug("existing_event = False")
			playa_event = PlayaEvent()
		
		playa_event.year=self.year
		playa_event.creator=user
		playa_event.title = self.cleaned_data['title']
		playa_event.slug = slugify(self.cleaned_data['title'])
		playa_event.description = self.cleaned_data['description'].strip()
		playa_event.print_description = self.cleaned_data['print_description'].strip()
		playa_event.event_type = self.cleaned_data['event_type']
		playa_event.url=self.cleaned_data['url']
		playa_event.contact_email=self.cleaned_data['contact_email']
		playa_event.hosted_by_camp=self.cleaned_data['hosted_by_camp']
		playa_event.located_at_art = self.cleaned_data['located_at_art']
		playa_event.other_location=self.cleaned_data['other_location']
		playa_event.check_location=self.cleaned_data['check_location']
		playa_event.all_day = self.cleaned_data['all_day']
		playa_event.list_online=self.cleaned_data['list_online']
		playa_event.list_contact_online=self.cleaned_data['list_contact_online']

		playa_event.save()

		# TODO ... Handle for All Day Events

		if(existing_event):
			# Existing Event, update occurrence(s)
			# TODO
			# Not sure what to do if the time is changed for a recurring event?
			pass
		else:
			# New Event, add occurrence
			if(self.cleaned_data['repeats']):
				if(self.cleaned_data['all_day']):
					start_time = datetime.strptime("1/1/01 00:00", "%d/%m/%y %H:%M").time()
					end_time = datetime.strptime("1/1/01 23:59", "%d/%m/%y %H:%M").time()
				else:
					start_time = self.cleaned_data['start_time'].time()
					end_time = self.cleaned_data['end_time'].time()
				for day in self.cleaned_data['repeat_days'] :
					event_start = datetime.combine(datetime.strptime(day, "%Y-%m-%d"), start_time) 
					event_end = datetime.combine(datetime.strptime(day, "%Y-%m-%d"), end_time) 
					playa_event.add_occurrences(event_start,event_end)
			elif(self.cleaned_data['all_day']):
				start_time = datetime.strptime("1/1/01 00:00", "%d/%m/%y %H:%M").time()
				end_time = datetime.strptime("1/1/01 23:59", "%d/%m/%y %H:%M").time()
				event_start = datetime.combine(self.cleaned_data['start_time'].date(), start_time) 
				event_end = datetime.combine(self.cleaned_data['end_time'].date(), end_time) 
				playa_event.add_occurrences(event_start, event_end)
			else:	
				playa_event.add_occurrences(self.cleaned_data['start_time'], self.cleaned_data['end_time'])

		return playa_event
	class Meta:
		model = PlayaEvent
		exclude = ('year', 'slug', 'location_point', 'location_track', 'creator')
		fields = ['title', 'print_description', 'description','event_type','url','contact_email','hosted_by_camp','located_at_art','other_location','check_location','all_day', 'repeats', 'repeat_days', 'start_time','end_time', 'list_online', 'list_contact_online']

class PlayaEventOccurrenceForm(forms.ModelForm):
	'''
	For use in editing occurrences
	'''
	curr_year='2009'
	year = Year.objects.filter(year=curr_year)[0]
	playa_day_choices=[(d, d.strftime('%A, %B %d')) for d in year.daterange()]
	start_time=forms.DateTimeField(label='Start', widget=PlayaSplitDateTimeWidget(choices=playa_day_choices))
	end_time=forms.DateTimeField(label='End', widget=PlayaSplitDateTimeWidget(choices=playa_day_choices))

	def clean(self):
		cleaned_data = self.cleaned_data
		start=cleaned_data.get('start_time')
		end = cleaned_data.get('end_time')
	
		if(self.instance.event.playaevent.all_day):
			pass
		elif end < start:
			raise forms.ValidationError("Event cannot end before it starts!")
    
		# Always return the full collection of cleaned data.
		return cleaned_data
    
	def save(self, event, occurrence_id):
		if(occurrence_id is not None):
			if(event.playaevent.all_day):
				start_time = datetime.strptime("1/1/01 00:00", "%d/%m/%y %H:%M").time()
				end_time = datetime.strptime("1/1/01 23:59", "%d/%m/%y %H:%M").time()
				self.instance.start_time = datetime.combine(self.cleaned_data['start_time'], start_time)
				self.instance.end_time = datetime.combine(self.cleaned_data['start_time'], end_time)
				self.instance.save()
			else:
				self.instance.start_time = self.cleaned_data['start_time']
				self.instance.end_time = self.cleaned_data['end_time']
				self.instance.save()
		else:
			# Add new Occurrence
			event.add_occurrences(self.cleaned_data['start_time'], self.cleaned_data['end_time'])
