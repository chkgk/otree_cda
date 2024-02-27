from otree.api import *
import random
import uuid
from otree.settings import DEBUG, LANGUAGE_CODE
from common.pages import TranslatedPage, LANGUAGE_MAP

doc = """
Stroop Task as used in Kocher et al.
"""


def _(s):
    LANGUAGE_MAP["de"] = {
        "A farmer had 15 sheep and all but 8 died. How many are left?": "Ein Bauer hatte 15 Schafe und alle bis auf 8 starben. Wie viele sind übrig?",
        "Emily's father has three daughters. The first two are called April and May. What is the name of the third daughter?": "Emilys Vater hat drei Töchter. Die ersten beiden heißen April und Mai. Wie heißt die dritte Tochter?",
        "How many cubic feet of dirt are there in a hole that is 3’ deep x 3’ wide x 3’ long?": "Wie viele Kubikfuß Erde gibt es in einem Loch, das 3 Fuß tief x 3 Fuß breit x 3 Fuß lang ist?",
        "How strenuous did you find the previous task on a scale of 1 to 6?": "Wie anstrengend fanden Sie die vorhergehende Aufgabe auf einer Skala von 1 bis 6?",
        "Is your native language German?": "Ist Ihre Muttersprache Deutsch?",
        "Are you suffering from ametropia?": "Leiden Sie unter einer Fehlsichtigkeit?",
        "Are you suffering from color blindness?": "Leiden Sie unter einer Farbenfehlsichtigkeit?",
        "Yes": "Ja",
        "No": "Nein",
        "Yes, myopia": "Ja, unter Kurzsichtigkeit",
        "Yes, farsightedness": "Ja, unter Weitsichtigkeit",
        "Yes, other": "Ja, anderes",
        "Yes, red green weakness": "Ja, unter Rot-Grün-Schwäche",
        "Yes, red green blindness": "Ja, unter Rot-Grün-Blindheit",
        "1 - not strenuous at all": "1 - gar nicht anstrengend",
        "6 - very strenuous": "6 - sehr anstrengend",
    }
    if LANGUAGE_CODE in LANGUAGE_MAP.keys():
        return LANGUAGE_MAP[LANGUAGE_CODE][s]
    return s

class C(BaseConstants):
    NAME_IN_URL = 'stroop'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    TASK_DURATION = 300  # seconds, set to 300

    POINTS_PER_EUR = 160
    CRT3_VAR_PAY = cu(0.5 * POINTS_PER_EUR)  # cu are in points!
    STROOP_FIX_PAY = cu(3.00 * POINTS_PER_EUR)  # cu are in points!

    COLORS = ['purple', 'brown', 'yellow', 'green', 'red', 'blue']
    COLOR_NAMES = {
        'purple': 'violett',
        'brown': 'braun',
        'yellow': 'gelb',
        'green': 'grün',
        'red': 'rot',
        'blue': 'blau',
    }

    HL_LOTTERY = {
        "name": "HL1",
        "lottery_a": {
            "probabilities": [0.5, 0.5],
            "prizes": [
                [0.2 for _ in range(0, 10)],
                [4.2 for _ in range(0, 10)]
            ]
        },
        "lottery_b": {
            "probabilities": [1],
            "prizes": [[0.6, 1.0, 1.4, 1.8, 2.2, 2.6, 3.0, 3.4, 3.8, 4.2]]
        },
    }


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    condition = models.StringField()
    treatment = models.StringField()
    num_trials = models.IntegerField()
    num_correct = models.IntegerField()

    mother_tongue_german = models.BooleanField(label=_("Is your native language German?"), choices=[(True, _("Yes")), (False, _("No"))], widget=widgets.RadioSelect)
    vision_impairment = models.IntegerField(label=_("Are you suffering from ametropia?"), choices=[(0, _("No")), (1, _("Yes, myopia")), (2, _("Yes, farsightedness")), (3, _("Yes, other"))], widget=widgets.RadioSelect)
    vision_impairment_color = models.IntegerField(label=_("Are you suffering from color blindness?"), choices=[(0, _("No")), (1, _("Yes, red green weakness")), (2, _("Yes, red green blindness")), (3, _("Yes, other"))], widget=widgets.RadioSelect)

    stroop_difficulty = models.IntegerField(label=_("How strenuous did you find the previous task on a scale of 1 to 6?"), choices=[(1, _("1 - not strenuous at all")), (2, "2"), (3, "3"), (4, "4"), (5, "5"), (6, _("6 - very strenuous"))], widget=widgets.RadioSelect)

    crt3_sheep = models.IntegerField(label=_("A farmer had 15 sheep and all but 8 died. How many are left?"), min=0, max=15)
    crt3_daughters = models.StringField(label=_("Emily's father has three daughters. The first two are called April and May. What is the name of the third daughter?"))
    crt3_dirt = models.IntegerField(label=_("How many cubic feet of dirt are there in a hole that is 3’ deep x 3’ wide x 3’ long?"), min=0, max=100)

    crt3_score = models.IntegerField()

    hl_a_1 = models.BooleanField(widget=widgets.RadioSelect)
    hl_a_2 = models.BooleanField(widget=widgets.RadioSelect)
    hl_a_3 = models.BooleanField(widget=widgets.RadioSelect)
    hl_a_4 = models.BooleanField(widget=widgets.RadioSelect)
    hl_a_5 = models.BooleanField(widget=widgets.RadioSelect)
    hl_a_6 = models.BooleanField(widget=widgets.RadioSelect)
    hl_a_7 = models.BooleanField(widget=widgets.RadioSelect)
    hl_a_8 = models.BooleanField(widget=widgets.RadioSelect)
    hl_a_9 = models.BooleanField(widget=widgets.RadioSelect)
    hl_a_10 = models.BooleanField(widget=widgets.RadioSelect)


