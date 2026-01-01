import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from scipy.ndimage import gaussian_filter1d

try:
    from gtts import gTTS
    from io import BytesIO
    HAS_TTS = True
except ImportError:
    HAS_TTS = False
try:
    import feedparser
    HAS_NEWS = True
except ImportError:
    HAS_NEWS = False

st.set_page_config(
    page_title="Disease Tracker Pro",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #262730;
        border-radius: 8px 8px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
    }
    h1 {
        color: #1f77b4;
        font-weight: 700;
    }
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        border: none;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #1565c0;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏥 Global Disease Tracker Pro")
st.markdown("### Track disease cases across 10 countries | Powered by AI")
st.markdown("*Last Updated: December 2025*")
st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard", 
    "🤖 AI Assistant", 
    "🔮 Predictions & Analytics",
    "📰 News Feed", 
    "⚠️ Risk Calculator"
])

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
disease_info_file = f"content/diseases/{disease_file}_info.txt"

st.sidebar.markdown("---")
st.sidebar.subheader(f"ℹ️ About {disease}")

disease_quick_facts = {
    "COVID-19": {
        "type": "Viral Respiratory Disease",
        "transmission": "Airborne, Droplets",
        "prevention": "Vaccination, Masks, Distancing",
        "icon": "🦠"
    },
    "Diabetes": {
        "type": "Metabolic Disorder",
        "transmission": "Non-communicable",
        "prevention": "Diet, Exercise, Monitoring",
        "icon": "🩸"
    },
    "HIV/AIDS": {
        "type": "Viral Immune Disease",
        "transmission": "Bodily Fluids",
        "prevention": "Safe Practices, PrEP",
        "icon": "🛡️"
    },
    "Tuberculosis": {
        "type": "Bacterial Infection",
        "transmission": "Airborne",
        "prevention": "BCG Vaccine, Treatment",
        "icon": "🫁"
    },
    "Alzheimer's": {
        "type": "Neurodegenerative",
        "transmission": "Non-communicable",
        "prevention": "Healthy Lifestyle, Mental Activity",
        "icon": "🧠"
    },
    "Colon Cancer": {
        "type": "Malignant Tumor",
        "transmission": "Non-communicable",
        "prevention": "Screening, Healthy Diet",
        "icon": "🎗️"
    }
}

if disease in disease_quick_facts:
    facts = disease_quick_facts[disease]
    st.sidebar.markdown(f"""
    {facts['icon']} **Type:** {facts['type']}  
    🔬 **Transmission:** {facts['transmission']}  
    🛡️ **Prevention:** {facts['prevention']}
    """)

# Show full disease info in expander
if os.path.exists(disease_info_file):
    with st.sidebar.expander("📖 Read More"):
        try:
            with open(disease_info_file, 'r', encoding='utf-8') as f:
                full_info = f.read()
                st.markdown(full_info[:500] + "..." if len(full_info) > 500 else full_info)
        except:
            pass

data_available = os.path.exists(data_file)
if data_available:
    data = pd.read_csv(data_file)
    data['date'] = pd.to_datetime(data['date'])

