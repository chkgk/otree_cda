from otree.api import Currency as c, currency_range, expect, Bot
from . import *
import random


class PlayerBot(Bot):
    def play_round(self):
        yield Part4Announcement
        yield Demographics, {
            "gender": random.randint(1, 3),
            "age": random.randint(18, 110),
            "field_of_studies": random.randint(1, 7),
            "num_semesters": random.randint(0, 20),
            "math_grade": random.randint(1, 6),
            "risk_appetite": random.randint(1, 6)
        }
        yield Questionnaire, {
            "mood_today": random.randint(1, 5),
            "mood_experiment": random.randint(1, 5),
            "exhaustion": random.randint(1, 6),
            "strenuousness": random.randint(1, 6),
            "num_crt_known": random.randint(0, 3),
            "num_previous_participation": random.randint(0, 3),
            "num_known_participants": random.randint(0, 40)
        }
        yield Payments
