from points.forms import PointForm

form = PointForm()

def ol_media(request):
    '''provides the media for an olwidget for maps data being dyn-ajax

    '''
    rendered_style = [ u'<link href="%s" rel="stylesheet"/>' %v 
                        for v in form.media._css['all']]

    string = form.media.render()

    return {
        'points_form_media': string,
        'form_css': rendered_style,
    }

def GAK(request):
    ''' Provides settings.GOOGLE_API_KEY as GAK

    '''

    from django.conf import settings
    GAK = settings.GOOGLE_API_KEY
    return {
            'GAK': GAK
    }