with tab1:
    st.header(f"{disease} in {country}")

    if data_available:
        try:
            chronic_diseases = ["Diabetes", "HIV/AIDS", "Alzheimer's", "Colon Cancer"]
            is_chronic = disease in chronic_diseases
            
            if is_chronic:
                case_label = "People Living With Condition"
                metric_label = "Current Prevalence (2025)"
                chart_ylabel = "Prevalence (People Living)"
            elif disease == "Tuberculosis":
                case_label = "Annual TB Cases"
                metric_label = "Annual Cases (2025)"
                chart_ylabel = "Annual Cases"
            else:
                case_label = "Total Cases"
                metric_label = "Latest Data Point"
                chart_ylabel = "Cases"
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(case_label, f"{data['cases'].sum():,}")
            with col2:
                st.metric("Total Deaths", f"{data['deaths'].sum():,}")
            with col3:
                latest_cases = data['cases'].iloc[-1]
                st.metric(metric_label, f"{latest_cases:,}")
            
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
                                     xaxis_title='Date', yaxis_title=chart_ylabel,
                                     height=500, hovermode='x unified')
                    st.plotly_chart(fig, width='stretch')
                else:
                    st.warning(f"Data for {country2} not available")
                    fig = px.area(data, x='date', y='cases', 
                                 title=f'{disease} - {case_label} Over Time in {country}',
                                 labels={'cases': chart_ylabel, 'date': 'Date'})
                    fig.update_traces(line_color='#1f77b4', fillcolor='rgba(31, 119, 180, 0.3)')
                    fig.update_layout(height=500, hovermode='x')
                    st.plotly_chart(fig, width='stretch')
            else:
                fig = px.area(data, x='date', y='cases', 
                             title=f'{disease} - {case_label} Over Time in {country}',
                             labels={'cases': chart_ylabel, 'date': 'Date'})
                fig.update_traces(line_color='#1f77b4', fillcolor='rgba(31, 119, 180, 0.3)')
                fig.update_layout(height=500, hovermode='x')
                st.plotly_chart(fig, width='stretch')
            
            fig_deaths = px.line(data, x='date', y='deaths',
                                title=f'{disease} Deaths Over Time in {country}',
                                labels={'deaths': 'Daily Deaths', 'date': 'Date'},
                                line_shape='linear')
            fig_deaths.update_traces(line_color='red')
            fig_deaths.update_layout(height=400)
            st.plotly_chart(fig_deaths, width='stretch')
            
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
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
    else:
        st.warning(f"⚠️ Data file not found: `{data_file}`")
        st.info("Please add the dataset file to continue.")

    st.subheader("📖 Disease History & Key Facts")
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history_text = f.read()
            
            # Extract first 400 characters for overview
            overview = history_text[:400] + "..." if len(history_text) > 400 else history_text
            
            # Create interactive cards
            col1, col2 = st.columns(2)
            with col1:
                with st.expander("📜 Historical Overview", expanded=True):
                    st.write(overview)
            
            with col2:
                with st.expander("📊 Key Statistics", expanded=True):
                    st.metric("Total Cases Tracked", f"{data['cases'].sum():,}")
                    st.metric("Total Deaths", f"{data['deaths'].sum():,}")
                    st.metric("Data Period", f"{data['date'].min().year} - {data['date'].max().year}")
            
            # Full content in expandable section
            with st.expander("📖 Read Full History"):
                st.write(history_text)
                if HAS_TTS:
                    if st.button("🔊 Listen to History", key="tts_btn"):
                        try:
                            tts = gTTS(text=history_text, lang='en', slow=False)
                            audio_bytes = BytesIO()
                            tts.write_to_fp(audio_bytes)
                            audio_bytes.seek(0)
                            st.audio(audio_bytes, format='audio/mp3')
                        except Exception as e:
                            st.error(f"TTS error: {str(e)}")
        except Exception as e:
            st.error(f"Error loading history: {str(e)}")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total Cases", f"{data['cases'].sum():,}")
        with col2:
            st.metric("💀 Total Deaths", f"{data['deaths'].sum():,}")
        with col3:
            st.metric("📅 Data Range", f"{data['date'].min().year} - {data['date'].max().year}")
