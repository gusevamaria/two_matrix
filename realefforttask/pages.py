from ._builtin import Page, WaitPage
from .models import Constants, Task


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
                'correct': num_correct
            })
        return {
            'num_rounds': Constants.num_rounds,
            'round': self.round_number,
            'players': players
        }


page_sequence = [
    WorkPage,
    WaitForResults,
    Results
]
