import subprocess
import tempfile
import textwrap

QUESTIONS = {
    'determine_impact': (
        ('Will this have an impact that will last beyond this week or this '
         'month?'),
        'How will it change my job, my career, my life?',
        'How will this further a long-term goal of mine?',
        'How important is that goal?',
    ),
    'one_to_ten': (
        'On a scale of one to ten, how important is this?',
    ),
    'choosing_the_essential': (
        'What are your values?',
        'What are your goals?',
        'What do you love?',
        'What is important to you?',
        'What has the biggest impact?'
    ),
}


def conduct_survey(questions, answers):
    q_a = []
    for q, a in zip(questions, answers):
        print(q)
        # Open an editor if text is present, else just read from stdin
        answer = vim_edit(q, a) if a else input()
        q_a.append((q, answer))
    return q_a


def vim_edit(question, text):
    with tempfile.NamedTemporaryFile('w+') as fp:
        # Print question and blank line
        fp.write(textwrap.dedent('''> {}

        {}'''.format(question, text)))
        # Reset to start of file
        fp.seek(0)
        subprocess.call(['vim', fp.name])
        return '\n'.join([line for line in fp if line.strip() and not
                         line.startswith('>')])
