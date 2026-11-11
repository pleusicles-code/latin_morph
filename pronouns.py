import streamlit as st
import random
import time
import pandas as pd
import ast
import html
import unicodedata
from utils import radio_change, reset, new_question, submit_and_check_answer, clear_page, send_setting, save_defaults, clear_defaults, auto_advance_delay
from exercise_presets import (bool_setting, list_setting, resolve_exercise_settings, initialize_widget_state,
                              widget_key, url_preset_active, exercise_link_popover)
from vocab import import_pronouns

st.set_page_config("BevLat – Névmások", layout="centered")

# if st.session_state.question_list :
questions_asked = st.session_state.question_list

# if "pronouns_enforce_macrons" not in st.session_state:
st.session_state.pronouns_enforce_macrons = st.session_state.enforce_macrons["pronouns_enforce_macrons"]

if "part_gen" not in st.session_state:
    st.session_state.part_gen = None
def choose_genitive(pronoun,case,gen_diff=None):
    # if gen_diff and pronoun in ["nōs","vōs"] and case == "gen":
    if pronoun in ["nōs","vōs"] and case == "gen":
        part_gen = random.choice([True,False])
    else:
        part_gen = None
    st.session_state.part_gen = part_gen


def hungarian_article(word):
    """Select a/az according to the Latin lemma's initial sound."""
    normalized = "".join(
        char for char in unicodedata.normalize("NFD", str(word).lower())
        if unicodedata.category(char) != "Mn"
    )
    if not normalized or normalized[0] not in "aeiouy":
        return "a"
    if len(normalized) > 1 and normalized[0] in "iu" and normalized[1] in "aeiouy":
        if normalized[:2] != "ui":
            return "a"
    return "az"


def submit_pronoun_answer():
    """Preserve the shared correctness check, with Hungarian feedback."""
    submitted = st.session_state.get("answer_input", "")
    correct_answer = st.session_state.get("correct_answer")
    forms = list(correct_answer) if isinstance(correct_answer, list) else [correct_answer]
    submit_and_check_answer()

    if not st.session_state.get("answer_checked"):
        st.session_state.answer_display_message = (
            "Nem adtál meg választ. Írj be egy választ, majd kattints a "
            "**Válasz ellenőrzése** gombra (vagy nyomd meg az Entert), "
            "esetleg lépj tovább az **Új kérdés** gombbal."
        )
        return

    correct_forms = " *vagy* ".join(f"*{form}*" for form in forms)
    answer_phrase = (
        f"A helyes válasz: {correct_forms}"
        if len(forms) == 1 else f"A helyes válaszok: {correct_forms}"
    )
    st.session_state.answer_phrase = answer_phrase
    if "Good job!" in st.session_state.result_message:
        st.session_state.result_message = "**Helyes!**"
        st.session_state.answer_display_message = f":green-background[{answer_phrase}]"
    else:
        st.session_state.result_message = "**Helytelen válasz.**"
        st.session_state.answer_display_message = (
            f":red-background[Válaszod: {submitted}]  \n"
            f":red-background[{answer_phrase}]"
        )


page_id = "pronouns"
clear_page(page_id)
# print(st.session_state.supabase_connection.table("setting_type").select("*").execute().data)


defaults = st.session_state.default_settings.get(f"{page_id}.py", {})
# defaults["demonstratives"] = ["ipse"]
# defaults["gen_forms_diff"] = True

st.markdown("# Névmások")


## IMPORT PRONOUNS ##

pronoun_vocab = import_pronouns()

demonstrative_options = [k for k,v in pronoun_vocab.items() if v.get("type") == "demonstrative"]
personal_options = [k for k,v in pronoun_vocab.items() if v.get("type") == "pers_pron"]
rel_interr_options = [k for k,v in pronoun_vocab.items() if v.get("type") == "rel_interrog"]
indefinite_options = [k for k,v in pronoun_vocab.items() if v.get("type") == "indefinite"]
exercise_schema = {
    "demonstratives": list_setting(demonstrative_options, demonstrative_options),
    "personal_pron": list_setting(personal_options, personal_options),
    "rel_interr": list_setting(rel_interr_options, rel_interr_options),
    "indefinites": list_setting(indefinite_options, indefinite_options),
    "gen_forms_diff": bool_setting(False),
}
exercise_settings = resolve_exercise_settings(page_id, exercise_schema, defaults)
initialize_widget_state(page_id, exercise_settings)
preset_active = url_preset_active(page_id)

