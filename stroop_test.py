import streamlit as st
import random
import time
import pandas as pd
from streamlit_autorefresh import st_autorefresh

TOTAL_QUESTIONS = 42
TIME_LIMIT = 5

COLORS = {
    "RED": "red",
    "GREEN": "green",
    "BLUE": "blue",
    "YELLOW": "yellow"
}

NEUTRAL_WORDS = ["DOG", "CAR", "TREE", "HOUSE"]


# ---------------- QUESTION GENERATION ----------------
def generate_question():
    q_type = random.choice(["congruent", "incongruent", "neutral"])

    if q_type == "neutral":
        word = random.choice(NEUTRAL_WORDS)
        color = random.choice(list(COLORS.values()))
        return word, color, "Neutral"

    word = random.choice(list(COLORS.keys()))
    if q_type == "congruent":
        color = COLORS[word]
        condition = "Congruent"
    else:
        color = random.choice([c for c in COLORS.values() if c != COLORS[word]])
        condition = "Incongruent"

    return word, color, condition


def record_response(results, q_no, word, color, condition, answer, correct, rt):
    results.append({
        "Question": q_no,
        "Word": word,
        "Font Color": color,
        "Condition": condition,
        "Response": answer if answer else "No Response",
        "Correct": correct,
        "Reaction Time (s)": rt
    })


def next_question():
    st.session_state.stroop_q_index += 1
    st.session_state.stroop_start_time = time.time()
    st.session_state.stroop_answered = False
    (
        st.session_state.stroop_word,
        st.session_state.stroop_color,
        st.session_state.stroop_condition
    ) = generate_question()


# ---------------- MAIN FUNCTION ----------------
def run_stroop_test():

    st.header("🧠 Stroop Color–Word Test")

    # Initialize stroop-specific session states
    if "stroop_q_index" not in st.session_state:
        st.session_state.stroop_q_index = 1
        st.session_state.stroop_results = []
        st.session_state.stroop_start_time = time.time()
        (
            st.session_state.stroop_word,
            st.session_state.stroop_color,
            st.session_state.stroop_condition
        ) = generate_question()
        st.session_state.stroop_answered = False

    # ---------------- FINISH CONDITION ----------------
    if st.session_state.stroop_q_index > TOTAL_QUESTIONS:

        df = pd.DataFrame(st.session_state.stroop_results)

        total_trials = len(df)
        total_errors = total_trials - df["Correct"].sum()
        error_rate = (total_errors / total_trials) * 100

        df_correct = df[df["Correct"] == True]
        mean_rt = df_correct["Reaction Time (s)"].dropna().mean()

        cong_rt = df_correct[df_correct["Condition"] == "Congruent"]["Reaction Time (s)"].mean()
        incong_rt = df_correct[df_correct["Condition"] == "Incongruent"]["Reaction Time (s)"].mean()

        stroop_effect = None
        if pd.notna(cong_rt) and pd.notna(incong_rt):
            stroop_effect = incong_rt - cong_rt

        # Clear stroop states so next participant is fresh
        for key in list(st.session_state.keys()):
            if key.startswith("stroop_"):
                del st.session_state[key]

        return {
            "Stroop_Error_Rate": round(error_rate, 2),
            "Stroop_Mean_RT": round(mean_rt, 2) if pd.notna(mean_rt) else None,
            "Stroop_Interference": round(stroop_effect, 2) if stroop_effect else None,
            "Stroop_Total_Trials": total_trials
        }

    # ---------------- TIMER ----------------
    elapsed = time.time() - st.session_state.stroop_start_time
    remaining = max(0, int(TIME_LIMIT - elapsed))
    st_autorefresh(interval=1000, key="stroop_timer")

    st.write(f"### Question {st.session_state.stroop_q_index} / {TOTAL_QUESTIONS}")
    st.warning(f"⏱ Time left: {remaining} seconds")

    # ---------------- DISPLAY ----------------
    st.markdown(
        f"<h1 style='color:{st.session_state.stroop_color}; text-align:center;'>"
        f"{st.session_state.stroop_word}</h1>",
        unsafe_allow_html=True
    )

    # ---------------- ANSWER BUTTONS ----------------
    cols = st.columns(4)
    for color_name, col in zip(COLORS.keys(), cols):
        with col:
            if st.button(color_name,
                         key=f"stroop_{st.session_state.stroop_q_index}_{color_name}") \
                         and not st.session_state.stroop_answered:

                rt = round(elapsed, 2)
                correct = color_name.lower() == st.session_state.stroop_color

                record_response(
                    st.session_state.stroop_results,
                    st.session_state.stroop_q_index,
                    st.session_state.stroop_word,
                    st.session_state.stroop_color,
                    st.session_state.stroop_condition,
                    color_name,
                    correct,
                    rt
                )

                st.session_state.stroop_answered = True
                next_question()
                st.rerun()

    # ---------------- TIMEOUT ----------------
    if remaining == 0 and not st.session_state.stroop_answered:

        record_response(
            st.session_state.stroop_results,
            st.session_state.stroop_q_index,
            st.session_state.stroop_word,
            st.session_state.stroop_color,
            st.session_state.stroop_condition,
            None,
            False,
            None
        )

        next_question()
        st.rerun()

    return None
