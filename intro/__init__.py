from otree.api import *
from otree.settings import DEBUG, LANGUAGE_CODE
from common.pages import TranslatedPage, ManualAdvancePage, manual_advance_admin_vars, LANGUAGE_MAP

doc = """
Your app description
"""

def _(s):
    LANGUAGE_MAP["de"] = {
        "I am 18 years or older, have read the above information and I consent to participate in this study": "Ich bin mindestens 18  Jahre alt, habe die obigen Informationen gelesen und möchte ausdrücklich an der Studie teilnehmen.",
    }
    if LANGUAGE_CODE in LANGUAGE_MAP.keys():
        return LANGUAGE_MAP[LANGUAGE_CODE][s]
    return s


class C(BaseConstants):
    NAME_IN_URL = 'intro'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    
    ADVANCE_PAGES = ['Instructions']


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    consent_given = models.BooleanField(initial=False, label=_("I am 18 years or older, have read the above information and I consent to participate in this study"), widget=widgets.CheckboxInput)
    consent_berlin = models.BooleanField(initial=False, label=
        "Ich habe die Datenschutzinformationen gelesen und bin mit der Teilnahme am Experiment und der genannten Datenverarbeitung einverstanden",
                                        widget=widgets.CheckboxInput)


# PAGE FUNCTIONS
def vars_for_admin_report(subsession: Subsession):
    return manual_advance_admin_vars(subsession, C.ADVANCE_PAGES)


# PAGES
class ConsentBerlin(Page):
    form_model = 'player'
    form_fields = ['consent_berlin']


class Consent(TranslatedPage):
    form_model = 'player'
    form_fields = ['consent_given']

    def vars_for_template(player: Player):
        duration = player.session.config.get('duration', 120)
        participation_fee = player.session.config.get('participation_fee', 0.0)
        return dict(
            duration=duration,
            fix_pay=participation_fee
        )


class Instructions(TranslatedPage, ManualAdvancePage):
    pass


page_sequence = [ConsentBerlin, Consent, Instructions]
