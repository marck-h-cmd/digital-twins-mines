import streamlit as st
from utils.translations import get_text, get_current_lang, init_language, TRANSLATIONS

def load_translation(lang_code):
    return TRANSLATIONS.get(lang_code, TRANSLATIONS["es"])

def init_i18n():
    init_language()
    current = get_current_lang()
    st.session_state.t = load_translation(current)

def change_lang(lang_code):
    st.session_state.language = lang_code
    st.session_state.lang = lang_code
    st.session_state.t = load_translation(lang_code)