## SET OPTIONS ##

option_expander = st.expander("Beállítások", expanded=True)

gen_forms_diff = False
with option_expander:
    pronoun_type_col, options_col = st.columns([2,1], gap="medium")

with pronoun_type_col:
    # demonstratives
    demonstratives = st.multiselect("Válaszd ki, mely mutató névmásokat szeretnéd gyakorolni (alapértelmezés szerint mindegyik ki van választva):",
                                    options=demonstrative_options,
                                    key=widget_key(page_id, "demonstratives"))
    # personal pronouns
    personal_pron = st.multiselect("Válaszd ki, mely személyes névmásokat szeretnéd gyakorolni:",
                                    options=personal_options,
                                    key=widget_key(page_id, "personal_pron"))
    # relative and interrogative pronouns
    rel_interr = st.multiselect("Válaszd ki, mely vonatkozó és kérdő névmásokat szeretnéd gyakorolni:",
                                    options=rel_interr_options,
                                    key=widget_key(page_id, "rel_interr"))

    # indefinite pronouns
    indefinites = st.multiselect("Válaszd ki, mely határozatlan névmásokat szeretnéd gyakorolni:",
                                    options=indefinite_options,
                                    key=widget_key(page_id, "indefinites"))

    # if nos or vos selected: option to distinguish between partitive and non-partitive genitive forms of nōs and vōs
    if any(pn in personal_pron for pn in ["nōs","vōs"]):
        gen_forms_diff = st.checkbox("A partitivusi és nem partitivusi genitivus megkülönböztetése?",
                                        help="Ha be van jelölve, a *nōs* és *vōs* névmásnál külön kérjük a partitivusi vagy a nem partitivusi genitivust. Ha nincs bejelölve, mindkét alakot elfogadjuk.",
                                        key=widget_key(page_id, "gen_forms_diff"))

with options_col:
    st.markdown("Opciók:", help="Ezeket a beállításokat gyakorlás közben is bármikor módosíthatod.")
    def switch_pronoun_macrons():
        st.session_state.enforce_macrons["pronouns_enforce_macrons"] = st.session_state.pronouns_enforce_macrons
        return
    st.checkbox("Hosszú magánhangzók ellenőrzése?",
                help="Ha be van jelölve, a hosszú magánhangzók hibás jelölése hibás válasznak számít. Ha nincs bejelölve, a hosszúságjelek használhatók, de a program nem értékeli őket.",
                key="pronouns_enforce_macrons",
                on_change=send_setting,
                args=(switch_pronoun_macrons,),
                kwargs={"streamlit_page":"pronouns.py","setting_name":"pronouns_enforce_macrons"},
                )
    macrons = st.session_state.pronouns_enforce_macrons
    if macrons:
        st.markdown("A hosszú magánhangzók innen másolhatók:")
        st.code("āēīōū", language=None)

    st.html('<hr style="border-top: 1px dotted; border-bottom: none;">')

    current_exercise_settings = {
        "demonstratives": demonstratives,
        "personal_pron": personal_pron,
        "rel_interr": rel_interr,
        "indefinites": indefinites,
        "gen_forms_diff": gen_forms_diff,
    }
    if st.user.is_logged_in:
        set_defaults_col, clear_defaults_col, link_col = st.container(vertical_alignment="bottom", height="stretch").columns(3, vertical_alignment="center")
        with set_defaults_col:
            st.button("Beállítások mentése",
                        type="primary",
                        width="stretch",
                        help="A jelenlegi névmási beállítások mentése alapértelmezettként (a hosszú magánhangzók ellenőrzésének kivételével).",
                        on_click=save_defaults,
                        args=(page_id, defaults,),
                        kwargs=current_exercise_settings,
                        disabled=preset_active,
                        )
        with clear_defaults_col:
            st.button("Alapbeállítások",
                        type="primary",
                        width="stretch",
                        help="A BevLat általános alapértelmezett névmási beállításainak visszaállítása.",
                        on_click=clear_defaults,
                        args=(page_id,),
                        disabled=preset_active or not defaults
                        )
        with link_col:
            exercise_link_popover(page_id, exercise_schema, current_exercise_settings)
    else:
        exercise_link_popover(page_id, exercise_schema, current_exercise_settings)

