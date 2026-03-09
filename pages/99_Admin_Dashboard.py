import streamlit as st
import pandas as pd
from database import supabase

st.title("Admin Dashboard")


admin_email = "harjeet.singh@chitkara.edu.in"

if st.session_state.user_email != admin_email:
    st.error("You are not authorized to view this page")
    st.stop()

# total logins
login_data = supabase.table("login_logs").select("*").execute()
logins = login_data.data




# Convert to DataFrame
df = pd.DataFrame(logins)

# Convert login_time from UTC → IST
df["login_time"] = pd.to_datetime(df["login_time"])              # parse as datetime
df["login_time"] = df["login_time"].dt.tz_localize("UTC")        # mark as UTC
df["login_time"] = df["login_time"].dt.tz_convert("Asia/Kolkata")# convert to IST

df["login_time"] = df["login_time"].dt.strftime("%d-%m-%Y %H:%M:%S")


st.subheader("Login History")
st.dataframe(df)






# unique users
unique_users = set([x["email"] for x in logins])

col1, col2 = st.columns(2)

col1.metric("Total Logins", len(logins))
col2.metric("Unique Users", len(unique_users))

# st.subheader("Login History")
# st.dataframe(logins)