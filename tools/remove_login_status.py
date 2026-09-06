from pathlib import Path

path = Path(__file__).resolve().parents[1] / "latin_morph.py"
text = path.read_text()
old = '''# if st.context.headers.get("host","").startswith("localhost"):
if "User Account" not in choose_page.title:
    if st.user.is_logged_in:
        email = st.user.email.replace("@","<span>@</span>")
        # st.markdown(f"""
        #         <div><p style="margin-bottom:-.5em;padding-bottom:.5em;font-size:smaller;">
        #         You are logged in as <b>{email}</b>
        #         </p></div>
        #         """, unsafe_allow_html=True)
        
        st.markdown(f"""<small>You are logged in as <b>{email}</b></small>""", 
                    help="Visit the User Account page to see your information or logout.", 
                    unsafe_allow_html=True
                    )
    elif choose_page.title != "User Account":
        # st.html(f"""
        #         <p style="margin-bottom:-1em;font-size:smaller;">
        #         You are currently not logged in.
        #         </p>
        #         """)
        st.markdown("<small>You are currently not logged in.</small>", 
                    unsafe_allow_html=True, 
                    help="Visit the User Account page to log in. The site has full functionality if you are not logged in, but your answer history and settings will not persist across sessions."
                    )

'''
count = text.count(old)
if count != 1:
    raise RuntimeError(f"Expected one login status block, found {count}")
path.write_text(text.replace(old, "", 1))
