from pathlib import Path

# Global left padding
path = Path('streamlit_app.py')
text = path.read_text()
old = '''            .block-container {
                max-width: 1300px !important;
                padding-top: 2rem !important;
                margin-top: 0 !important;
                margin-left: 0 !important;
                margin-right: auto !important;
            }
'''
new = '''            .block-container {
                max-width: 1300px !important;
                padding-top: 2rem !important;
                padding-left: 40px !important;
                margin-top: 0 !important;
                margin-left: 0 !important;
                margin-right: auto !important;
            }
'''
if text.count(old) != 1:
    raise SystemExit(f'Expected one block-container rule, found {text.count(old)}')
text = text.replace(old, new)
compile(text, 'streamlit_app.py', 'exec')
path.write_text(text)

# Footer alignment: stop pushing it 3em beyond the page edge.
path = Path('latin_morph.py')
text = path.read_text()
old = 'font-size:smaller;text-align:right;position:absolute;bottom:0;right:-3em;'
new = 'font-size:smaller;text-align:right;position:absolute;bottom:0;right:0;'
if text.count(old) != 1:
    raise SystemExit(f'Expected one footer positioning rule, found {text.count(old)}')
text = text.replace(old, new)
compile(text, 'latin_morph.py', 'exec')
path.write_text(text)
