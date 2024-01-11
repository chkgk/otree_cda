from otree.api import *
import random
import uuid

doc = """
Stroop Task as used in Kocher et al.
"""


class C(BaseConstants):
    NAME_IN_URL = 'stroop'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    TASK_DURATION = 300  # seconds, set to 300

    COLORS = ['purple', 'brown', 'yellow', 'green', 'red', 'blue']
    COLOR_NAMES = {
        'purple': 'violett',
        'brown': 'braun',
        'yellow': 'gelb',
        'green': 'grün',
        'red': 'rot',
        'blue': 'blau',
    }



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    treatment = models.StringField()
    num_trials = models.IntegerField()
    num_correct = models.IntegerField()

    mother_tongue_german = models.BooleanField(label="Ist Ihre Muttersprache Deutsch?", choices=[(True, "Ja"), (False, "Nein")], widget=widgets.RadioSelect)
    vision_impairment = models.IntegerField(label="Leiden Sie unter einer Fehlsichtigkeit?", choices=[(0, "Nein"), (1, "Ja, unter Kurzsichtigkeit"), (2, "Ja, unter Weitsichtigkeit"), (3, "Ja, anderes")], widget=widgets.RadioSelect)
    vision_impairment_color = models.IntegerField(label="Leiden Sie unter einer Farbenfehlsichtigkeit?", choices=[(0, "Nein"), (1, "Ja, Rot-Grün-Schwäche"), (2, "Ja, Rot-Grün-Blindheit"), (3, "Ja, anderes")], widget=widgets.RadioSelect)

    stroop_difficulty = models.IntegerField(label="Wie anstrengend fanden Sie die vorhergehende Aufgabe auf einer Skala von 1 bis 6?", choices=[(1, "1 - gar nicht anstrengend"), (2, "2"), (3, "3"), (4, "4"), (5, "5"), (6, "6 - sehr anstrengend")], widget=widgets.RadioSelect)


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
    for player in subsession.get_players():
        player.treatment = player.participant.vars.get('treatment', random.choice(['congruent', 'incongruent']))


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

# PAGES
class PreTaskQuestions(Page):
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


class PostTaskQuestions(Page):
    form_model = 'player'
    form_fields = ['stroop_difficulty']



page_sequence = [
    PreTaskQuestions,
    Task,
    PostTaskQuestions
]
