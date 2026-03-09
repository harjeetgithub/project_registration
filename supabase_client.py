# supabase_client.py
from supabase import create_client, Client
import os
import streamlit as st

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# from supabase import create_client
# import streamlit as st

# SUPABASE_URL = st.secrets["SUPABASE_URL"]
# SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)