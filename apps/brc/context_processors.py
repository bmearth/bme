from django.conf import settings # import the settings file

def bme_production(context):
    # return the value you want as a dictionary. you may add multiple values in there.
    return {'BME_PRODUCTION': settings.BME_PRODUCTION}