class Trial(ExtraModel):
    player = models.Link(Player)
    uuid = models.StringField()
    decoy_text = models.StringField()
    color = models.StringField()
    is_congruent = models.BooleanField()
    is_correct = models.BooleanField()
    response_ms = models.IntegerField()

    def as_dict(self):
        return {
            'uuid': self.uuid,
            'decoy_text': self.decoy_text,
            'color': self.color,
            'is_congruent': self.is_congruent,
        }


# FUNCTIONS
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
        player.treatment = 'congruent' if player.condition == 'control' else 'incongruent'
        player.participant.vars['group_id'] = player.group.id_in_subsession
        player.participant.vars['players_per_group'] = players_per_group
        player.participant.vars['condition'] = player.condition


def get_trial(is_congruent, exclude_color=None):
    while True:
        color = random.choice(C.COLORS)
        if color != exclude_color:
            break
    decoy = color if is_congruent else random.choice([c for c in C.COLORS if c != color])
    return {'decoy_text': decoy, 'color': color, 'is_congruent': is_congruent}


def create_trial(player: Player, last_trial_color):
    trial = get_trial(is_congruent=player.treatment == 'congruent', exclude_color=last_trial_color)
    trial_obj = Trial.create(player=player, uuid=str(uuid.uuid4()), decoy_text=trial['decoy_text'],
                             color=trial['color'],
                             is_congruent=trial['is_congruent'])
    return trial_obj.as_dict()


def custom_export(players):
    # header row
    yield ['session', 'participant_code', 'id_in_group', "decoy_text", "color", "is_congruent", "is_correct", "response_ms"]
    trials = Trial.filter()
    for t in trials:
        p = t.player
        participant = p.participant
        session = p.session
        yield [session.code, participant.code, p.id_in_group, t.decoy_text, t.color, t.is_congruent, t.is_correct, t.response_ms]


