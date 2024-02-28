from otree.api import *
from otree.settings import DEBUG, LANGUAGE_CODE
from common.pages import TranslatedPage, LANGUAGE_MAP

doc = """
Your app description
"""


def _(s):
    LANGUAGE_MAP["de"] = {
        "female": "weiblich",
        "male": "männlich",
        "other / I prefer not to tell": "anderes / möchte ich nicht sagen",
        "What is your gender?": "Was ist Ihr Geschlecht?",
        "What is your age?": "Wie alt sind Sie?",
        "What is your field of studies?": "Was studieren Sie?",
        "Economics": "Volkswirtschaftslehre",
        "Business Administration": "Betriebswirtschaftslehre",
        "Other Social Sciences": "Andere Sozialwissenschaften",
        "Psychology": "Psychologie",
        "Humanities": "Geisteswissenschaften",
        "Natural Sciences": "Naturwissenschaften",
        "Other": "Andere",
        "How many semesters have you completed so far?": "Wie viele Semester haben Sie bisher absolviert?",
        "How would you rate your overall mood today?": "Wie würden Sie Ihre Stimmung heute insgesamt bewerten?",
        "very bad": "sehr schlecht",
        "bad": "schlecht",
        "neutral": "neutral",
        "good": "gut",
        "very good": "sehr gut",
        "How would you rate your mood during the experiment?": "Wie würden Sie Ihre Stimmung während des Experiments bewerten?",
        "How would you rate your level of exhaustion on a scale from 1 to 6?": "Wie würden Sie Ihre Erschöpfung auf einer Skala von 1 bis 6 bewerten?",
        "1 - not exhausted at all": "1 - überhaupt nicht erschöpft",
        "6 - very exhausted": "6 - sehr erschöpft",
        "How strenuous do you think today’s experiment was on a scale from 1 to 6?": "Wie anstrengend denken Sie, dass das Experiment heute auf einer Skala von 1 bis 6 war?",
        "1 - not strenuous at all": "1 - überhaupt nicht anstrengend",
        "6 - very strenuous": "6 - sehr anstrengend",
        "How many of the seven questions of Part 3 Task 3.1 did you know already?": "Wie viele der sieben Fragen von Teil 3 Aufgabe 3.1 kannten Sie bereits?",
        "How often have you participated in experiments?": "Wie oft haben Sie an Experimenten teilgenommen?",
        "never before": "noch nie",
        "once before": "einmal",
        "2-5 times": "2-5 mal",
        "more often": "öfter",
        "How many of the other participants in the room do you know personally (approximately)?": "Wie viele der anderen Teilnehmer im Raum kennen Sie persönlich (ungefähr)?",
        "How would you rate your risk appetite on a scale from 1 to 6?": "Wie würden Sie Ihre Risikobereitschaft auf einer Skala von 1 bis 6 bewerten?",
        "1 - very risk averse": "1 - sehr risikoavers",
        "6 - very risk seeking": "6 - sehr risikofreudig",
        "What was your math grade at the end of school?": "Wie war Ihre Mathematiknote am Ende der Schule?",
        "satisfactory": "befriedigend",
        "sufficient": "ausreichend",
        "deficient or inadequate": "mangelhaft oder ungenügend",
    }
    if LANGUAGE_CODE in LANGUAGE_MAP.keys():
        return LANGUAGE_MAP[LANGUAGE_CODE][s]
    return s


