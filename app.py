import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

from math_test import run_math_test
from stroop_test import run_stroop_test

st.set_page_config(page_title="Cognitive Assessment Tool", layout="centered")

# ================= SESSION CONTROL =================

if "stage" not in st.session_state:
    st.session_state.stage = "form"

if "participant_data" not in st.session_state:
    st.session_state.participant_data = {}

# ================= PAGE 1: DEMOGRAPHICS =================

if st.session_state.stage == "form":

    st.title("Cognitive Assessment Tool")
    st.subheader("Participant Information")

    name = st.text_input("Name")

    age = st.selectbox("Age Category",
                       ["18-25", "26-35", "36-45", "46-60", "60+"])

    gender = st.selectbox("Gender",
                          ["Male", "Female", "Other"])

    hometown = st.text_input("Home Town")
    current_city = st.text_input("Current City")

    mother_language = st.selectbox("Mother Language",
                                   ["English", "Hindi", "Bengali", "Other"])

    qualification = st.selectbox("Academic Qualification",
                                 ["Pursuing UG", "Pursuing PG",
                                  "Completed UG", "Completed PG"])

    service = st.selectbox("Service Status",
                           ["Employed", "Not Employed", "Retired"])

    handedness = st.selectbox("Handedness",
                              ["Right", "Left", "Ambidextrous"])

    device = st.selectbox("Device Used",
                          ["Laptop", "Desktop", "Mobile", "Tablet"])

    vision = st.selectbox("Vision Status",
                          ["Normal", "Corrected to Normal"])

    prior_test = st.selectbox(
        "Prior exposure to cognitive test recently?",
        ["Yes", "No"]
    )

    st.markdown("---")

    consent = st.checkbox(
        "I provide digital consent to participate in this study. "
        "I confirm I am 12 pass, computer literate, and that my data "
        "will be used only for academic purposes."
    )

    if st.button("Start Test"):

        if not consent:
            st.error("Consent is required before starting.")
        elif name.strip() == "":
            st.error("Please enter your name.")
        else:
            st.session_state.participant_data = {
                "Name": name,
                "Age": age,
                "Gender": gender,
                "HomeTown": hometown,
                "CurrentCity": current_city,
                "MotherLanguage": mother_language,
                "Qualification": qualification,
                "ServiceStatus": service,
                "Handedness": handedness,
                "Device": device,
                "Vision": vision,
                "PriorExposure": prior_test,
                "StartTime": datetime.now()
            }

            st.session_state.stage = "math"
            st.rerun()

# ================= PAGE 2: MATH TEST =================

elif st.session_state.stage == "math":

    result = run_math_test()

    if result is not None:
        st.session_state.participant_data.update(result)
        st.session_state.stage = "transition"
        st.rerun()

# ================= TRANSITION SCREEN =================

elif st.session_state.stage == "transition":

    st.success("Math Test Completed ✅")
    st.write("Next test will begin shortly...")
    time.sleep(3)

    st.session_state.stage = "stroop"
    st.rerun()

# ================= PAGE 3: STROOP TEST =================

elif st.session_state.stage == "stroop":

    result = run_stroop_test()

    if result is not None:
        st.session_state.participant_data.update(result)
        st.session_state.stage = "save"
        st.rerun()

# ================= SAVE DATA =================

elif st.session_state.stage == "save":

    st.success("All Tests Completed Successfully 🎉")

    st.session_state.participant_data["EndTime"] = datetime.now()

    df = pd.DataFrame([st.session_state.participant_data])

    file_path = "results.csv"

    if os.path.exists(file_path):
        df.to_csv(file_path, mode="a", header=False, index=False)
    else:
        df.to_csv(file_path, index=False)

    st.success("Data Saved Successfully ✅")

    st.write("Thank you for participating in the study.")

    if st.button("Finish"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
