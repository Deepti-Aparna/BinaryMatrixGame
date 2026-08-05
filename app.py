from flask import Flask, render_template, request, redirect
import time
import random

app = Flask(__name__)

# ---------------- CONFIG ----------------
ADMIN_PASSWORD = "next"
TOTAL_ROUNDS = 20

# ---------------- GAME LOGIC ----------------
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


# ---------------- GLOBAL STATE ----------------
scores = {}
round_number = 1
matrix = generate_matrix()
correct_answer = calculate_answer(matrix)
submissions = []
round_winner = None


# ---------------- HOME ----------------
# @app.route('/', methods=['GET', 'POST'])
# def home():
#     global round_winner
#
#     message = ""
#     winner = round_winner
#
#     if request.method == 'POST':
#         name = request.form['name'].strip()
#         answer = request.form['answer'].strip()
#
#         is_correct = answer == correct_answer
#
#         submissions.append({
#             'name': name,
#             'answer': answer,
#             'correct': is_correct,
#             'time': time.time()
#         })
#
#         submissions.sort(key=lambda x: x['time'])
#
#         if is_correct:
#             if round_winner is None:
#                 round_winner = name
#                 winner = name
#
#                 scores[name] = scores.get(name, 0) + 1
#
#                 message = f"🏆 {name} answered first! (+1 point)"
#             else:
#                 message = f"✅ Correct, but {round_winner} was first."
#         else:
#             message = "❌ Wrong answer."
#
#     is_admin = request.args.get("admin") == "true"
#
#     leaderboard = sorted(scores.items(), key=lambda x: x[1], reverse=True)
#
#     return render_template(
#         'index.html',
#         matrix=matrix,
#         message=message,
#         round_number=round_number,
#         total_rounds=TOTAL_ROUNDS,
#         scores=leaderboard,
#         admin=is_admin,
#         winner=winner
#     )

@app.route('/')
def home():
    is_admin = request.args.get("admin") == "true"

    leaderboard = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return render_template(
        'index.html',
        matrix=matrix,
        message="",
        round_number=round_number,
        total_rounds=TOTAL_ROUNDS,
        scores=leaderboard,
        admin=is_admin,
        winner=round_winner
    )

# ---------------- ADMIN PANEL ----------------
@app.route('/admin')
def admin_panel():
    password = request.args.get("password")

    if password != ADMIN_PASSWORD:
        return "Access Denied ❌", 403

    # Sort leaderboard by highest score
    leaderboard = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Overall champion
    champion = leaderboard[0] if leaderboard else None

    return render_template(
        'admin.html',
        round_number=round_number,
        total_rounds=TOTAL_ROUNDS,
        winner=round_winner,
        leaderboard=leaderboard,
        champion=champion,
        submissions=submissions
    )
# ---------------- NEXT ROUND ----------------
@app.route('/next')
def next_round():
    global matrix, correct_answer, submissions, round_number, round_winner

    password = request.args.get("password")

    if password != ADMIN_PASSWORD:
        return "Access Denied ❌", 403

    if round_number >= TOTAL_ROUNDS:
        return redirect('/admin?password=' + ADMIN_PASSWORD)

    round_number += 1
    matrix = generate_matrix()
    correct_answer = calculate_answer(matrix)
    submissions = []
    round_winner = None

    return redirect('/?admin=true')


# ---------------- RESET GAME ----------------
@app.route('/reset')
def reset_game():
    global scores, round_number, matrix, correct_answer, submissions, round_winner

    password = request.args.get("password")

    if password != ADMIN_PASSWORD:
        return "Access Denied ❌", 403

    scores = {}
    round_number = 1
    matrix = generate_matrix()
    correct_answer = calculate_answer(matrix)
    submissions = []
    round_winner = None

    return redirect('/?admin=true')


# ---------------- STATUS API ----------------
@app.route('/status')
def status():
    if round_winner:
        return {
            "winner": round_winner,
            "message": f"🏆 {round_winner} is the FIRST correct answer!"
        }

    return {
        "winner": "",
        "message": ""
    }

@app.route('/submit', methods=['POST'])
def submit_answer():
    global round_winner, scores, submissions, correct_answer

    name = request.form['name'].strip()
    answer = request.form['answer'].strip()

    # Normalize both answers
    answer = answer.replace(" ", "")
    expected = correct_answer.replace(" ", "")

    is_correct = (answer == expected)

    submissions.append({
        'name': name,
        'answer': answer,
        'correct': is_correct,
        'time': time.time()
    })

    submissions.sort(key=lambda x: x['time'])

    if is_correct:

        # First correct answer of this round
        if round_winner is None:
            round_winner = name
            scores[name] = scores.get(name, 0) + 1

            return {
                'success': True,
                'winner': round_winner,
                'message': f'🏆 {name} answered first! (+1 point)'
            }

        # Correct but not first
        return {
            'success': True,
            'winner': round_winner,
            'message': f'✅ Correct, but {round_winner} was first.'
        }

    # Wrong answer
    return {
        'success': False,
        'winner': round_winner or '',
        'message': f'❌ Wrong answer. Expected format: Rmax-Cmax-XOR'
    }

@app.route('/round_status')
def round_status():
    return {
        "round": round_number
    }
# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)