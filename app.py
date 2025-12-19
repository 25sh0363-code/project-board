import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

st.set_page_config(
    page_title="Disease Tracker Pro",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏥 Global Disease Tracker Pro")
st.markdown("Track disease cases across countries from 2000 to present | Powered by AI")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "🤖 AI Assistant", "📰 News Feed", "⚠️ Risk Calculator", "🎤 Voice Search"])

st.sidebar.header("Select Parameters")

COUNTRIES = [
    "India", "America", "Canada", "China", "Russia",
    "Australia", "South Korea", "France", "Germany", "Japan"
]

DISEASES = [
    "HIV/AIDS", "Diabetes", "Tuberculosis",
    "COVID-19", "Colon Cancer", "Alzheimer's"
]

country = st.sidebar.selectbox("Select Country", COUNTRIES)
disease = st.sidebar.selectbox("Select Disease", DISEASES)

compare_mode = st.sidebar.checkbox("🔄 Compare with another country")
if compare_mode:
    country2 = st.sidebar.selectbox("Compare with", [c for c in COUNTRIES if c != country])

disease_file = disease.lower().replace("-", "").replace("/", "_").replace(" ", "_")
country_file = country.lower().replace(" ", "_")
data_file = f"data/{disease_file}_{country_file}.csv"
history_file = f"content/history/{disease_file}_{country_file}.txt"

with tab1:
    st.header(f"{disease} in {country}")

    if os.path.exists(data_file):
        try:
            data = pd.read_csv(data_file)
            data['date'] = pd.to_datetime(data['date'])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Cases", f"{data['cases'].sum():,}")
            with col2:
                st.metric("Total Deaths", f"{data['deaths'].sum():,}")
            with col3:
                latest_cases = data['cases'].iloc[-1]
                st.metric("Latest Daily Cases", f"{latest_cases:,}")
            
            st.subheader("📊 Historical Data")
            
            if compare_mode:
                country_file2 = country2.lower().replace(" ", "_")
                data_file2 = f"data/{disease_file}_{country_file2}.csv"
                if os.path.exists(data_file2):
                    data2 = pd.read_csv(data_file2)
                    data2['date'] = pd.to_datetime(data2['date'])
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=data['date'], y=data['cases'], 
                                            mode='lines', name=country,
                                            line=dict(color='blue', width=3)))
                    fig.add_trace(go.Scatter(x=data2['date'], y=data2['cases'], 
                                            mode='lines', name=country2,
                                            line=dict(color='red', width=3)))
                    fig.update_layout(title=f'{disease} Cases Comparison',
                                     xaxis_title='Date', yaxis_title='Cases',
                                     height=500, hovermode='x unified')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"Data for {country2} not available")
                    fig = px.area(data, x='date', y='cases', 
                                 title=f'{disease} Cases Over Time in {country}',
                                 labels={'cases': 'Daily Cases', 'date': 'Date'})
                    fig.update_traces(line_color='#1f77b4', fillcolor='rgba(31, 119, 180, 0.3)')
                    fig.update_layout(height=500, hovermode='x')
                    st.plotly_chart(fig, use_container_width=True)
            else:
                fig = px.area(data, x='date', y='cases', 
                             title=f'{disease} Cases Over Time in {country}',
                             labels={'cases': 'Daily Cases', 'date': 'Date'})
                fig.update_traces(line_color='#1f77b4', fillcolor='rgba(31, 119, 180, 0.3)')
                fig.update_layout(height=500, hovermode='x')
                st.plotly_chart(fig, use_container_width=True)
            
            fig_deaths = px.line(data, x='date', y='deaths',
                                title=f'{disease} Deaths Over Time in {country}',
                                labels={'deaths': 'Daily Deaths', 'date': 'Date'},
                                line_shape='linear')
            fig_deaths.update_traces(line_color='red')
            fig_deaths.update_layout(height=400)
            st.plotly_chart(fig_deaths, use_container_width=True)
            
            st.subheader("🔍 Daily Case Finder")
            selected_date = st.date_input("Select a date to view cases", 
                                          value=data['date'].max(),
                                          min_value=data['date'].min().date(),
                                          max_value=data['date'].max().date())
            
            selected_data = data[data['date'].dt.date == selected_date]
            if not selected_data.empty:
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Cases on {selected_date}:** {selected_data['cases'].values[0]:,}")
                with col2:
                    st.info(f"**Deaths on {selected_date}:** {selected_data['deaths'].values[0]:,}")
            else:
                st.warning("No data available for selected date")
            
            st.subheader("📈 Predictions (Next 30 Days)")
            st.info("Prediction model will be implemented here")
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
    else:
        st.warning(f"⚠️ Data file not found: `{data_file}`")
        st.info("Please add the dataset file to continue.")

    st.subheader("📖 Disease History")
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history_text = f.read()
            st.write(history_text)
        except Exception as e:
            st.error(f"Error loading history: {str(e)}")
    else:
        st.warning(f"⚠️ History file not found: `{history_file}`")
        st.info("History content will be added by research team.")

