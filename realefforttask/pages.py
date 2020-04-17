from ._builtin import Page, WaitPage
from .models import Constants, Task
from . import models
#import logging
#logger = logging.getLogger(__name__)
import numpy as np

def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return -1

class WorkPage(Page):
    timer_text = 'Оставшееся время до завершения этого раунда:'
    timeout_seconds = Constants.task_time
    hidden_correct_input = ['hidden_correct_input']

class WaitForResults(WaitPage):
    pass

class Results(Page):
    def vars_for_template(self):
        players = []
        for p in self.group.get_players():
            tasks = Task.objects.filter(
                player=p,
                round_number=self.round_number
            )
            print(p)
            num_correct = 0
            for t in tasks:
                if t.answer == t.correct_answer:
                    num_correct += 1
            players.append({
                'id': p.participant.id_in_session,
                'total': len(tasks),
                'correct': num_correct,
                'tr_class': 'table-danger' if p.participant.id_in_session == self.player.participant.id_in_session else ''
            })
            sorted_players = sorted(players, key=lambda i: i['correct'], reverse = True)
        return {
            'qty_rounds': Constants.num_rounds,
            'round': self.round_number,
            'players': sorted_players,
            'position': find(sorted_players, 'id', self.player.participant.id_in_session)+1
        }


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
            return 'Ваш ответ "{}" не верен. Попробуйте сложить еще раз'.format(value)

class Feedback(Page):
    def is_displayed(self):
        return self.subsession.round_number == 1

class Contacts(Page):
    def is_displayed(self):
        return self.subsession.round_number == 1
    form_model = 'player'
    form_fields = ['fname', 'lname', 'age', 'sex']


class StartAll(Page):
    def is_displayed(self):
        return self.subsession.round_number == 1

class ExpectedResult(Page):
    def is_displayed(self):
        return self.subsession.round_number == 1
    form_model = 'player'
    form_fields = ['expected_result', 'fields']




page_sequence = [
    Introduction,
    Question,
    Feedback,
    Contacts,
    StartAll,
    WorkPage,
    ExpectedResult,
    WaitForResults,
    Results
]
