import streamlit as st
import pandas as pd
import numpy as np
import base64
import plotly.express as px


st.title('NBA Player Stats & Analytics')

st.markdown("""
This app performs simple webscraping of NBA player stats data!
* **Data source:** [Basketball-reference.com](https://www.basketball-reference.com/).
""")

st.sidebar.header('Filter')
selected_year = st.sidebar.selectbox('Year', list(reversed(range(1950,2024))))

# Web scraping of NBA player stats
@st.cache_data
def load_data(year):
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_totals.html"
    html = pd.read_html(url, header = 0)
    df = html[0]
    raw = df.drop(df[df.Age == 'Age'].index) # Deletes repeating headers in content
    raw = raw.fillna(0)
    playerstats = raw.drop(['Rk'], axis=1)
    return playerstats
playerstats = load_data(selected_year)

# Sidebar - Team selection
sorted_unique_team = sorted(playerstats.Tm.unique())
selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

# Sidebar - Position selection
unique_pos = ['C','PF','SF','PG','SG']
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

# Filtering data
df_selected_team = playerstats[(playerstats.Tm.isin(selected_team)) & (playerstats.Pos.isin(selected_pos))]
# Convert the 'Age' column to float
df_selected_team['Age'] = df_selected_team['Age'].astype(float)
# Convert the fifth column to the end to float
df_selected_team.iloc[:, 4:] = df_selected_team.iloc[:, 4:].astype(float)


st.header('Display Player Stats of Selected Team(s)')
st.write('Data Dimension: ' + str(df_selected_team.shape[0]) + ' rows and ' + str(df_selected_team.shape[1]) + ' columns.')
st.dataframe(df_selected_team)

# Download NBA player stats data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

st.subheader('Top 5 Scorers')
df_grouped = df_selected_team.groupby('Player', as_index=False).sum()
# Sort the grouped DataFrame by PTS in descending order
st.bar_chart(df_selected_team.sort_values(by="PTS",ascending=False).head().set_index('Player')['PTS'])

st.subheader('Top 5 Players Who Played Games')
# Group by player and sum the values, then sort by games played (GS) in descending order
df_top_games = df_selected_team.groupby('Player', as_index=False).sum().sort_values(by='GS', ascending=False)
# Create a pie chart using Plotly Express
fig = px.pie(df_top_games.head(), values='GS', names='Player')
# Display the pie chart using Streamlit
st.plotly_chart(fig)

st.subheader('Top 5 (3-Pointer) Scorers')
df_3p = df_selected_team.groupby('Player', as_index=False).sum()
# Sort the grouped DataFrame by 3P in descending order
st.scatter_chart(df_selected_team.sort_values(by="3P",ascending=False).head().set_index('Player')['3P'])

st.subheader("Points Distribution")
figure = px.histogram(df_selected_team, x='PTS')
# Display the pie chart using Streamlit
st.plotly_chart(figure)


st.subheader("Oldest Vs. Youngest Players")
st.dataframe(df_selected_team.sort_values(by='Age',ascending=False).head())
st.dataframe(df_selected_team.sort_values(by='Age').head())