with tab2:
    st.header("🤖 AI Chatbot Assistant")
    st.markdown("Ask me anything about diseases and countries!")
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    user_question = st.text_input("Ask a question:", placeholder="e.g., How many COVID cases in India in 2023?")
    
    if st.button("Ask") and user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        
        response = f"Based on the data for {disease} in {country}, I can help you with that information. "
        if os.path.exists(data_file):
            try:
                data = pd.read_csv(data_file)
                total_cases = data['cases'].sum()
                response += f"Total cases recorded: {total_cases:,}. "
            except:
                response += "Please check the data file. "
        else:
            response += "Data not available yet. Please add the dataset files."
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**AI:** {msg['content']}")

with tab3:
    st.header("📰 Real-time Disease News")
    st.markdown("Latest news about selected disease")
    
    st.info("News feed feature - requires internet connection and feedparser library")
    st.markdown(f"Search Google News for: [{disease} {country}](https://news.google.com/search?q={disease.replace(' ', '+')}+{country.replace(' ', '+')})")

with tab4:
    st.header("⚠️ Disease Risk Calculator")
    st.markdown(f"Calculate your risk level for {disease}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.slider("Your Age", 0, 100, 30)
        location = st.selectbox("Your Location", COUNTRIES)
        symptoms = st.multiselect("Do you have any symptoms?", 
                                  ["Fever", "Cough", "Fatigue", "Difficulty Breathing", 
                                   "Loss of Taste/Smell", "Body Aches", "None"])
    
    with col2:
        vaccinated = st.radio("Vaccination Status", ["Fully Vaccinated", "Partially Vaccinated", "Not Vaccinated"])
        pre_conditions = st.multiselect("Pre-existing Conditions",
                                       ["Diabetes", "Heart Disease", "Lung Disease", 
                                        "Obesity", "Immunocompromised", "None"])
    
    if st.button("Calculate Risk"):
        risk_score = 10
        
        if age > 60:
            risk_score += 30
        elif age > 40:
            risk_score += 20
        elif age > 20:
            risk_score += 10
        
        risk_score += len(symptoms) * 5
        risk_score += len(pre_conditions) * 10
        
        if vaccinated == "Not Vaccinated":
            risk_score += 25
        elif vaccinated == "Partially Vaccinated":
            risk_score += 15
        
        risk_score = min(risk_score, 100)
        
        st.subheader("Your Risk Assessment")
        
        if risk_score < 30:
            st.success(f"🟢 Low Risk: {risk_score}%")
            st.write("Your risk is relatively low. Continue following basic health guidelines.")
        elif risk_score < 60:
            st.warning(f"🟡 Moderate Risk: {risk_score}%")
            st.write("You have moderate risk. Consider consulting a healthcare provider.")
        else:
            st.error(f"🔴 High Risk: {risk_score}%")
            st.write("You have high risk factors. Please consult a healthcare professional immediately.")
        
        st.progress(risk_score / 100)

with tab5:
    st.header("🎤 Voice Search")
    st.markdown("Voice search feature - requires microphone access and SpeechRecognition library")
    
    st.info("This feature requires additional setup. For now, use the manual search below.")
    
    st.markdown("### Manual Search")
    voice_country = st.selectbox("Select Country", COUNTRIES, key="voice_country")
    voice_disease = st.selectbox("Select Disease", DISEASES, key="voice_disease")
    if st.button("Search"):
        country = voice_country
        disease = voice_disease
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("Disease Information")
disease_info_file = f"content/diseases/{disease_file}_info.txt"
if os.path.exists(disease_info_file):
    try:
        with open(disease_info_file, 'r', encoding='utf-8') as f:
            disease_info = f.read()
        with st.sidebar.expander("View Disease Info"):
            st.write(disease_info)
    except Exception as e:
        st.sidebar.error(f"Error loading disease info: {str(e)}")
else:
    st.sidebar.info("Disease information coming soon")

st.markdown("---")
st.markdown("*Data from 2000 to present | Updated daily | Powered by AI*")
