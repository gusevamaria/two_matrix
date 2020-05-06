from ._builtin import Page, WaitPage
from .models import Constants, Task
from . import models
import logging

logger = logging.getLogger(__name__)
import numpy as np


def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return -1


class WorkPage(Page):
    timer_text = 'Оставшееся время до завершения этого раунда:'
    timeout_seconds = Constants.task_time
    form_model = models.Player
    form_fields = ['hidden_total_answer', 'hidden_correct_answer']


class Results(Page):
    form_model = models.Player
    form_fields = ['rank_disclosure']


class Introduction(Page):
    def is_displayed(self):
        return self.subsession.round_number == 1


class Question(Page):
    form_model = models.Player
    form_fields = ['training_answer_All']

    def is_displayed(self):
        return self.subsession.round_number == 1

    def training_answer_All_error_message(self, value):
        if value != Constants.training_answer_All_correct:
            return 'Ваш ответ "{}" не верен. Попробуйте ещё раз'.format(value)


class Feedback(Page):
    def is_displayed(self):
        return self.subsession.round_number == 1


class Contacts(Page):
    def is_displayed(self):
        return self.subsession.round_number == 1

    form_model = 'player'
    form_fields = ['fname', 'lname', 'otchestvo', 'age', 'city', 'sex', 'phone']


class StartAll(Page):
    def is_displayed(self):
        return self.subsession.round_number == 1

# class ExpectedResult(Page):
#     # def is_displayed(self):
#     #     return self.subsession.round_number == 1
#
#     form_model = 'player'
#     form_fields = ['expected_result', 'radio_select1', 'radio_select2', 'radio_select3', 'radio_select4']

class ExpectedResult(Page):
    # def is_displayed(self):
    #     return self.subsession.round_number == 1

    form_model = 'player'
    form_fields = ['expected_result', 'inter_question_1', 'inter_question_2', 'inter_question_3', 'inter_question_4']

class MyWaitPage(WaitPage):
    template_name = 'realefforttask/MyWaitPage.html'


class WaitForResults(WaitPage):
    after_all_players_arrive = 'set_ranking'


class Payoffs(Page):
    def is_displayed(self):
        return self.subsession.round_number == Constants.num_rounds

    def vars_for_template(self):
        allplayers = self.group.get_players()
        total_score = self.participant.payoff_plus_participation_fee()
        # total_score = sum([sum([p.total_score for p in pp.in_all_rounds()]) for pp in allplayers])
        # total_payoff = sum([sum([p.payoff for p in pp.in_all_rounds()]) for pp in allplayers])
        return {
            'total_score': total_score,
            # 'total_payoff': total_payoff,
        }


class EndQuestionnaire(Page):
    def is_displayed(self):
        return self.subsession.round_number == Constants.num_rounds
    form_model = models.Player
    form_fields = [
        'end_question_1', 'end_question_2', 'end_question_3',
        'end_question_4', 'end_question_5', 'end_question_6',
        'end_question_7', 'end_question_8'
        ]


page_sequence = [
    Introduction,
    Contacts,
    Question,
    Feedback,
    StartAll,
    MyWaitPage,
    WorkPage,
    ExpectedResult,
    WaitForResults,
    #Results,
    EndQuestionnaire,
    Payoffs,
]
