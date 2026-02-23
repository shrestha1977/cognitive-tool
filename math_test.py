import streamlit as st
import random
import time

TEST_DURATION = 300
QUESTION_POOL_SIZE = 100


# ================= QUESTION GENERATOR =================
def generate_math_questions(num=QUESTION_POOL_SIZE):
    questions = []

    for _ in range(num):

        difficulty = random.choices(
            ["easy", "moderate", "hard"],
            weights=[0.4, 0.35, 0.25]
        )[0]

        if difficulty == "easy":
            pattern = random.choice(["add", "sub", "mul", "div"])

            if pattern == "add":
                a, b = random.randint(1, 50), random.randint(1, 50)
                expr = f"{a} + {b}"

            elif pattern == "sub":
                a, b = random.randint(20, 70), random.randint(1, 20)
                expr = f"{a} - {b}"

            elif pattern == "mul":
                a, b = random.randint(2, 12), random.randint(2, 12)
                expr = f"{a} * {b}"

            else:
                b = random.randint(2, 12)
                answer = random.randint(2, 12)
                a = b * answer
                expr = f"{a} / {b}"

        elif difficulty == "moderate":
            pattern = random.choice(["add_mul", "sub_mul", "div_add", "add_div"])

            if pattern == "add_mul":
                a, b, c = random.randint(1, 20), random.randint(1, 10), random.randint(1, 10)
                expr = f"{a} + {b} * {c}"

            elif pattern == "sub_mul":
                a, b, c = random.randint(20, 50), random.randint(1, 10), random.randint(1, 10)
                expr = f"{a} - {b} * {c}"

            elif pattern == "div_add":
                b = random.randint(2, 10)
                answer = random.randint(2, 10)
                a = b * answer
                c = random.randint(1, 20)
                expr = f"{a} / {b} + {c}"

            else:
                b = random.randint(2, 10)
                answer = random.randint(2, 10)
                a = b * answer
                c = random.randint(1, 20)
                expr = f"{c} + {a} / {b}"

        else:
            pattern = random.choice(["bracket_mul", "bracket_div", "complex_mix"])

            if pattern == "bracket_mul":
                a, b, c = random.randint(1, 20), random.randint(1, 20), random.randint(1, 10)
                expr = f"({a} - {b}) * {c}"

            elif pattern == "bracket_div":
                b = random.randint(2, 10)
                answer = random.randint(2, 10)
                a = b * answer
                c = random.randint(1, 10)
                expr = f"({a} / {b}) + {c}"

            else:
                a, b, c, d = random.randint(1, 20), random.randint(1, 10), random.randint(2, 10), random.randint(1, 10)
                expr = f"({a} + {b}) - {c} * {d}"

        answer = int(eval(expr))
        questions.append((expr, answer, difficulty))

    return questions


# ================= MAIN FUNCTION =================
def run_math_test():

    st.header("Numerical Ability Cognitive Test")

    # Initialize session keys
    if "math_start_time" not in st.session_state:
        st.session_state.math_start_time = time.time()
        st.session_state.math_questions = generate_math_questions()
        st.session_state.math_current_index = 0
        st.session_state.math_correct = 0
        st.session_state.math_attempted = 0
        st.session_state.math_difficulty = {
            "low_attempted": 0,
            "moderate_attempted": 0,
            "high_attempted": 0,
            "low_correct": 0,
            "moderate_correct": 0,
            "high_correct": 0,
        }

    elapsed = time.time() - st.session_state.math_start_time
    remaining = int(TEST_DURATION - elapsed)

    mins = max(0, remaining) // 60
    secs = max(0, remaining) % 60
    st.metric("⏳ Time Remaining", f"{mins:02d}:{secs:02d}")

    # ================= TIME UP =================
    if remaining <= 0:

        attempted = st.session_state.math_attempted
        correct = st.session_state.math_correct

        stats = st.session_state.math_difficulty
        weights = {"low": 1, "moderate": 2, "high": 3}

        weighted_correct = (
            stats["low_correct"] * weights["low"] +
            stats["moderate_correct"] * weights["moderate"] +
            stats["high_correct"] * weights["high"]
        )

        weighted_attempted = (
            stats["low_attempted"] * weights["low"] +
            stats["moderate_attempted"] * weights["moderate"] +
            stats["high_attempted"] * weights["high"]
        )

        weighted_accuracy = weighted_correct / weighted_attempted if weighted_attempted > 0 else 0
        speed_efficiency = min(attempted / QUESTION_POOL_SIZE, 1)
        numerical_score = (0.7 * weighted_accuracy) + (0.3 * speed_efficiency)

        # Clear math-specific states
        for key in list(st.session_state.keys()):
            if key.startswith("math_"):
                del st.session_state[key]

        return {
            "Math_Attempted": attempted,
            "Math_Correct": correct,
            "Math_Weighted_Accuracy": round(weighted_accuracy, 2),
            "Math_Speed_Efficiency": round(speed_efficiency, 2),
            "Math_Numerical_Score": round(numerical_score, 2)
        }

    # ================= DISPLAY QUESTION =================
    idx = st.session_state.math_current_index

    if idx >= len(st.session_state.math_questions):
        st.session_state.math_questions.extend(generate_math_questions(50))

    question, correct_answer, difficulty = st.session_state.math_questions[idx]

    st.subheader(f"Question: {question} = ?")

    with st.form("math_form", clear_on_submit=True):
        ans = st.text_input("Your answer")
        submit = st.form_submit_button("Submit")

    if submit:

        answer_clean = ans.strip()

        if answer_clean == "":
            st.session_state.math_current_index += 1
            st.rerun()

        try:
            numeric_answer = int(answer_clean)
            is_correct = numeric_answer == correct_answer

            st.session_state.math_attempted += 1

            if is_correct:
                st.session_state.math_correct += 1

            if difficulty == "easy":
                level = "low"
            elif difficulty == "moderate":
                level = "moderate"
            else:
                level = "high"

            st.session_state.math_difficulty[f"{level}_attempted"] += 1

            if is_correct:
                st.session_state.math_difficulty[f"{level}_correct"] += 1

            st.session_state.math_current_index += 1
            st.rerun()

        except ValueError:
            st.warning("Enter valid integer or leave blank to skip.")
