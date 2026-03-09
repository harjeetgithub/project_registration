import streamlit as st
from database import supabase

st.title("Admin Dashboard")


admin_email = "harjeet.singh@chitkara.edu.in"

if st.session_state.user_email != admin_email:
    st.error("You are not authorized to view this page")
    st.stop()
# total logins
login_data = supabase.table("login_logs").select("*").execute()
logins = login_data.data

# unique users
unique_users = set([x["email"] for x in logins])

col1, col2 = st.columns(2)

col1.metric("Total Logins", len(logins))
col2.metric("Unique Users", len(unique_users))

st.subheader("Login History")
st.dataframe(logins)