import streamlit as st
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client, ClientOptions
import uuid
import os
import pandas as pd
import json
from utils import send_setting
import jwt
import time
from streamlit_sortables import sort_items

st.set_page_config("BevLat", 
                   menu_items={
                       "About": "A pedagogical morphology tool for Latin students at any level to practice creating correct word forms."
                        },
                    layout="centered",
                    page_icon="bevlat_logo.svg"
                    )

# if st.user.is_logged_in:
#     st.logout()

def refresh_user_token():
    sb_auth_apikey = st.secrets["connections"]["supabase"]["SUPABASE_SECRET_KEY"]
    sb_conn_auth = create_client(sb_url, sb_auth_apikey)
    response = sb_conn_auth.table("active_auth_users").select("id").eq("email", st.user.email).execute()
    if not response.data:
        # print("Rescue failed at sb_conn_auth: User email not found in database table.")
        st.logout()
    st.session_state.user_id = response.data[0]["id"]
    user_id = st.session_state.user_id
    expiry_time = int(time.time()) + 86400
    payload = {
        "role": "authenticated",
        "aud": "authenticated",
        "sub": user_id,
        "exp": expiry_time
    }
    minted_token = jwt.encode(
        payload=payload,
        key=st.secrets["connections"]["supabase"]["SUPABASE_PRIVATE_KEY"],
        algorithm="ES256",
        headers={"kid": st.secrets["connections"]["supabase"]["SUPABASE_PRIVATE_KEY_ID"]}
    )
    st.session_state.user_token_expiry = expiry_time
    options = ClientOptions(headers={"Authorization":f"Bearer {minted_token}"})
    st.session_state.supabase_connection = create_client(sb_url, sb_apikey, options=options)

## SESSION STATE VARIABLES ##
if "curr_page_id" not in st.session_state:
    st.session_state["curr_page_id"] = ""
if "enforce_macrons" not in st.session_state:
    st.session_state["enforce_macrons"] = {"pronouns_enforce_macrons": False,
                                           "verbal_adj_enforce_macrons": False,
                                           "verbs_enforce_macrons": False,
                                           "nouns_enforce_macrons": False,
                                           "adjectives_enforce_macrons": False}
if "current_question" not in st.session_state:
    st.session_state["current_question"] = []
if "correct_answer" not in st.session_state:
    st.session_state["correct_answer"] = ""
if "answer_input" not in st.session_state:
    st.session_state["answer_input"] = ""
if "answer_to_check" not in st.session_state:
    st.session_state["answer_to_check"] = ""
if "current_score" not in st.session_state:
    st.session_state["current_score"] = 0
if "total_questions" not in st.session_state:
    st.session_state["total_questions"] = 0
if "answer_checked" not in st.session_state:
    st.session_state["answer_checked"] = False
if "append_answer" not in st.session_state:
    st.session_state["append_answer"] = True
if "question_generation_error_message" not in st.session_state:
    st.session_state["question_generation_error_message"] = ""
if "answer_phrase" not in st.session_state:
    st.session_state["answer_phrase"] = ""
if "result_message" not in st.session_state:
    st.session_state["result_message"] = ""
if "button_disable" not in st.session_state:
    st.session_state["button_disable"] = False
if "answer_display_message" not in st.session_state:
    st.session_state["answer_display_message"] = ""
if not "irreg_alert_message" in st.session_state:
    st.session_state["irreg_alert_message"] = ""
if "auto_advance" not in st.session_state:
    st.session_state.auto_advance = False
if "auto_advance_trigger" not in st.session_state:
    st.session_state.auto_advance_trigger = False
if "gen_func" not in st.session_state:
    st.session_state.gen_func = ""
if "question_list" not in st.session_state:
    st.session_state["question_list"] = []
if "adap_learning_frequency" not in st.session_state:
    st.session_state["adap_learning_frequency"] = 2
if "cons_u_normalize" not in st.session_state:
    st.session_state["cons_u_normalize"] = False
if "case_drag_widget" not in st.session_state:
    st.session_state["case_drag_widget"] = None
if "case_order" not in st.session_state:
    st.session_state["case_order"] = None
if "gen_string" not in st.session_state:
    st.session_state["gen_string"] = None
if "active_expander" not in st.session_state:
    st.session_state["active_expander"] = ""

## SUPABASE CONNECTION ##
sb_url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
sb_apikey = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_history" not in st.session_state:
    st.session_state.user_history = []
if "user_settings" not in st.session_state:
    st.session_state.user_settings = []
if "default_settings" not in st.session_state:
    st.session_state.default_settings = {}
if "current_user_consent" not in st.session_state:
    st.session_state.current_user_consent = None
