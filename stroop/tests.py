from otree.api import Currency as c, currency_range, expect, Bot
from . import *


def call_live_method(method, **kwargs):
    if kwargs['page_class'] != Task:
        return

    # we simulate that the first player in the group gets two trials
    # get a first trial
    trial_data = method(1, {'type': 'stroop-start'})
    assert trial_data

    # get a response
    response_to_response = method(1, {
        'type': 'stroop-response',
        'response': 'red',
        'uuid': trial_data[1]['trial']['uuid'],
        'response_time': 500
    })
    assert response_to_response

    # Todo: should probably check if the responses are well formed. So far we only check if they are non-empty


class PlayerBot(Bot):
    def play_round(self):
        yield PreTaskQuestions, {
            'mother_tongue_german': random.choice([True, False]),
            'vision_impairment': random.randint(0, 3),
            'vision_impairment_color': random.randint(0, 3),
        }

        yield Task

        if self.player.id_in_group == 1:
            # there should be at exactly two trial in the db from the testing of the live methods
            assert len(Trial.filter(player=self.player)) == 2

        yield PostTaskQuestions, {
            'stroop_difficulty': random.randint(1, 6)
        }

        yield CRT3, {
            "crt3_sheep": random.randint(0, 15),
            "crt3_daughters": random.choice(['Emily', 'June']),
            "crt3_dirt": random.randint(0, 100)
        }

        yield Submission(HL, {
            f"hl_a_{i}": random.choice([True, False]) for i in range(1, 11)
        }, check_html=False)
        yield Part2Announcement
