import streamlit as st
import plotly.express as px

st.write("Streamlit version:", st.__version__)

df = px.data.iris()
fig = px.scatter(df, x="sepal_width", y="sepal_length")

event = st.plotly_chart(fig, key="iris", on_select="rerun")

st.write("Raw event object:")
st.write(event)
if event and "selection" in event:
    st.write("Selection points:", event.selection.points)
