import streamlit as st
# import random
import unicodedata
import re
import os
import sys
# from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
from datetime import datetime as dt, timezone
# import traceback
# import time
# import threading

def clear_page(page_id):
    if page_id != st.session_state.curr_page_id:
        st.session_state.current_question = []
        st.session_state.current_score = 0
        st.session_state.total_questions = 0
        st.session_state.answer_to_check = ""
        st.session_state.correct_answer = None
        st.session_state.answer_input = None
        st.session_state.result_message = ""
        st.session_state.answer_display_message = ""
        st.session_state.append_answer = True
    st.session_state.curr_page_id = page_id
    


def radio_change():
    st.session_state.current_question = []
    st.session_state.answer_to_check = ""
    st.session_state.current_score = 0
    st.session_state.total_questions = 0

# def store_and_clear_answer():
#     st.session_state.answer_to_check = st.session_state.answer_input
#     st.session_state.answer_input = ""

def reset():
    st.session_state.current_score = 0
    st.session_state.total_questions = 0


def auto_advance_delay():
    """Return the effective delay before advancing to the next question."""
    base_delay = st.session_state.auto_advance
    if not base_delay:
        return 0
    success_messages = ("Good job!", "Helyes!")
    if st.session_state.answer_checked and not any(
        success_message in st.session_state.result_message
        for success_message in success_messages
    ):
        return min(60, base_delay + 5)
    return base_delay



def new_question(gen_question):
    ''' 
    This runs whichever question-generator function specifies the target features of the relevant part of speech.
    It clears the current user answer and asserts that the user's answer has not yet been checked.
    '''

#    try:
    st.session_state.answer_checked = False
    st.session_state.answer_to_check = ""
    st.session_state["_bevlat_clear_answer_input"] = True
    st.session_state.result_message = ""
    st.session_state.answer_display_message = ""
    st.session_state.button_disable = False
    st.session_state.append_answer = True
    st.session_state.gen_string = None
    st.session_state.pop("answer_credit_override", None)

    st.session_state.current_question = gen_question()
    # except:
    #     # st.write("Your selected options have resulted in an impossibility: try selecting some additional options.")
    #     st.write("Something went wrong.")
    #     return



def remove_macrons(text):
    for macron, vowel in {"ā": "a",
                        "ē": "e",
                        "ī": "i",
                        "ō": "o",
                        "ū": "u"}.items():
        if macron in text:
            text = text.replace(macron, vowel)
    return text


def tokenize_morphology_answer(text):
    """Return lowercase word tokens and standalone person digits 1-3.

    All other non-letter/digit characters are treated purely as separators.
    Grammatical interpretation and alias normalization belong to
    exercise-specific parsers built on top of this tokenizer.
    """
    if not isinstance(text, str):
        return []
    return re.findall(r"[^\W\d_]+|[1-3]", text.casefold(), flags=re.UNICODE)