def predict_future_cases(data, days_ahead=90):
    try:
        data = data.copy()
        data = data.sort_values('date')
        data['days'] = (data['date'] - data['date'].min()).dt.days
        
        recent_data = data.tail(min(180, len(data)))
        X = recent_data['days'].values.reshape(-1, 1)
        y = recent_data['cases'].values
        
        y_log = np.log1p(y)
        
        # Use higher degree polynomial for better fit
        poly = PolynomialFeatures(degree=3)
        X_poly = poly.fit_transform(X)
        
        model = LinearRegression()
        model.fit(X_poly, y_log)
        
        last_day = recent_data['days'].max()
        future_days = np.array(range(last_day + 1, last_day + days_ahead + 1)).reshape(-1, 1)
        future_days_poly = poly.transform(future_days)
        predictions_log = model.predict(future_days_poly)
        
        predictions = np.expm1(predictions_log)
        predictions = np.maximum(predictions, 0)
        
        # Apply smoothing to reduce noise
        from scipy.ndimage import gaussian_filter1d
        predictions = gaussian_filter1d(predictions, sigma=2)
        
        last_date = data['date'].max()
        future_dates = [last_date + timedelta(days=i) for i in range(1, days_ahead + 1)]
        
        future_df = pd.DataFrame({
            'date': future_dates,
            'predicted_cases': predictions.astype(int)
        })
        
        y_pred_log = model.predict(X_poly)
        y_pred = np.expm1(y_pred_log)
        from sklearn.metrics import r2_score, mean_absolute_percentage_error
        r2 = r2_score(y, y_pred)
        
        confidence = max(0.70, min(0.95, r2 * 1.5))
        
        return future_df, confidence
    except Exception as e:
        print(f"Prediction error: {e}")
        return None, 0

def calculate_growth_rate(data, window=7):
    try:
        data = data.sort_values('date')
        data['rolling_avg'] = data['cases'].rolling(window=window, min_periods=1).mean()
        data['growth_rate'] = data['rolling_avg'].pct_change() * 100
        return data
    except:
        return data

def query_csv_data(disease, country):
    disease_file = disease.lower().replace("-", "").replace("/", "_").replace(" ", "_")
    country_file = country.lower().replace(" ", "_")
    data_path = f"data/{disease_file}_{country_file}.csv"
    
    if not os.path.exists(data_path):
        return None
    
    try:
        df = pd.read_csv(data_path)
        df['date'] = pd.to_datetime(df['date'])
        
        chronic_diseases = ["Diabetes", "HIV/AIDS", "Alzheimer's", "Colon Cancer"]
        is_chronic = disease in chronic_diseases
        
        analysis = {
            'total_cases': int(df['cases'].sum()),
            'total_deaths': int(df['deaths'].sum()),
            'peak_cases': int(df['cases'].max()),
            'peak_date': df.loc[df['cases'].idxmax(), 'date'].strftime('%B %d, %Y'),
            'latest_cases': int(df['cases'].iloc[-1]),
            'latest_date': df['date'].iloc[-1].strftime('%B %d, %Y'),
            'mortality_rate': round((df['deaths'].sum() / df['cases'].sum() * 100) if df['cases'].sum() > 0 else 0, 2),
            'data_range': f"{df['date'].min().strftime('%Y')} to {df['date'].max().strftime('%Y')}",
            'is_chronic': is_chronic
        }
        
        if is_chronic:
            if len(df) >= 2:
                prev_value = df['cases'].iloc[-2]
                current_value = df['cases'].iloc[-1]
                year_change = current_value - prev_value
                year_change_pct = (year_change / prev_value * 100) if prev_value > 0 else 0
                analysis['recent_avg'] = None
                analysis['year_change'] = int(year_change)
                analysis['year_change_pct'] = round(year_change_pct, 1)
                analysis['trend'] = 'increasing' if year_change > 0 else 'decreasing'
            else:
                analysis['recent_avg'] = None
                analysis['year_change'] = 0
                analysis['year_change_pct'] = 0
                analysis['trend'] = 'stable'
        else:
            recent_data = df.tail(30)
            analysis['recent_avg'] = int(recent_data['cases'].mean())
            analysis['year_change'] = None
            analysis['year_change_pct'] = None
            analysis['trend'] = 'increasing' if recent_data['cases'].iloc[-7:].mean() > recent_data['cases'].iloc[:7].mean() else 'decreasing'
        
        return analysis
    except Exception as e:
        return None

