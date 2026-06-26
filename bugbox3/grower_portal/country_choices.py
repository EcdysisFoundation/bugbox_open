
import pycountry


def build_country_choices():
    choices = [('', 'Select country')]
    for country in sorted(pycountry.countries, key=lambda entry: entry.name):
        choices.append((country.alpha_2, country.name))
    return choices


COUNTRY_CHOICES = build_country_choices()
COUNTRY_CODE_TO_NAME = dict(COUNTRY_CHOICES[1:])