class C(BaseConstants):
    NAME_IN_URL = 'demographics'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # demographics
    gender = models.IntegerField(choices=[(1, _("female")), (2, _("male")), (3, _("other / I prefer not to tell"))],
                                 widget=widgets.RadioSelect, label=_("What is your gender?"))
    age = models.IntegerField(min=18, max=110, label=_("What is your age?"))
    field_of_studies = models.IntegerField(choices=[
        (1, _("Economics")),
        (2, _("Business Administration")),
        (3, _("Other Social Sciences")),
        (4, _("Psychology")),
        (5, _("Humanities")),
        (6, _("Natural Sciences")),
        (7, _("Other"))
    ], widget=widgets.RadioSelect, label=_("What is your field of studies?"))
    num_semesters = models.IntegerField(min=0, label=_("How many semesters have you completed so far?"))

    math_grade = models.IntegerField(choices=[
        (1, _("very good")),
        (2, _("good")),
        (3, _("satisfactory")),
        (4, _("sufficient")),
        (5, _("deficient or inadequate"))
    ], widget=widgets.RadioSelect, label=_("What was your math grade at the end of school?"))

    risk_appetite = models.IntegerField(choices=[1, 2, 3, 4, 5, 6], widget=widgets.RadioSelect, label=_("How would you rate your risk appetite on a scale from 1 to 6?"))

    # questionnaire
    mood_today = models.IntegerField(choices=[
        (1, _("very bad")),
        (2, _("bad")),
        (3, _("neutral")),
        (4, _("good")),
        (5, _("very good"))
    ], widget=widgets.RadioSelect, label=_("How would you rate your overall mood today?"))
    mood_experiment = models.IntegerField(choices=[
        (1, _("very bad")),
        (2, _("bad")),
        (3, _("neutral")),
        (4, _("good")),
        (5, _("very good"))
    ], widget=widgets.RadioSelect, label=_("How would you rate your mood during the experiment?"))
    exhaustion = models.IntegerField(choices=[1, 2, 3, 4, 5, 6], widget=widgets.RadioSelect, label=_("How would you rate your level of exhaustion on a scale from 1 to 6?"))
    strenuousness = models.IntegerField(choices=[1, 2, 3, 4, 5, 6], widget=widgets.RadioSelect, label=_("How strenuous do you think today’s experiment was on a scale from 1 to 6?"))
    num_crt_known = models.IntegerField(min=0, label=_("How many of the seven questions of Part 3 Task 3.1 did you know already?"))
    num_previous_participation = models.IntegerField(choices=[
        (0, _("never before")),
        (1, _("once before")),
        (2, _("2-5 times")),
        (3, _("more often"))
    ], widget=widgets.RadioSelect, label=_("How often have you participated in experiments?"))
    num_known_participants = models.IntegerField(min=0, label=_("How many of the other participants in the room do you know personally (approximately)?"))


# PAGES
class Part4Announcement(TranslatedPage):
    pass


class Part4Waitpage(WaitPage):
    def is_displayed(player):
        return not DEBUG


class Demographics(TranslatedPage):
    form_model = 'player'
    form_fields = ["gender", "age", "field_of_studies", "num_semesters", "math_grade", "risk_appetite"]


class Questionnaire(TranslatedPage):
    form_model = 'player'
    form_fields = ["mood_today", "mood_experiment", "exhaustion", "strenuousness", "num_crt_known", "num_previous_participation", "num_known_participants"]


class Payments(TranslatedPage):
    def vars_for_template(player):
        pp = player.participant
        ps = player.session

        context = dict()
        if ps.config.get('experiment', None) == "stroop":
            part1_points = pp.vars.get("part1_points", cu(32))
            part1_task1_points = pp.vars.get("stroop_points", cu(0))
            part1_task2_points = pp.vars.get("crt_points", cu(0))
            part1_task3_points = pp.vars.get("hl_points", cu(32))
            context.update({
                "part1_points": part1_points,
                "part1_eur": part1_points.to_real_world_currency(ps),
                "part1_task1_points": part1_task1_points,
                "part1_task1_eur": part1_task1_points.to_real_world_currency(ps),
                "part1_task2_points": part1_task2_points,
                "part1_task2_eur": part1_task2_points.to_real_world_currency(ps),
                "part1_task3_points": part1_task3_points,
                "part1_task3_eur": part1_task3_points.to_real_world_currency(ps),
                "crt_num_correct": pp.vars.get("crt_num_correct", 0),
                "hl_lottery_choice": "A" if pp.vars.get("hl_chose_a", True) else "B",
                "hl_row": pp.vars.get("hl_row", 1),
                "hl_outcome": "€0.20" if pp.vars.get("hl_pay_left", True) else "€4.20",
            })

        context.update({
            "treatment": ps.config.get("experiment", None),
            "show_up_eur": ps.config['participation_fee'],

            "part2_points": pp.vars.get("part2_points", cu(0)),
            "part2_eur": pp.vars.get("part2_points", cu(0)).to_real_world_currency(ps),

            "market_repetition": pp.vars.get("market_repetition", 1),

            "total_points": pp.payoff,
            "total_eur": pp.payoff_plus_participation_fee(),
        })
        return context


page_sequence = [
    Part4Announcement,
    Part4Waitpage,
    Demographics,
    Questionnaire,
    Payments
]