pron_list = demonstratives+personal_pron+rel_interr+indefinites

## FILTER PRONOUNS ##

selected_pronouns = {k: v for k, v in pronoun_vocab.items() if k in pron_list} # filter pronouns based on options selected


## LOOKUP TABLES ##

#st.write(selected_pronouns.keys())

abbrevs = {
    "case": {"nom": "nom.", "gen": "gen.", "dat": "dat.", "acc": "acc.", "abl": "abl."},
    "number": {"sg": "sg.", "pl": "pl."},
    "gender": {"m": "m.", "f": "f.", "n": "n."},
}

pronoun_options = {"case": list(abbrevs["case"].keys()),
                "number": list(abbrevs["number"].keys()),
                "gender": list(abbrevs["gender"].keys())}


## ADAPTIVE LEARNING ALGORITHM ##

def gen_question():
    avail_pronouns = list(selected_pronouns.keys())
    if not avail_pronouns:
        return

    dfs = {}
    pronoun = case = number = gender = None
    recent_words = []
    pronoun_qs_answered = [item for item in questions_asked if item["pos"] == "pronoun" and "correct" in item]
    last_q = pronoun_qs_answered[-1] if pronoun_qs_answered else []
    # last_gen_type = ""
    # last_case = last_q.get("id",{}).get("case")
    # if isinstance(last_case, str) and len(last_case.split()) > 1:
    #     last_gen_type = last_case.split()[1][1:-2]

    # st.write(last_q)

    if questions_asked and len(pronoun_qs_answered) > 0:
        pronoun_df = pd.json_normalize(pronoun_qs_answered).replace({None: "-", pd.NA: "-", "nan": "-", "None": "-"})
        #st.write(pronoun_df)
        dfs["pronoun_df"] = pronoun_df
        if len(pronoun_df) > 0:
            pronoun_df_wrong_indiv = pronoun_df.copy().groupby([col for col in pronoun_df.columns if col not in ["pos","answer","correct"]]) \
                .agg(num_correct=("correct","sum"),total_q=("correct","count")) \
                .assign(pct_wrong = lambda df: (df["total_q"]-df["num_correct"])/df["total_q"]) \
                .assign(weight = lambda df: ((df["total_q"]-df["num_correct"])/(df["num_correct"]+1))**0.5) \
                .query("pct_wrong > 0") \
                .query(f"word in @avail_pronouns")
            pronoun_df_wrong_agg = pronoun_df.copy().groupby([col for col in pronoun_df.columns if not (col in ["pos","answer","correct"] or col[:3] == "id.")]) \
                .agg(num_correct=("correct","sum"),total_q=("correct","count")) \
                .assign(pct_wrong = lambda df: (df["total_q"]-df["num_correct"])/df["total_q"]) \
                .assign(weight = lambda df: ((df["total_q"]-df["num_correct"])/(df["num_correct"]+1))**0.5) \
                .query("pct_wrong > 0") \
                .query(f"word in @avail_pronouns")
            if len(pronoun_df_wrong_indiv) > 0:
                dfs["pronoun_df_wrong_indiv"] = pronoun_df_wrong_indiv
                dfs["pronoun_df_wrong_agg"] = pronoun_df_wrong_agg
            # st.write(pronoun_df_wrong_indiv)
            # st.write(pronoun_df_wrong_agg)

        if not pronoun_df.empty:
            recent = min(len(avail_pronouns)-1,3)
            # st.write(pronoun_df.tail(recent))
            recent_words = list(pronoun_df.tail(recent)["word"].values) if recent > 0 else []
            # st.write(recent_words)
    if "pronoun_df_wrong_agg" in dfs and pronoun_df_wrong_agg["weight"].max() >= .58:
        repeat_chance = random.choices(["new","repeat"],[st.session_state["adap_learning_frequency"],1])[0]   # 1 in 3 chance of repeated question
        if repeat_chance == "repeat" and len(pronoun_df) > 5:
            # st.write("repeat!")
            pronoun = pronoun_df_wrong_agg.query("weight >= .58")["weight"].sample(n=1, weights=pronoun_df_wrong_agg.query("weight >= .58")["weight"]).index[0]
            # st.write(pronoun)
            word_weight = pronoun_df_wrong_indiv.xs(pronoun,level="word").query("weight >= .58")["weight"] if not pronoun_df_wrong_indiv.query("weight >= .58").empty else None
            if word_weight is not None and not word_weight.empty:
                pronoun_id = word_weight.sample(n=1, weights=word_weight).index[0]
                # st.write(pronoun_id)
                if pronoun_id is not None:
                    pronoun_id = [item if item != "-" else None for item in pronoun_id]
                    # st.write(pronoun_id)
                    case, number, gender = pronoun_id
                    if len(case.split()) > 1:
                        gen_type = case.split()[1][1:-2]
                        case = case.split()[0]
                        # if gen_type == "part":
                        #     part_gen = True

    if not pronoun or pronoun in recent_words:
        pronoun = random.choice(avail_pronouns)
        case = None
    while not case:
        number = random.choice(pronoun_options["number"]) if pronoun_vocab[pronoun].get("sg") and pronoun_vocab[pronoun].get("pl") else None
        gender = random.choice(pronoun_options["gender"]) if pronoun_vocab[pronoun].get("genders") else None

        # since sē has no nominative, ensure that nominative can't be chosen.
        form = None
        while form is None:
            if number is None or (number == "sg" and gender == "m"): # for personal pronouns, or for the dictionary entry form, reduce likelihood of nominative
                case = random.choices(pronoun_options["case"], [10,90,90,90,90])[0]
            else:
                case = random.choice(pronoun_options["case"])
            if pronoun_vocab[pronoun].get("genders"):
                form = pronoun_vocab[pronoun][number][case]
            else:
                form = pronoun_vocab[pronoun]["forms"][case]
        # st.write(last_q)
        if last_q and pronoun == last_q["word"] and ((case == last_q["id"]["case"] or case == last_q["id"]["case"].split()[0]) and number == last_q["id"]["num"] and gender == last_q["id"]["gender"]):
            # st.write("perfect match: reroll")
            case = None

    return_val = [pronoun, case, number, gender]
        # if part_gen:
        #     return_val += [part_gen]

    choose_genitive(pronoun,case,gen_forms_diff)
    # st.write(st.session_state.part_gen)

    return return_val

