from ._builtin import Page, WaitPage
from .models import Constants, Task
from . import models
#import logging
#logger = logging.getLogger(__name__)
import numpy as np


class WorkPage(Page):
    timer_text = 'Оставшееся время до завершения этого раунда:'
    timeout_seconds = Constants.task_time



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
                'tr_class': 'active' if p.participant.id_in_session == self.participant.id else ''
            })
            sorted_players = sorted(players, key=lambda i: i['correct'], reverse = True)
        return {
            'qty_rounds': Constants.num_rounds,
            'round': self.round_number,
            'players': sorted_players,
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
    form_model = 'player'
    form_fields = ['name', 'phone']

class StartAll(Page):
    def is_displayed(self):
        return self.subsession.round_number == 1


page_sequence = [
    # Introduction,
    # Question,
    # Feedback,
    # StartAll,
    WorkPage,
    WaitForResults,
    Results
]