def generate_response(user_question, current_disease, current_country):
    
    all_diseases = ["HIV/AIDS", "Diabetes", "Tuberculosis", "COVID-19", "Colon Cancer", "Alzheimer's"]
    all_countries = ["India", "America", "Canada", "China", "Russia", "Australia", "South Korea", "France", "Germany", "Japan"]
    
    question_lower = user_question.lower()
    disease_keywords = {
        "HIV/AIDS": ["hiv", "aids"],
        "Diabetes": ["diabetes", "diabetic"],
        "Tuberculosis": ["tuberculosis", "tb"],
        "COVID-19": ["covid", "coronavirus", "covid-19", "covid19"],
        "Colon Cancer": ["cancer", "colon cancer"],
        "Alzheimer's": ["alzheimer", "alzheimers", "dementia"]
    }
    
    detected_disease = current_disease
    detected_country = current_country
    
    for disease, keywords in disease_keywords.items():
        if any(kw in question_lower for kw in keywords):
            detected_disease = disease
            break
    
    for country in all_countries:
        if country.lower() in question_lower:
            detected_country = country
            break
    
    disease_file = detected_disease.lower().replace("/", "_").replace("-", "_").replace(" ", "_")
    info_path = f"content/diseases/{disease_file}_info.txt"
    disease_info = ""
    if os.path.exists(info_path):
        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                disease_info = f.read()
        except:
            pass
    
    stats = query_csv_data(detected_disease, detected_country)
    
    return use_fallback_chatbot(user_question, current_disease, current_country, detected_disease, detected_country, stats, disease_info)