if "user_token_expiry" not in st.session_state:
    st.session_state.user_token_expiry = None
if "supabase_connection" not in st.session_state:
    st.session_state["supabase_connection"] = None
    if st.user.is_logged_in is True:
        st.session_state["supabase_connection"] = create_client(sb_url, sb_apikey)
        sb_conn: Client = st.session_state.supabase_connection
        try:
            sb_conn.auth.sign_in_with_id_token(
                {
                    "provider":"google",
                    "token":st.user.tokens.id,
                    "access_token": st.user.tokens.access
                }
            )
            st.session_state.user_id = sb_conn.auth.get_user().user.id
        except:
            try:
                refresh_user_token()
            except:
                st.logout()
        sb_conn: Client = st.session_state.supabase_connection
        answer_history = st.session_state.supabase_connection.table("answer").select("answer").eq("user_id",st.session_state.user_id).eq("deleted",False).execute().data
        if answer_history:
            st.session_state["question_list"] = [answer["answer"] for answer in answer_history]
        curr_consent = sb_conn.table("current_consent").select("*").eq("user_id",st.session_state.user_id).execute().data
        if curr_consent:
            st.session_state.current_user_consent = curr_consent[0]["consent"]
        user_settings = sb_conn.table("user_setting").select("*").eq("user_id",st.session_state.user_id).execute().data
        if user_settings:
            st.session_state.user_settings = (
                pd.DataFrame.from_dict(user_settings)
                    .drop(columns=["user_setting_id","user_id"])
            )
            for idx, row in st.session_state.user_settings.iterrows():
                if row["streamlit_page"] == "latin_morph.py":
                    st.session_state[row["setting_name"]] = row["setting_value"]
                elif "macrons" in row["setting_name"]:
                    st.session_state.enforce_macrons[row["setting_name"]] = row["setting_value"]
            default_dict = st.session_state.default_settings
            for page in list(st.session_state.user_settings.streamlit_page.unique()):
                df = st.session_state.user_settings.query(f"streamlit_page == '{page}'")
                default_dict[page] = dict(zip(df["setting_name"],df["setting_value"]))


if st.session_state.supabase_connection is not None and st.session_state.current_user_consent is None:
    @st.dialog("User Consent",dismissible=False)
    def show_consent_dialog():
        sb_conn: Client = st.session_state.supabase_connection
        st.markdown("""Please indicate if you consent for your answers to be used, in pseudonymized form, 
            as part of a future academic study on the efficacy of BevLat or approaches to Latin pedagogy more generally. 
            You may change your consent at any time. If you do not give consent, 
            you will still have full access to all features of a BevLat account.""")
        st.warning("You *should* only see this screen once; if you see it more than once, please let me know ASAP and I'll investigate the cause.")
        def consent_display(x):
            if x is True:
                return "Yes, I consent."
            if x is False:
                return "No, I do not consent."
        st.radio("Choose one:",[True,False], format_func=consent_display, index=None, key="consent_radio")
        def log_consent():
            st.session_state.current_user_consent = st.session_state.consent_radio            
            insert_dict = {"user_id": st.session_state.user_id, "consent":st.session_state.current_user_consent}
            sb_conn.table("user_consent").insert(insert_dict).execute()
        if st.button("Submit", on_click=log_consent, disabled=True if st.session_state.get("consent_radio") is None else False):
            st.rerun()

    show_consent_dialog()

if st.user.is_logged_in and st.session_state.user_token_expiry is not None and time.time() > st.session_state.user_token_expiry - 60:
    refresh_user_token()

## NAVIGATION MENU SIDE-BAR ##

main_page = st.Page("main_page.py", title="Kezdőlap")
about_page = st.Page("about.py", title="A programról")
faq_page = st.Page("faq.py", title="Gyakori kérdések")
recognize_pos_page = st.Page("recognize_pos.py", title="Szófaj felismerése")
recognize_declension_page = st.Page("recognize_declension.py", title="Declinatio felismerése")
identify_stems_page = st.Page("identify_stems.py", title="Tövek felismerése")
nouns_page = st.Page("nouns.py", title="Főnevek")
verbs_page = st.Page("verbs.py", title="Igék")
pronouns_page = st.Page("pronouns.py", title="Névmások")
adj_page = st.Page("adjectives.py", title="Melléknevek és határozószók")
verbal_adj_page = st.Page("verbal_adj.py", title="Igenevek")
data_page = st.Page("data.py", title="Statisztikáid és adataid")
test_page = st.Page("button_test.py", title="Tesztoldal") if st.context.headers.get("host","").startswith("localhost") else ""
account_page = st.Page("account.py", title=("Felhasználói fiók" if st.user.is_logged_in else "Felhasználói fiók (bejelentkezés)"))
vocab_page = st.Page("vocab_list.py", title="Szójegyzék")