def calculate_payoff(player: Player, lottery):
    max_row = len(lottery["lottery_a"]["prizes"][0])
    random_row = random.randint(1, max_row)
    chose_a = getattr(player, f"hl_a_{random_row}")

    pay_left = random.random() < lottery["lottery_a"]["probabilities"][0]
    if not chose_a:
        lottery_outcome = lottery["lottery_b"]["prizes"][0][random_row - 1]

    else:
        if pay_left:
            lottery_outcome = lottery["lottery_a"]["prizes"][0][random_row - 1]
        else:
            lottery_outcome = lottery["lottery_a"]["prizes"][1][random_row - 1]

    crt3_payoff = cu(player.crt3_score * C.CRT3_VAR_PAY)
    lottery_points = cu(lottery_outcome * C.POINTS_PER_EUR)

    player.payoff = lottery_points + crt3_payoff + C.STROOP_FIX_PAY

    pp = player.participant

    # stroop - task 1.1
    pp.vars["stroop_points"] = C.STROOP_FIX_PAY

    # crt - task 1.2
    pp.vars["crt_points"] = crt3_payoff
    pp.vars["crt_num_correct"] = player.crt3_score

    # hl - task 1.3
    pp.vars["hl_chose_a"] = chose_a
    pp.vars["hl_row"] = random_row
    pp.vars["hl_lottery_low"] = pay_left
    pp.vars["hl_points"] = lottery_points

    # total part 1
    pp.vars["part_1_points"] = player.payoff


# PAGES
class Part1Announcement(TranslatedPage):
    pass


class PreTaskQuestions(TranslatedPage):
    form_model = 'player'
    form_fields = ['mother_tongue_german', 'vision_impairment', 'vision_impairment_color']


class Task(Page):
    timeout_seconds = C.TASK_DURATION

    def live_method(player: Player, data):
        if data['type'] == 'stroop-start':
            trials = Trial.filter(player=player)
            existing_trial = [t for t in trials if t.is_correct is None]
            if existing_trial:
                trial_data = existing_trial[0].as_dict()
                trial_data["decoy_text"] = C.COLOR_NAMES[trial_data["decoy_text"]]
                return {player.id_in_group: {'type': 'stroop-trial', 'trial': trial_data}}

            # new trial 
            if len(trials) > 0:
                last_trial = [t for t in trials if t.is_correct is not None][-1]
                last_trial_color = last_trial.color
            else:
                last_trial_color = None

            trial_data = create_trial(player, last_trial_color)
            trial_data["decoy_text"] = C.COLOR_NAMES[trial_data["decoy_text"]]
            return {player.id_in_group: {'type': 'stroop-trial', 'trial': trial_data}}

        if data['type'] == 'stroop-response':
            # print(data["response"], data["uuid"])
            trials = Trial.filter(player=player, uuid=data["uuid"])
            if trials:
                trial = trials[0]
                trial.response_ms = data["response_time"]
                trial.is_correct = data["response"] == trial.color

                # new trial
                ntrial_data = create_trial(player, trial.color)
                ntrial_data["decoy_text"] = C.COLOR_NAMES[ntrial_data["decoy_text"]]
                return {player.id_in_group: {'type': 'stroop-trial', 'trial': ntrial_data}}

    def before_next_page(player, timeout_happened):
        trials = Trial.filter(player=player)
        player.num_trials = len(trials)
        player.num_correct = len([t for t in trials if t.is_correct])


class PostTaskQuestions(TranslatedPage):
    form_model = 'player'
    form_fields = ['stroop_difficulty']


class CRT3(TranslatedPage):
    form_model = 'player'
    form_fields = ['crt3_sheep', 'crt3_daughters', 'crt3_dirt']

    def before_next_page(player, timeout_happened):
        player.crt3_score = sum([
            player.crt3_sheep == 8,
            player.crt3_daughters.strip().lower() == 'emily',
            player.crt3_dirt == 0
        ])


class HL(TranslatedPage):
    form_model = 'player'
    form_fields = [f"hl_a_{i}" for i in range(1, 11)]

    def js_vars(player: Player):
        return {
            'lotteries': C.HL_LOTTERY,
        }

    def before_next_page(player: Player, timeout_happened):
        calculate_payoff(player, C.HL_LOTTERY)


class Part2Announcement(TranslatedPage):
    pass


page_sequence = [
    Part1Announcement,
    PreTaskQuestions,
    Task,
    PostTaskQuestions,
    CRT3,
    HL,
    Part2Announcement
]
