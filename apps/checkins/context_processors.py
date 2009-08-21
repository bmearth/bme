from django.conf import settings

def ALLOW_CHECKINS(request):
    ''' Provides settings.ALLOW CHECKINS

    '''

    ALLOW_CHECKINS = settings.ALLOW_CHECKINS
    return {
            'ALLOW_CHECKINS': ALLOW_CHECKINS
    }
