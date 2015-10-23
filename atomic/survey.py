import sys

QUESTIONS = {
    'power_of_less': (
        ('Will this have an impact that will last beyond this week or this '
        'month?'),
        'How will it change my job, my career, my life?',
        'How will this further a long-term goal of mine?',
        'How important is that goal?',
    ),
    'one_to_ten': (
        'On a scale of one to ten, how important is this?',
    )
}


def conduct_survey(questions, answers):
    q_a = []
    for q, a in zip(questions, answers):
        print(q)
        sys.stdout.write(a)
        q_a.append((q, input()))
    return q_a