def submit_and_check_answer():
    userid = st.session_state.user_id
    user_answer = st.session_state.answer_input
    
    if not user_answer: # if an empty form is submitted, don't process the answer or disable the submit button.
        st.session_state.button_disable = False
        st.session_state.answer_display_message = "Your answer was blank! Enter something and hit 'Check Answer' (or press the return key), or click 'New Question' again if you want to skip this one."

    else:
        st.session_state.button_disable = True
        st.session_state.answer_to_check = user_answer.strip().lower()
    
        # combine macrons on correct answer (just in case)
        if isinstance(st.session_state.correct_answer,list):
            for i, answer in enumerate(st.session_state.correct_answer):
                st.session_state.correct_answer[i] = unicodedata.normalize("NFC", answer)
        else:
            st.session_state.correct_answer = unicodedata.normalize("NFC", st.session_state.correct_answer)
        correct_answer = st.session_state["correct_answer"]

        # set phrase for correct answer(s)
        if isinstance(correct_answer, list):
            st.session_state["answer_phrase"] = f"The correct answers are: {' *or* '.join(correct_answer)}"
        else:
            st.session_state["answer_phrase"] = f"The correct answer is: {correct_answer}"

        # Set display message to show user answer and correct answer(s)
        st.session_state.answer_display_message = f"""Your answer is: {user_answer}  
        {st.session_state["answer_phrase"]}""" # note: the first line ends with two spaces to force the line-break

    ### above here is definitely correct ###
        if not st.session_state.answer_checked:
            st.session_state.total_questions += 1
            st.session_state.answer_checked = True

            # combine macrons on user answer (just in case)
            user_answer_check = unicodedata.normalize("NFC", st.session_state.answer_to_check)

            # if normalizing v to u is selected, replace all v with u in user answer and correct answer
            correct_answer_check = st.session_state.correct_answer
            if st.session_state["cons_u_normalize"] is True:
                user_answer_check = user_answer_check.replace("v", "u")
                if isinstance(correct_answer_check, list):
                    for i,answer_option in enumerate(correct_answer_check):
                        correct_answer_check[i] = answer_option.replace("v", "u")
                else:
                    correct_answer_check = correct_answer_check.replace("v", "u")


            # if 'enforce macrons' isn't checked, remove them from both the user answer and the correct answer
            if not st.session_state.enforce_macrons[f"{st.session_state.curr_page_id}_enforce_macrons"]:

                if isinstance(correct_answer_check, list):
                    for i,answer_option in enumerate(correct_answer_check):
                        correct_answer_check[i] = remove_macrons(answer_option)
                else:
                    correct_answer_check = remove_macrons(correct_answer_check)

                user_answer_check = remove_macrons(user_answer_check)

            correct_flag = False    # is the answer correct? We don't know yet...

            # check whether answer is correct
            if isinstance(correct_answer_check, list):
                if user_answer_check in correct_answer_check:
                    correct_flag = True
            elif user_answer_check == correct_answer_check:
                correct_flag = True
            
            # set score and correct/incorrect result message
            credit_override = st.session_state.pop("answer_credit_override", None)
            answer_credit = (1 if correct_flag else 0) if credit_override is None else credit_override
            st.session_state.current_score += answer_credit
            if correct_flag is True:
                st.session_state.result_message = "**Good job!**"
            else:
                st.session_state.result_message = "**Incorrect. Better luck next time!**"

            # Correct responses need only the canonical answer. Incorrect responses
            # retain the fuller user-answer/correct-answer comparison.
            if correct_flag:
                st.session_state.answer_display_message = (
                    f":green-background[{st.session_state['answer_phrase']}]"
                )
            else:
                st.session_state.answer_display_message = (
                    f":red-background[Your answer is: {user_answer}]  \n"
                    f":red-background[{st.session_state['answer_phrase']}]"
                )

#            st.write(st.session_state.append_answer)
            if st.session_state.append_answer is False:
                st.session_state.question_list[-1]["answer"] = user_answer
                st.session_state.question_list[-1]["correct"] = (
                    answer_credit if credit_override is not None else correct_flag
                )  # write correctness / partial credit to question_list

                # if st.context.headers["host"].startswith("localhost"):
                if st.user.is_logged_in is True:
                    # pass
                    insert_dict = {
                        "user_id": str(userid),
                        "time_answered": dt.now(timezone.utc).isoformat(),
                        "answer": st.session_state.question_list[-1]
                        }
                    st.session_state.supabase_connection.table("answer").insert(insert_dict).execute()

    if st.session_state.auto_advance:
        st.session_state.auto_advance_trigger = True        
    else:
        st.session_state.auto_advance_trigger = False
    
def send_setting(*args,**kwargs):
    if args:
        for func in args:
            func()
    if st.user.is_logged_in is False:
        return
    else:
        value_dict = {}
        for key, val in kwargs.items():
            value_dict[key] = val
        value_dict["user_id"] = st.session_state.user_id
        value_dict["setting_value"] = st.session_state[kwargs["setting_name"]]
        st.session_state.supabase_connection.table("user_setting").upsert(value_dict, on_conflict="user_id, streamlit_page, setting_name").execute()
        # st.session_state.user_settings # update df

def save_defaults(page_id, defaults, **kwargs):
    if st.user.is_logged_in is False:
        return
    values_list = []
    for val_name,val in kwargs.items():
        value_dict = {}
        value_dict["user_id"] = st.session_state.user_id
        value_dict["streamlit_page"] = f"{page_id}.py"
        defaults[val_name] = val
        value_dict["setting_name"] = val_name
        value_dict["setting_value"] = val
        values_list.append(value_dict)
    st.session_state.supabase_connection.table("user_setting").upsert(values_list, on_conflict="user_id, streamlit_page, setting_name").execute()
    st.session_state.default_settings[f"{page_id}.py"] = defaults
    return

def clear_defaults(page_id):
    if not st.user.is_logged_in:
        return
    if st.session_state.default_settings.get(f"{page_id}.py") is not None:
        defaults_to_clear = list(st.session_state.default_settings[f"{page_id}.py"])
        # for key in defaults:
        #     st.session_state.default_settings[f"{page_id}.py"][key] = None
        #     defaults_to_clear.append(key)
            # defaults[key] = None
        st.session_state.supabase_connection.table("user_setting").delete().eq("user_id", st.session_state.user_id).eq("streamlit_page",f"{page_id}.py").in_("setting_name",defaults_to_clear).execute()
        st.session_state.default_settings.pop(f"{page_id}.py")
    return