def build_pronoun(pronoun_id=None, temp_gen_diff=None):
    if pronoun_id:
        pass
    else:
        pronoun_id = gen_question()

    pronoun, case, number, gender = pronoun_id

    if not pronoun_vocab[pronoun].get("genders"):
        if number is None:
            correct_form = pronoun_vocab[pronoun]["forms"][case]
        else:
            correct_form = pronoun_vocab[pronoun][number][case]
    else:
        correct_num_case = pronoun_vocab[pronoun][number][case]
        # neuter is always the last form in the tuple
        if gender == "n":
            correct_form = correct_num_case[-1]
        # if one- or two-termination, M/F are both the first form
        elif len(correct_num_case) in [1,2]:
            correct_form = correct_num_case[0]
        # otherwise, M is the first form, F is the second form
        else:
            if gender == "m":
                correct_form = correct_num_case[0]
            elif gender == "f":
                correct_form = correct_num_case[1]

    if isinstance(correct_form,dict):
        if st.session_state.part_gen is None or temp_gen_diff is False:
            correct_form = list(correct_form.values())
        else:
            if st.session_state.part_gen:
                correct_form = correct_form["partitive"]
                # st.session_state.gen_string = "gen. (partitivus)"
            else:
                correct_form = correct_form["non_part"]
                # st.session_state.gen_string = "gen. (nem partitivus)"


    return correct_form

## CREATE THE QUIZ ##

st.session_state.gen_func = gen_question

