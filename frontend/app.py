import streamlit as st

st.title("My First Streamlit App")
st.write("Hello, Streamlit!")

# Add a simple slider widget
number = st.slider("Pick a number", 0, 100, 50)
st.write("Your number is:", number)
