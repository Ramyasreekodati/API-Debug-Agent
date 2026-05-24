import streamlit as st

def login():
    """Simple password authentication.
    The password should be stored in Streamlit's Secrets as `APP_PASSWORD`.
    If the user provides the correct password, `st.session_state['auth']` is set to True.
    """
    if st.session_state.get('auth'):
        return  # Already logged in
    st.title('🔐 Authentication')
    pwd = st.text_input('Enter password', type='password')
    if pwd:
        if pwd == st.secrets.get('APP_PASSWORD'):
            st.session_state['auth'] = True
            st.success('✅ Access granted')
            # Rerun to load the rest of the app
            st.experimental_rerun()
        else:
            st.error('❌ Incorrect password')