if st.session_state.current_question:
    pronoun, case, number, gender = st.session_state.current_question
    if gen_forms_diff is not None:
        if gen_forms_diff is False:
            temp_gen_diff = False
        else:
            temp_gen_diff = True
    else:
        temp_gen_diff = None
    correct_form = build_pronoun(st.session_state.current_question, temp_gen_diff)
    # st.write(correct_form)
    st.session_state.correct_answer = correct_form


    # if not pronoun_vocab[pronoun].get("genders"):
    #     if number is None:
    #         correct_form = pronoun_vocab[pronoun]["forms"][case]
    #     else:
    #         correct_form = pronoun_vocab[pronoun][number][case]
    # else:
    #     correct_num_case = pronoun_vocab[pronoun][number][case]
    #     # neuter is always the last form in the tuple
    #     if gender == "n":
    #         correct_form = correct_num_case[-1]
    #     # if one- or two-termination, M/F are both the first form
    #     elif len(correct_num_case) in [1,2]:
    #         correct_form = correct_num_case[0]
    #     # otherwise, M is the first form, F is the second form
    #     else:
    #         if gender == "m":
    #             correct_form = correct_num_case[0]
    #         elif gender == "f":
    #             correct_form = correct_num_case[1]


    # if not st.session_state.gen_string:
    #     part_gen = False
    #     if gen_forms_diff:
    #         part_gen = random.choice([True,False])
    # elif "non" in st.session_state.gen_string:
    #     part_gen = False
    # else:
    #     part_gen = True
    # #gen_string = st.session_state.gen_string

    # if gen_forms_diff and pronoun in ["nōs","vōs"] and case == "gen":
    if st.session_state.part_gen is not None:
        if st.session_state.part_gen:
            # correct_form = correct_form["partitive"]
            st.session_state.gen_string = "gen. (partitivus)"
        else:
            # correct_form = correct_form["non_part"]
            st.session_state.gen_string = "gen. (nem partitivus)"


    # if isinstance(correct_form,dict):
    #     if not gen_forms_diff:
    #         correct_form = list(correct_form.values())
    #     else:
    #         if part_gen:
    #             correct_form = correct_form["partitive"]
    #             st.session_state.gen_string = "gen. (partitivus)"
    #         else:
    #             correct_form = correct_form["non_part"]
    #             st.session_state.gen_string = "gen. (nem partitivus)"


    gen_string = st.session_state.gen_string
    # st.write(gen_string)
    # # st.write("correct form:",correct_form)
    # st.session_state.correct_answer = correct_form

    curr_question = {
            "pos": "pronoun",
            "word": pronoun,
            "id": {
                # "case": case + " (part.)" if st.session_state.part_gen and gen_string and gen_forms_diff else case + " (non-part.)" if gen_string and gen_forms_diff else case,
                "case": case,
                "num": number,
                "gender": gender
            },
#            "correct": False
        }

    if st.session_state.append_answer is True:
        questions_asked.append(
            curr_question
        )
        st.session_state.append_answer = False

    if st.session_state.append_answer is False and "answer" not in questions_asked[-1] and questions_asked[-1]["pos"] == "pronoun":
        if questions_asked[-1]["word"] in ["nōs","vōs"] and "gen" in questions_asked[-1]["id"]["case"]:
            if gen_forms_diff:
                # if st.session_state and temp_gen_diff is not False:
                if st.session_state.part_gen:
                    # st.write("setting to partitive genitive")
                    questions_asked[-1]["id"]["case"] = "gen (part.)"
                elif st.session_state.part_gen is False:
                    # st.write("setting to non-partitive")
                    questions_asked[-1]["id"]["case"] = "gen (non-part.)"
            else:
                # st.write("setting to regular genitive")
                questions_asked[-1]["id"]["case"] = "gen"

## CREATE QUESTION PHRASE ##
    form_label = ", ".join(
        item for item in (
            abbrevs["number"].get(number),
            gen_string if gen_string and gen_forms_diff else abbrevs["case"].get(case),
            abbrevs["gender"].get(gender),
        ) if item is not None
    )
    question_html = (
        f'Képezd {hungarian_article(pronoun)} '
        f'<strong><em>{html.escape(pronoun)}</em></strong> névmás következő alakját: '
        f'<strong>{html.escape(form_label)}</strong>!'
    )

