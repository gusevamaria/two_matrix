from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants


class WorkPage(Page):
    timer_text = 'Оставшееся время до завершения этого раунда:'
    timeout_seconds = Constants.task_time


class WaitPage(Page):
    def is_displayed(self):
        return self.subsession.round_number == Constants.num_rounds

# class Payoffs(Page):
#     def is_displayed(self):
#         return self.subsession.round_number == Constants.num_rounds
#     def vars_for_template(self):
#         round = self.session.vars['paying_rounds']
#         return {"paying_round": str(round)[1:-1],
#                 "final_payoff": self.participant.payoff_plus_participation_fee(),
#                 'player_in_all_rounds': self.player.in_all_rounds()}

class MyWaitPage(WaitPage):
    group_by_arrival_time = True
    def is_displayed(self):
        return self.round_number == 1


page_sequence = [
    WorkPage,
    MyWaitPage,
]