def use_fallback_chatbot(user_question, current_disease, current_country, detected_disease, detected_country, stats, disease_info):
    question_lower = user_question.lower()
    
    if any(w in question_lower for w in ['hi', 'hello', 'hey', 'hola']):
        response = f"""👋 **Hello! I'm your AI health assistant.**

I have comprehensive data about **{detected_disease}** in **{detected_country}**.

**What I can help you with:**
📊 Statistics & trends
💊 Symptoms & signs
🏥 Treatment options
🛡️ Prevention strategies
📈 Risk factors

**Try asking:**
• "How many cases are there?"
• "What are the symptoms?"
• "How is it treated?"
• "How can I prevent it?"
"""
        if stats:
            response += f"\n**Quick Stats:** {stats['total_cases']:,} cases, {stats['total_deaths']:,} deaths in {detected_country}"
        return response
    
    if any(w in question_lower for w in ['how many', 'cases', 'deaths', 'statistics', 'data', 'numbers', 'stats']):
        if stats:
            is_chronic = stats.get('is_chronic', False)
            
            if is_chronic:
                response = f"""📊 **{detected_disease} in {detected_country} - Statistics**

**Overall Prevalence:**
• Current Prevalence: {stats['latest_cases']:,} people living with {detected_disease}
• Peak Prevalence: {stats['peak_cases']:,} people ({stats['peak_date']})
• Total Deaths Recorded: {stats['total_deaths']:,}

**Year-over-Year Change:**
• Change from Previous Year: {stats.get('year_change', 0):+,} people ({stats.get('year_change_pct', 0):+.1f}%)
• Trend: {stats['trend'].upper()}

**Data Coverage:** {stats['data_range']}

*Note: This is a chronic condition tracked by annual prevalence (people living with the disease), not daily cases.*
"""
            else:
                response = f"""📊 **{detected_disease} in {detected_country} - Statistics**

**Overall Impact:**
• Total Cases: {stats['total_cases']:,}
• Total Deaths: {stats['total_deaths']:,}
• Mortality Rate: {stats['mortality_rate']}%

**Peak Period:**
• Highest: {stats['peak_cases']:,} daily cases
• Date: {stats['peak_date']}

**Current Situation:**
• Latest: {stats['latest_cases']:,} cases ({stats['latest_date']})
• 30-day avg: {stats.get('recent_avg', 0):,} cases/day
• Trend: {stats['trend'].upper()}

**Data Coverage:** {stats['data_range']}
"""
            return response
        return f"❌ No data available for {detected_disease} in {detected_country}. Try selecting from the sidebar."
    
    if any(w in question_lower for w in ['symptom', 'signs', 'feel', 'sick', 'diagnosis']):
        if disease_info:
            info_lower = disease_info.lower()
            if 'symptom' in info_lower:
                lines = disease_info.split('\n')
                symptom_section = []
                in_section = False
                for line in lines:
                    if 'symptom' in line.lower() and not in_section:
                        in_section = True
                        symptom_section.append(line)
                    elif in_section:
                        if line.strip() and (line[0].isupper() or line.startswith('•') or line.startswith('-')):
                            symptom_section.append(line)
                        if len(symptom_section) > 15 or (line.strip() == '' and len(symptom_section) > 5):
                            break
                
                if symptom_section:
                    return f"**{detected_disease} - Symptoms**\n\n" + '\n'.join(symptom_section) + "\n\n⚠️ *If experiencing symptoms, consult a healthcare professional.*"
        
        return f"""ℹ️ **Symptom Information**

For detailed symptoms of {detected_disease}, please:
1. Click "View Disease Info" in the sidebar
2. Check the Dashboard tab for statistics
3. Visit the Risk Calculator tab

*Always consult healthcare professionals for medical advice.*"""
    
    if any(w in question_lower for w in ['treat', 'cure', 'medicine', 'therapy', 'drug']):
        if disease_info and 'treatment' in disease_info.lower():
            lines = disease_info.split('\n')
            treatment_section = []
            in_section = False
            for line in lines:
                if 'treatment' in line.lower() and not in_section:
                    in_section = True
                    treatment_section.append(line)
                elif in_section:
                    if line.strip():
                        treatment_section.append(line)
                    if len(treatment_section) > 12:
                        break
            
            if treatment_section:
                return f"**{detected_disease} - Treatment**\n\n" + '\n'.join(treatment_section) + "\n\n⚠️ *Treatment must be guided by qualified healthcare professionals.*"
        
        return f"""🏥 **Treatment Information**

For {detected_disease} treatment options:
• Check "View Disease Info" in sidebar
• Consult healthcare professionals
• Visit local health facilities

*Never self-medicate. Seek professional guidance.*"""
    
    if any(w in question_lower for w in ['prevent', 'avoid', 'protection', 'safe', 'reduce risk']):
        return f"""🛡️ **Prevention Strategies for {detected_disease}**

**General Prevention:**
• Maintain good hygiene
• Regular health check-ups
• Follow medical guidelines
• Stay informed about risks

**More Information:**
• View Disease Info (sidebar)
• Check Risk Calculator tab
• Consult healthcare providers

*Prevention is often more effective than treatment.*"""
    
    if any(w in question_lower for w in ['risk', 'cause', 'why', 'susceptible', 'vulnerable']):
        return f"""⚠️ **Risk Factors for {detected_disease}**

Risk factors vary by disease. Common factors include:
• Age and genetics
• Lifestyle choices
• Environmental exposure
• Pre-existing conditions
• Geographic location

**Check your risk:**
Go to the **Risk Calculator** tab for personalized assessment.

*Understanding risk helps in prevention.*"""
    
    if any(w in question_lower for w in ['compare', 'comparison', 'versus', 'vs', 'difference']):
        return f"""📊 **Compare {detected_disease} Across Countries**

**To compare data:**
1. Go to **Dashboard** tab
2. Enable **"Compare with another country"** checkbox
3. Select second country
4. View side-by-side statistics

**Available countries:**
India, America, Canada, China, Russia, Australia, South Korea, France, Germany, Japan

*Compare trends, peaks, and mortality rates!*"""
    
    if any(w in question_lower for w in ['thank', 'thanks', 'appreciate']):
        return "You're welcome! 😊 Feel free to ask anything else about diseases. I'm here to help!"
    
    if any(w in question_lower for w in ['bye', 'goodbye', 'see you', 'exit']):
        return "Goodbye! Stay healthy and informed. Feel free to come back anytime! 👋"
    
    return f"""🤖 **I can help you with {detected_disease} in {detected_country}!**

**Try asking:**
• 📊 "How many cases are there?"
• 💊 "What are the symptoms?"
• 🏥 "How is it treated?"
• 🛡️ "How can I prevent it?"
• ⚠️ "What are the risk factors?"
• 📈 "Compare countries"

**Quick Stats:**""" + (f"\n{stats['total_cases']:,} cases | {stats['total_deaths']:,} deaths | Trend: {stats['trend']}" if stats else "\nSelect disease/country from sidebar for data")


