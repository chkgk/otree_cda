from otree.api import *
from otree.settings import DEBUG, LANGUAGE_CODE

from common.pages import TranslatedPage, LANGUAGE_MAP

import random

doc = """
Your app description
"""


def _(s):
    LANGUAGE_MAP["de"] = {
        "I am 18 years or older, have read the above information and I consent to participate in this study": "Ich bin mindestens 18  Jahre alt, habe die obigen Informationen gelesen und möchte ausdrücklich an der Studie teilnehmen.",
        "Afraid / Scared / Anxious": "ängstlich / verängstigt / besorgt",
        "Anxiety / Fear / Nervousness": "Angst / Furcht / Nervosität",
        "Excitement / Pleasure / Enthusiasm": "Aufregung / Freude / Begeisterung",
        "Bored / Jaded / Uninterested": "gelangweilt / ermattet / desinteressiert",
        "Neutral (no emotional reaction)": "neutral (keine emotionale Reaktion)",
        "Excited / Eager / Enthusiastic": "aufgeregt / gespannt / enthusiastisch",
        "Sad / Gloomy / Depressed": "traurig / düster / depressiv",
        "Calm / Relaxed / Peaceful": "ruhig / entspannt / friedlich",
        "The movie clip made me feel...": "Nach dem Videoclip fühle ich mich...",
        "Do you think this clip is a nice filler task to be used in future experiments?": "Denken Sie, dass dieser Clip eine schöne Fülleraufgabe für zukünftige Experimente ist?",
        "Yes": "Ja",
        "No": "Nein",
        "Intensity (1 = very little; 9 = very much)": "Intensität (1 = sehr gering; 9 = sehr hoch)",
        "Please fill in the intensity of the selected feeling.": "Bitte füllen Sie die Intensität des ausgewählten Gefühls aus."
    }
    if LANGUAGE_CODE in LANGUAGE_MAP.keys():
        return LANGUAGE_MAP[LANGUAGE_CODE][s]
    return s


class C(BaseConstants):
    NAME_IN_URL = 'mcheck'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    CLIP_FEELING_CHOICES = [
        (1, _("Afraid / Scared / Anxious")),
        (2, _("Bored / Jaded / Uninterested")),
        (3, _("Neutral (no emotional reaction)")),
        (4, _("Excited / Eager / Enthusiastic")),
        (5, _("Sad / Gloomy / Depressed")),
        (6, _("Calm / Relaxed / Peaceful"))
    ]

    CLIP_DATA = {
        'intense': {
            "seconds": 7*60,
            "poster": "loading.gif",
            "url": "video/intense.webm",
            "width": 940,
            "height": 530,
            "youtube": "https://www.youtube-nocookie.com/embed/eGdUE1SldvE?si=-mbhPIhE-pY2PnDm&controls=0&autoplay=1"
        },
        'calm': {
            "seconds": 4*60,
            "poster": "loading.gif",
            "url": "video/calm.webm",
            "width": 706,
            "height": 530,
            "youtube": "https://www.youtube-nocookie.com/embed/S8fpFGnsq3w?si=Wx1BcDbCJraklm6j&amp;controls=0&autoplay=1"
        }
    }
    CLIP_NAMES = list(CLIP_DATA.keys())


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    condition = models.StringField()
    clip = models.StringField(choioes=C.CLIP_NAMES)
    movie_feeling = models.IntegerField(choices=[(1, _("Anxiety / Fear / Nervousness")), (2, _("Excitement / Pleasure / Enthusiasm"))], widget=widgets.RadioSelect)
    movie_filler_task = models.BooleanField(choices=[(True, _("Yes")), (False, _("No"))], widget=widgets.RadioSelect, label=_("Do you think this clip is a nice filler task to be used in future experiments?"))
    movie_intensity_anxiety = models.IntegerField(min=1, max=9, label=_("Intensity (1 = very little; 9 = very much)"), blank=True)
    movie_intensity_excitement = models.IntegerField(min=1, max=9, label=_("Intensity (1 = very little; 9 = very much)"), blank=True)


# FUNCTIONS



def clip_feeling_choices(player: Player):
    choices = C.CLIP_FEELING_CHOICES.copy()
    random.shuffle(choices)
    return choices


def creating_session(subsession: Subsession):
    # check if we have a valid number of players, skipped in debug
    num_players = len(subsession.get_players())
    players_per_group = int(num_players / 2)

    if num_players % 2 != 0:
        raise ValueError('Number of players must be even')

    if not DEBUG and num_players not in (16, 20):
        raise ValueError('Number of players must be 16 or 20')

    # first half of players forms a group, second half forms another group
    subsession.set_group_matrix([[i + 1 for i in range(players_per_group)], [i + 1 for i in range(players_per_group, players_per_group * 2)]])
    
    # select a repetition to pay
    subsession.session.vars['pay_repetition'] = random.randint(1, 2)

    # assign condition to players
    # store participant variables
    control_group = random.randint(1, 2)
    for player in subsession.get_players():
        player.condition = 'control' if player.group.id_in_subsession == control_group else 'treatment'
        player.clip = 'calm' if player.condition == 'control' else 'intense'
        player.participant.vars['group_id'] = player.group.id_in_subsession
        player.participant.vars['players_per_group'] = players_per_group
        player.participant.vars['condition'] = player.condition


# PAGES
class Part1Announcement(TranslatedPage):
    pass


class Instructions(TranslatedPage):
    pass


class Movie(TranslatedPage):
    def get_timeout_seconds(player):
        seconds = C.CLIP_DATA[player.clip]['seconds']
        return seconds

    def vars_for_template(player):
        context = C.CLIP_DATA[player.clip]
        return context


class Evaluation(TranslatedPage):
    form_model = 'player'
    form_fields = ['movie_feeling', 'movie_filler_task', 'movie_intensity_anxiety', 'movie_intensity_excitement']

    @staticmethod
    def error_message(player, values):
        if values['movie_feeling'] == 1 and values['movie_intensity_anxiety'] is None:
            return _("Please fill in the intensity of the selected feeling. 1")

        if values['movie_feeling'] == 2 and values['movie_intensity_excitement'] is None:
            return _("Please fill in the intensity of the selected feeling. 2")


class Part2Announcement(TranslatedPage):
    pass


page_sequence = [
    Part1Announcement,
    Instructions,
    Movie,
    Evaluation,
    Part2Announcement
]
