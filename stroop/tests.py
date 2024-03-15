from otree.api import Currency as c, currency_range, expect, Bot, Submission
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

    cases = [
        # 'random', 
        'selected'
    ]

    def play_round(self):
        yield Part1Announcement
        yield PreTaskQuestions, {
                'mother_tongue_german': random.choice([True, False]),
                'vision_impairment': random.randint(0, 3),
                'vision_impairment_color': random.randint(0, 3),
            }

        yield Submission(Task, check_html=False)

        if self.player.id_in_group == 1:
            # there should be at exactly two trial in the db from the testing of the live methods
            assert len(Trial.filter(player=self.player)) == 2

        yield PostTaskQuestions, {
            'stroop_difficulty': random.randint(1, 6)
        }

        if self.case == 'random':
            crt3_context = {
                "crt3_sheep": random.randint(0, 15),
                "crt3_daughters": random.choice(['Emily', 'June']),
                "crt3_dirt": random.randint(0, 100)
            }
        else:
            crt3_context = {
                "crt3_sheep": 8,  # correct 
                "crt3_daughters": 'Emily',  # correct
                "crt3_dirt": 10  # incorrect
            }
        yield CRT3, crt3_context
        if self.case == ' defined':
            assert self.player.crt3_score == 2

        if self.case == 'random':
            hl_context = {
                f"hl_a_{i}": random.choice([True, False]) for i in range(1, 11)
            }
        else:
            hl_context = {
                "hl_a_1": False,
                "hl_a_2": False,
                "hl_a_3": False,
                "hl_a_4": False,
                "hl_a_5": False,
                "hl_a_6": False,
                "hl_a_7": False,
                "hl_a_8": False,
                "hl_a_9": False,
                "hl_a_10": False,
            }
        yield Submission(HL, hl_context, check_html=False)
        if self.case == 'defined':
            pp = self.participant
            assert pp.vars["hl_chose_a"] == False
            assert pp.vars["hl_points"] == [cu(160*a) for a in [0.6, 1.0, 1.4, 1.8, 2.2, 2.6, 3.0, 3.4, 3.8, 4.2]][pp.vars["hl_row"] - 1]

        yield Part2Announcement