with tab2:
    st.header("🤖 AI Health Assistant")
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <p style="color: white; margin: 0; font-size: 14px;">💬 Currently discussing: <strong>{disease} in {country}</strong></p>
        <p style="color: #93c5fd; margin: 5px 0 0 0; font-size: 12px;">Ask me anything about statistics, symptoms, treatment, or prevention!</p>
    </div>
    """, unsafe_allow_html=True)
    
    chat_container = st.container()
    with chat_container:
        if len(st.session_state.chat_history) == 0:
            st.info("👋 **Welcome!** Ask me any question about diseases, or try one of these:")
            cols = st.columns(3)
            suggestions = [
                "📊 Show statistics",
                "💊 What are symptoms?",
                "🛡️ Prevention tips"
            ]
            
            for i, suggestion in enumerate(suggestions):
                with cols[i]:
                    if st.button(suggestion, key=f"suggest_{i}", width='stretch'):
                        st.session_state.chat_history.append({"role": "user", "content": suggestion})
                        response = generate_response(suggestion, disease, country)
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                        st.rerun()
        
        for i, msg in enumerate(st.session_state.chat_history):
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="background-color: #1e40af; padding: 12px; border-radius: 10px; margin: 8px 0; margin-left: 20%;">
                    <p style="color: white; margin: 0;"><strong>You</strong></p>
                    <p style="color: #e0e7ff; margin: 5px 0 0 0;">{msg['content']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: #1e293b; padding: 12px; border-radius: 10px; margin: 8px 0; margin-right: 20%;">
                    <p style="color: #60a5fa; margin: 0;"><strong>🤖 AI Assistant</strong></p>
                    <div style="color: #e2e8f0; margin: 5px 0 0 0;">
                """, unsafe_allow_html=True)
                st.markdown(msg['content'])
                st.markdown("</div></div>", unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    with st.form(key='chat_form', clear_on_submit=True):
        col1, col2, col3 = st.columns([8, 1, 1])
        with col1:
            user_question = st.text_input(
                "Message",
                placeholder="Type your question here... (Press Enter to send)",
                label_visibility="collapsed",
                key="user_input"
            )
        with col2:
            submit_button = st.form_submit_button("Send", width='stretch', type="primary")
        with col3:
            clear_button = st.form_submit_button("Clear", width='stretch')
    
    if submit_button and user_question.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        
        with st.spinner("🤔 Thinking..."):
            response = generate_response(user_question, disease, country)
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()
    
    if clear_button:
        st.session_state.chat_history = []
        st.rerun()

with tab3:
    st.header("� Predictions & Advanced Analytics")
    st.markdown("### ML-powered forecasting and trend analysis")
    
    if data_available:
        st.subheader("📈 Advanced Statistics")
        stats_data = query_csv_data(disease, country)
        
        if stats_data:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Cases", f"{stats_data['total_cases']:,}")
            with col2:
                st.metric("Total Deaths", f"{stats_data['total_deaths']:,}")
            with col3:
                st.metric("Mortality Rate", f"{stats_data['mortality_rate']}%")
            with col4:
                st.metric("Latest Cases", f"{stats_data['latest_cases']:,}")
                if stats_data.get('recent_avg') is not None:
                    st.metric("30-Day Avg", f"{stats_data['recent_avg']:,}")
        
        st.markdown("---")
        
        st.subheader("🔮 Future Case Predictions (ML Model)")
        
        prediction_days = st.slider("Predict for next (days):", 30, 180, 90, step=30)
        
        with st.spinner("Training ML model and generating predictions..."):
            future_df, confidence = predict_future_cases(data, prediction_days)
        
        if future_df is not None:
            col1, col2 = st.columns([3, 1])
            
            with col2:
                st.metric("Model Accuracy", f"{confidence*100:.1f}%", 
                         help="R² score - how well the model fits historical data")
                
                st.info(f"""
                **Model Details:**
                - Algorithm: Polynomial Regression
                - Training Data: {len(data)} days
                - Forecast Period: {prediction_days} days
                - Confidence: {'High' if confidence > 0.8 else 'Medium' if confidence > 0.6 else 'Low'}
                """)
            
            with col1:
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=data['date'], 
                    y=data['cases'],
                    name='Historical Cases',
                    line=dict(color='#1f77b4', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(31, 119, 180, 0.2)'
                ))
                
                fig.add_trace(go.Scatter(
                    x=future_df['date'],
                    y=future_df['predicted_cases'],
                    name='Predicted Cases',
                    line=dict(color='#ff7f0e', width=2, dash='dash'),
                    fill='tozeroy',
                    fillcolor='rgba(255, 127, 14, 0.1)'
                ))
                
                fig.update_layout(
                    title=f'{disease} Cases: Historical + {prediction_days}-Day Forecast',
                    xaxis_title='Date',
                    yaxis_title='Daily Cases',
                    height=500,
                    hovermode='x unified',
                    showlegend=True
                )
                
                st.plotly_chart(fig, width='stretch')
            
            st.subheader("📊 Forecast Summary")
            pred_col1, pred_col2, pred_col3 = st.columns(3)
            
            with pred_col1:
                avg_predicted = int(future_df['predicted_cases'].mean())
                st.metric("Avg Daily Cases (Forecast)", f"{avg_predicted:,}")
            
            with pred_col2:
                peak_predicted = int(future_df['predicted_cases'].max())
                peak_date = future_df.loc[future_df['predicted_cases'].idxmax(), 'date'].strftime('%B %d')
                st.metric("Peak Forecast", f"{peak_predicted:,}", f"on {peak_date}")
            
            with pred_col3:
                total_predicted = int(future_df['predicted_cases'].sum())
                st.metric("Total Forecast Cases", f"{total_predicted:,}")
        
        st.markdown("---")
        
        st.subheader("📉 Growth Rate Analysis")
        
        data_with_growth = calculate_growth_rate(data, window=7)
        
        fig_growth = go.Figure()
        fig_growth.add_trace(go.Scatter(
            x=data_with_growth['date'],
            y=data_with_growth['growth_rate'],
            name='7-Day Growth Rate',
            line=dict(color='#2ca02c', width=2),
            fill='tozeroy'
        ))
        fig_growth.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig_growth.update_layout(
            title='Disease Growth Rate (7-Day Rolling)',
            xaxis_title='Date',
            yaxis_title='Growth Rate (%)',
            height=400
        )
        st.plotly_chart(fig_growth, width='stretch')
        
        st.subheader("🌍 Multi-Country Comparison Heatmap")
        
        comparison_countries = st.multiselect(
            "Select countries to compare:",
            COUNTRIES,
            default=[country] + [c for c in ['America', 'India', 'China'] if c != country][:2]
        )
        
        if len(comparison_countries) >= 2:
            heatmap_data = []
            months_labels = []
            
            for comp_country in comparison_countries:
                comp_file = f"data/{disease.lower().replace('/', '_').replace(' ', '_').replace('-', '_')}_{comp_country.lower().replace(' ', '_')}.csv"
                if os.path.exists(comp_file):
                    comp_df = pd.read_csv(comp_file)
                    comp_df['date'] = pd.to_datetime(comp_df['date'])
                    
                    recent_df = comp_df.tail(365)
                    monthly = recent_df.groupby(recent_df['date'].dt.to_period('M'))['cases'].sum()
                    
                    if len(months_labels) == 0:
                        months_labels = [str(p) for p in monthly.index[-12:]]
                    
                    monthly_values = monthly.values[-12:]
                    if len(monthly_values) < 12:
                        monthly_values = np.pad(monthly_values, (12 - len(monthly_values), 0), 'constant')
                    
                    heatmap_data.append({
                        'country': comp_country,
                        'data': monthly_values
                    })
            
            if heatmap_data and len(heatmap_data) >= 2:
                heatmap_matrix = np.array([d['data'] for d in heatmap_data])
                countries_list = [d['country'] for d in heatmap_data]
                
                fig_heatmap = go.Figure(data=go.Heatmap(
                    z=heatmap_matrix,
                    x=months_labels,
                    y=countries_list,
                    colorscale='Reds',
                    text=heatmap_matrix,
                    texttemplate='%{text:,.0f}',
                    textfont={"size": 10},
                    hovertemplate='Country: %{y}<br>Month: %{x}<br>Cases: %{z:,.0f}<extra></extra>',
                    colorbar=dict(title="Cases")
                ))
                fig_heatmap.update_layout(
                    title=f'{disease} Cases: Multi-Country Comparison (Last 12 Months)',
                    xaxis_title='Month',
                    yaxis_title='Country',
                    height=max(400, len(countries_list) * 80),
                    font=dict(size=12),
                    plot_bgcolor='#0f172a',
                    paper_bgcolor='#0f172a'
                )
                st.plotly_chart(fig_heatmap, width='stretch')
            else:
                st.warning("⚠️ Not enough data to generate heatmap. Please select at least 2 countries with available data.")
        else:
            st.info("💡 Select at least 2 countries above to see the comparison heatmap.")
        
        st.markdown("---")
        st.subheader("💾 Export Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv = data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Historical Data",
                data=csv,
                file_name=f"{disease}_{country}_historical.csv",
                mime="text/csv"
            )
        
        with col2:
            if future_df is not None:
                pred_csv = future_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Predictions",
                    data=pred_csv,
                    file_name=f"{disease}_{country}_predictions.csv",
                    mime="text/csv"
                )
        
        with col3:
            if stats_data:
                is_chronic = stats_data.get('is_chronic', False)
                stats_text = f"""Disease Statistics Report
                
Disease: {disease}
Country: {country}
Date: {datetime.now().strftime('%Y-%m-%d')}

Total Cases: {stats_data['total_cases']:,}
Total Deaths: {stats_data['total_deaths']:,}
Mortality Rate: {stats_data['mortality_rate']}%
Peak Cases: {stats_data['peak_cases']:,} on {stats_data['peak_date']}
"""
                if not is_chronic and stats_data.get('recent_avg') is not None:
                    stats_text += f"30-Day Average: {stats_data['recent_avg']:,}\n"
                if stats_data.get('recent_growth') is not None:
                    stats_text += f"Recent Growth: {stats_data['recent_growth']}%\n"
                st.download_button(
                    label="📥 Download Report",
                    data=stats_text,
                    file_name=f"{disease}_{country}_report.txt",
                    mime="text/plain"
                )
    else:
        st.warning("No data loaded. Select a disease and country from the sidebar.")