## DISPLAY QUESTION ##
    prompt_space = st.container(height=82, border=False)
    with prompt_space:
        st.markdown(
            f'<div style="margin-top:0.75rem;font-size:1.75rem;line-height:1.25;">{question_html}</div>',
            unsafe_allow_html=True,
        )

    with st.form(key="pronoun_form", clear_on_submit=True):
        st.text_input("Válaszod:", key="answer_input")
        st.form_submit_button(
            "Válasz ellenőrzése",
            key="form_submission_button",
            on_click=submit_pronoun_answer,
            disabled=st.session_state.button_disable,
            width="stretch",
        )

    feedback_space = st.container(height=90, border=False)
    with feedback_space:
        st.markdown(st.session_state.answer_display_message)


## GENERATE NEW QUESTIONS AND CHECK ANSWERS ##

if not pron_list:
    st.write("Válassz ki legalább egy névmást a gyakorláshoz.")
else:

    control_row = st.container(height=110, border=False)
    with control_row:
        new_question_col, results_col, score_col = st.columns([1, 1, 1], gap="medium", vertical_alignment="top")

        new_q_button_text = "Új kérdés" if st.session_state.question_list else "Kattints ide az első kérdéshez!"
        new_q_button_type = "secondary" if st.session_state.question_list else "primary"
        with new_question_col:
            st.button(new_q_button_text, on_click=new_question, args=(gen_question,), key="question_button", width="stretch", type=new_q_button_type)

        with results_col:
            st.markdown(st.session_state.result_message)    # just write the result message, rather than other things as well.

            if st.session_state.current_question and st.session_state.answer_checked and "Helytelen" in st.session_state.result_message:
                chart_popover = st.popover("Ragozási táblázat",type="primary")
                with chart_popover:
                    st.caption("Ez a funkció még fejlesztés alatt áll.")
                    st.caption("Az esetek sorrendjét a navigációs menüben állíthatod be.")
                    starting_form = list(st.session_state.current_question)
                    next_form = list(starting_form)

                    pronoun_table = {}
                    table_index = []
                    cs_order = list(st.session_state.case_order)
                    cs_order = [cs for cs in cs_order if cs != "voc"]

                    if "forms" not in pronoun_vocab[pronoun]:
                        for num in ["sg","pl"]:
                            for gd in ["m","f","n"]:
                                pronoun_table[(num,gd)] = []
                    else:
                        pronoun_table[pronoun] = []
                    for cs in cs_order:
                        if cs not in table_index:
                            table_index.append(cs)
                        for item in pronoun_table:
                            if isinstance(item, tuple):
                                num = item[0]
                                gd = item[1]

                                next_form[1] = cs
                                next_form[2] = num
                                next_form[3] = gd

                            else:
                                num = None
                                gd = None

                                next_form[1] = cs

                            try:
                                form = build_pronoun(next_form, temp_gen_diff)
                                if isinstance(form, list):
                                    form = "/".join(form)
                                if next_form == starting_form:
                                    form = f":green-background[{form}]"
                                    if pronoun in ["nōs","vōs"] and starting_form[1] == "gen" and "/" not in form:
                                        form_append = pronoun_vocab[pronoun]["forms"]["gen"]["partitive"] if st.session_state.part_gen is False else pronoun_vocab[pronoun]["forms"]["gen"]["non_part"]
                                        form += f"/{form_append}"
                            except:
                                form = None
                            pronoun_table[item if isinstance(item, tuple) else pronoun].append(form if form is not None else "--")


                    display_table = pd.DataFrame(pronoun_table, table_index)
                    st.table(display_table, hide_header=True if "forms" in pronoun_vocab[pronoun] else False)


        with score_col:
            st.button("Pontszám nullázása", "reset", on_click=reset, width="stretch")
            st.markdown(
                f'<div style="text-align:right;">Jelenlegi pontszám: <strong>{st.session_state.current_score}</strong> / <strong>{st.session_state.total_questions}</strong></div>',
                unsafe_allow_html=True,
            )

if st.session_state.auto_advance_trigger and st.session_state.answer_checked:
    time.sleep(auto_advance_delay())
    new_question(st.session_state.gen_func)
    st.rerun()
