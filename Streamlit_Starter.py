import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- 1. Title and Description ---
st.title("Crime Analysis for St. Louis (2021-2023)")
st.markdown("""
This web application allows users to explore and visualize crime data for St. Louis from 2021 to 2023.
Use the filters and visualizations to understand trends, seasonality, and patterns in the data.
""")

# --- 2. Load Data ---
@st.cache_data
def load_data(file_path='path/to/2021-2023.csv'):
    crime_data = pd.read_csv(file_path)
    columns_to_drop = ['IncidentNum', 'NIBRS', 'NIBRSCategory', 'SRS_UCR', 'CrimeAgainst', 'FelMisdCit', 'IncidentTopSRS_UCR', 'District', 'Neighborhood', 'NbhdNum', 'Latitude', 'Longitude', 'IncidentSupplemented', 'LastSuppDate', 'VictimNum', 'FirearmUsed', 'IncidentNature']
    crime_data.drop(columns=columns_to_drop, inplace=True)
    crime_data.rename(columns={'IncidentDate': 'Date', 'OccurredFromTime': 'Time', 'Offense': 'CrimeType'}, inplace=True)
    crime_data['Date'] = pd.to_datetime(crime_data['Date'], errors='coerce')
    crime_data = crime_data[(crime_data['Date'].dt.year >= 2021) & (crime_data['Date'].dt.year <= 2023)]
    crime_data.dropna(subset=['Date', 'CrimeType'], inplace=True)
    crime_data['Year'] = crime_data['Date'].dt.year
    crime_data['Month'] = crime_data['Date'].dt.month
    crime_data['Day'] = crime_data['Date'].dt.day
    crime_data['DayOfWeek'] = crime_data['Date'].dt.day_name()
    crime_data['Season'] = crime_data['Month'].apply(lambda x: 'Winter' if x in [12, 1, 2] else 'Spring' if x in [3, 4, 5] else 'Summer' if x in [6, 7, 8] else 'Fall')
    return crime_data

crime_data = load_data()

# --- 3. Sidebar Filters ---
st.sidebar.header("Filter Data")
year_filter = st.sidebar.multiselect("Select Year(s):", options=crime_data['Year'].unique(), default=crime_data['Year'].unique())
season_filter = st.sidebar.multiselect("Select Season(s):", options=crime_data['Season'].unique(), default=crime_data['Season'].unique())

filtered_data = crime_data[(crime_data['Year'].isin(year_filter)) & (crime_data['Season'].isin(season_filter))]

# --- 4. Data Preview ---
st.subheader("Filtered Data Preview")
st.write(filtered_data.head())

# --- 5. Visualizations ---
# 1. Crime Over Time
st.subheader("Crime Over Time (2021-2023)")
crime_by_year = filtered_data.groupby('Year').size()
fig1, ax1 = plt.subplots()
crime_by_year.plot(kind='line', ax=ax1, title='Total Crime by Year')
st.pyplot(fig1)

# 2. Seasonal Crime Analysis
st.subheader("Seasonal Crime Analysis")
seasonal_crime = filtered_data.groupby(['Year', 'Season']).size().unstack()
fig2, ax2 = plt.subplots()
seasonal_crime.plot(kind='bar', stacked=True, ax=ax2, title='Total Crimes by Season')
st.pyplot(fig2)

# 3. Crime Type Analysis
st.subheader("Crime Type Analysis")
crime_type_by_year = filtered_data.groupby(['Year', 'CrimeType']).size().unstack()
fig3, ax3 = plt.subplots()
crime_type_by_year.plot(kind='bar', stacked=True, ax=ax3, title='Crime Types by Year')
st.pyplot(fig3)

# 4. Crime by Time of Day
st.subheader("Crime by Time of Day")
time_of_day_heatmap = filtered_data.pivot_table(index='DayOfWeek', columns='Time', values='CrimeType', aggfunc='count')
fig4, ax4 = plt.subplots()
sns.heatmap(time_of_day_heatmap, cmap='coolwarm', cbar=True, ax=ax4)
st.pyplot(fig4)

# 5. Crime Type Distribution
st.subheader("Crime Type Distribution")
crime_type_distribution = filtered_data['CrimeType'].value_counts()
fig5, ax5 = plt.subplots()
crime_type_distribution.plot(kind='pie', autopct='%1.1f%%', ax=ax5)
st.pyplot(fig5)

# 6. Monthly Crime Trends
st.subheader("Monthly Crime Trends")
monthly_crime_trends = filtered_data.groupby(['Year', 'Month']).size().unstack()
fig6, ax6 = plt.subplots()
monthly_crime_trends.plot(kind='line', ax=ax6, title='Monthly Crime Trends (2021-2023)')
st.pyplot(fig6)

# --- 6. Download Data ---
st.subheader("Download Filtered Data")
csv = filtered_data.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Filtered Data as CSV",
    data=csv,
    file_name='filtered_crime_data.csv',
    mime='text/csv'
)