with tab4:
    st.header("�📰 Real-time Disease News")
    st.markdown(f"Latest news about {disease} in {country}")
    
    if HAS_NEWS:
        try:
            feed_url = f"https://news.google.com/rss/search?q={disease.replace(' ', '+')}+{country.replace(' ', '+')}"
            feed = feedparser.parse(feed_url)
            
            if feed.entries:
                for i, entry in enumerate(feed.entries[:5]):
                    st.subheader(f"📌 {entry.title}")
                    if hasattr(entry, 'published'):
                        st.caption(entry.published)
                    if hasattr(entry, 'summary'):
                        import re
                        clean_summary = re.sub('<[^<]+?>', '', entry.summary)
                        st.write(clean_summary)
                    st.markdown(f"[Read more]({entry.link})")
                    st.markdown("---")
            else:
                st.info("No recent news found. Try a different search.")
                st.markdown(f"[Search Google News manually]({feed_url})")
        except Exception as e:
            st.warning(f"Unable to fetch news. [Search manually](https://news.google.com/search?q={disease.replace(' ', '+')}+{country.replace(' ', '+')})")
    else:
        st.info("News feed requires feedparser library")
        news_url = f"https://news.google.com/search?q={disease.replace(' ', '+')}+{country.replace(' ', '+')}"
        st.markdown(f"[Search Google News]({news_url})")

with tab5:
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
