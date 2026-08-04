from flask import Flask, render_template, request, redirect
import time
import random

def generate_matrix():
    return [[format(random.randint(0, 15), '04b') for _ in range(4)] for _ in range(4)]

def calculate_answer(matrix):
    dec = [[int(x, 2) for x in row] for row in matrix]
    row_max = max(sum(r) for r in dec)
    col_max = max(sum(dec[r][c] for r in range(4)) for c in range(4))
    diag_xor = 0
    for i in range(4):
        diag_xor ^= dec[i][i]
    return f"{row_max}-{col_max}-{diag_xor}"

app = Flask(__name__)
ADMIN_PASSWORD = "next"

round_number = 1
matrix = generate_matrix()
correct_answer = calculate_answer(matrix)
submissions = []
@app.route('/', methods=['GET', 'POST'])
def home():
    message = ""
    winner = None

    correct_subs = [s for s in submissions if s['correct']]
    if correct_subs:
        winner = correct_subs[0]['name']

    if request.method == 'POST':
        name = request.form['name']
        answer = request.form['answer'].strip()

        is_correct = answer == correct_answer

        submissions.append({
            'name': name,
            'answer': answer,
            'correct': is_correct,
            'time': time.time()
        })

        submissions.sort(key=lambda x: x['time'])

        if is_correct:
            winner = [s for s in submissions if s['correct']][0]['name']
            if name == winner:
                message = f"🏆 {name} is the FIRST correct answer!"
            else:
                message = f"✅ Correct, but {winner} was first."
        else:
            message = "❌ Wrong answer."

    return render_template('index.html',
                           matrix=matrix,
                           message=message,
                           round_number=round_number,
                           admin=True,
                           winner=winner)

@app.route('/next')
def next_round():
    global matrix, correct_answer, submissions, round_number
    password = request.args.get("password")

    if password != ADMIN_PASSWORD:
        return "Access Denied ❌", 403

    if round_number >= 20:
        return render_template(
            'index.html',
            matrix=matrix,
            message="🏁 Game Over! 20 rounds completed.",
            winner=None,
            round_number=round_number
        )
    round_number += 1
    matrix = generate_matrix()
    correct_answer = calculate_answer(matrix)
    submissions = []

    return render_template(
        'index.html',
        matrix=matrix,
        message=f"🔄 Round {round_number} started!",
        winner=None,
        round_number=round_number,
        admin=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)