nav_dict = {"**BevLat**": [main_page, account_page, about_page, faq_page], 
                            "Gyakorlás": [
                                recognize_pos_page,
                                recognize_declension_page,
                                identify_stems_page,
                                nouns_page, 
                                verbs_page, 
                                adj_page,
                                verbal_adj_page, 
                                pronouns_page, 
                            ],
                            "Eszközök": [data_page,
                                      vocab_page]
                            } 

if st.context.headers.get("host","").startswith("localhost"):
    nav_dict["Tesztelés"] = [test_page]

st.logo("bevlat_logo.svg", size="large")
choose_page = st.navigation(nav_dict, position="hidden")

st.sidebar.caption(
    "Ez az alkalmazás a Darcy Krasne által fejlesztett [Latin Morph!](https://latin-morph.streamlit.app/) egyedi változata."
)
st.sidebar.markdown("**BevLat**")
st.sidebar.page_link(main_page)
st.sidebar.page_link(account_page)
st.sidebar.page_link(about_page)
st.sidebar.page_link(faq_page)
st.sidebar.markdown("**Gyakorlás**")
st.sidebar.page_link(recognize_pos_page)
st.sidebar.page_link(recognize_declension_page)
st.sidebar.page_link(identify_stems_page)
st.sidebar.page_link(nouns_page)
st.sidebar.page_link(verbs_page)
st.sidebar.page_link(adj_page)
st.sidebar.page_link(verbal_adj_page)
st.sidebar.page_link(pronouns_page)
st.sidebar.markdown("**Eszközök**")
st.sidebar.page_link(data_page)
st.sidebar.page_link(vocab_page)
if st.context.headers.get("host", "").startswith("localhost"):
    st.sidebar.markdown("**Tesztelés**")
    st.sidebar.page_link(test_page)

st.sidebar.select_slider("Automatikus továbblépés a következő kérdésre?", 
                         options=[False, 3] + list(range(5,61)), 
                         format_func=lambda x: "Nem" if x is False else str(x)+" mp", 
                         key="auto_advance", 
                         help="Ha azt szeretnéd, hogy a válaszadás után automatikusan megjelenjen a következő kérdés, és ne kelljen az **Új kérdés** gombra kattintanod, itt állíthatod be, hány másodperc múlva lépjen tovább a program (3–60 másodperc). Hibás vagy részben helyes válasz esetén 5 másodperccel több időt kapsz a válasz áttekintésére. (Az **Új kérdés** gombbal továbbra is bármikor továbbléphetsz vagy átugorhatsz egy kérdést.)",
                         on_change=send_setting,
                         kwargs={"streamlit_page":"latin_morph.py","setting_name":"auto_advance"}
                         )

st.sidebar.divider()

# Consonantal-u and case-order functionality remain available internally for compatibility,
# but the sidebar controls are intentionally hidden in BevLat.
def change_case_order():
    default_case_order = ["nom","voc","acc","gen","dat","abl"]
    if not st.session_state.case_order:
        st.session_state.case_order = default_case_order

change_case_order()

# Stabilize the common quiz rows used by the legacy text-entry exercises.
# This reserves evaluation space and prevents the bottom controls from wrapping
# or shifting when feedback appears.
st.html("""
<style>
div[data-testid="stHorizontalBlock"]:has(.st-key-form_submission_button) {
    min-height: 72px;
    align-items: flex-start !important;
    flex-wrap: nowrap !important;
}

div[data-testid="stHorizontalBlock"]:has(.st-key-question_button),
div[data-testid="stHorizontalBlock"]:has(.st-key-identify_stems_question_button),
div[data-testid="stHorizontalBlock"]:has(.st-key-recognize_pos_question_button),
div[data-testid="stHorizontalBlock"]:has(.st-key-recognize_declension_question_button) {
    min-height: 92px;
    align-items: flex-start !important;
    flex-wrap: nowrap !important;
}

div[data-testid="stForm"]:has(.st-key-answer_input) {
    min-height: 154px;
}
</style>
""")

## PAGE ##
choose_page.run()

## PAGE FOOTER ##

st.markdown(
    body='''<div style="position:relative;height:5em;width:100%;">
        <p style="font-size:smaller;text-align:right;position:absolute;bottom:0;right:-3em;">
            &copy; 2026 (<a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" target="_BLANK">CC BY-NC-SA 4.0</a>)
        </p>
        </div>''',
    width="stretch", unsafe_allow_html=True
    )