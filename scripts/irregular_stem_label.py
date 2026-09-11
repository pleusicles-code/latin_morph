from pathlib import Path

path = Path('verbs.py')
text = path.read_text()
old = '''            if stems:
                stems_html = ", ".join(f"<em>{html.escape(stem)}-</em>" for stem in stems)
                st.markdown(
                    f'<div style="font-size:1.05rem;line-height:1.35;margin-top:0.35rem;">A tövek: {stems_html}.</div>',
                    unsafe_allow_html=True,
                )
'''
new = '''            if stems:
                stems_html = ", ".join(f"<em>{html.escape(stem)}-</em>" for stem in stems)
                is_irregular = bool(
                    complete_verb_vocab[verb].get("irreg", {}).get("irreg")
                )
                if is_irregular:
                    stem_label = "Szabályos tő:" if len(stems) == 1 else "Szabályos tövek:"
                else:
                    stem_label = "A tövek:"
                st.markdown(
                    f'<div style="font-size:1.05rem;line-height:1.35;margin-top:0.35rem;">{stem_label} {stems_html}.</div>',
                    unsafe_allow_html=True,
                )
'''
if text.count(old) != 1:
    raise SystemExit(f'Expected stem display block once, found {text.count(old)}')
text = text.replace(old, new)
compile(text, 'verbs.py', 'exec')
path.write_text(text)
