#dashboard_app.py
import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# Configuration
st.set_page_config(layout="wide")
db_path = os.path.join('output_database', 'output_db.db')
table_name ='combined_gold'
st.title("Rijndam ETL Dashboard")

# colors
SCORE_COLORS = {
    'Weinig beperking': '#4ff00f',
    'Redelijke beperking': '#f8951d',
    'Forse beperking': '#de424d'
}

#load data
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(f"SELECT * FROM {table_name}",conn )
        conn.close()
    except Exception as e:
        st.error(f"Error loading data from database: {e}")
        df = pd.DataFrame()
else:
    st.warning("Database not found. Please run the ETL pipeline first.")
    df =pd.DataFrame()


if not df.empty:
    # filters
    with st.sidebar:
        st.header("Filters")
        tracks = st.multiselect("Select a track", sorted(df['track_name'].dropna().unique()))
        if tracks:
            df = df[df['track_name'].isin(tracks)]

    # columns
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Average PDIscore per track")
        avg_scores = df.groupby("track_name")["PDIscore"].mean().sort_values().reset_index()
        fig = px.bar(avg_scores, x='track_name', y='PDIscore', color='track_name')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)

    with col2:
        st.subheader("Unique respondents per track")
        respondent_counts = df.groupby('track_name')['respondentid'].nunique().sort_values(ascending=False).reset_index()
        fig = px.bar(respondent_counts, x='track_name', y='respondentid', color='track_name')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)

    #Score level distribution
    st.subheader("Distribution of score levels")
    if 'score_level' in df.columns:
        score_counts = df['score_level'].value_counts().reset_index()
        score_counts.columns = ['score_level', 'Count']
        fig = px.pie(score_counts, names='score_level', values='Count',hole=0.4,
                     color='score_level', color_discrete_map=SCORE_COLORS)
        st.plotly_chart(fig)

    # Age categories
    st.subheader("Average PDIscore per age category and track")
    if 'age' in df.columns:
        df['age_category'] = pd.cut(df['age'], bins=[0, 18, 25, 35, 45, 60, 100],
                                    labels=['0-17', '18-25', '26-35', '36-45', '46-60', '60+'])
        age_track = df.groupby(['age_category', 'track_name'])['PDIscore'].mean().reset_index()
        fig= px.bar(age_track, x='age_category', y='PDIscore', color='track_name', barmode='group')
        st.plotly_chart(fig)

    # Time series
    if 'completion_time' in df.columns:
        df['completion_time'] = pd.to_datetime(df['completion_time'], errors='coerce')
        df['month'] = df['completion_time'].dt.to_period('M').astype(str)
        st.subheader( "Monthly PDIscore trend per track")
        trend_df = df.groupby(['month', 'track_name'])['PDIscore'].mean().reset_index()
        fig = px.line(trend_df, x='month', y='PDIscore', color='track_name', markers=True)
        st.plotly_chart(fig)

    # Age vs PDIscore
    if all(col in df.columns for col in ['age', 'PDIscore', 'score_level' ]):
        st.subheader("Age vs. PDIscore")
        fig = px.scatter(df, x='age', y='PDIscore', color='score_level',
                         color_discrete_map=SCORE_COLORS, hover_data=['track_name'])
        st.plotly_chart(fig)

    # Age categories per track
    st.subheader("Age category distribution per track")
    age_dist= df.groupby(['track_name', 'age_category']).size().reset_index(name='Count')
    fig = px.bar(age_dist, x='track_name', y='Count', color='age_category', barmode='stack')
    st.plotly_chart(fig)

else:
    # st.warning("Gold CSV not found. Please run the pipeline first.")
    st.warning("Database or table not found. Please run the ETL pipeline first.")

