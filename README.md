# Disease Tracker Web Application

A Streamlit web application that tracks and visualizes disease data across 15 countries and 6 diseases from 2000 to present.

## Features

- Historical data visualization for 15 countries and 6 diseases
- Daily case lookup by date
- Predictive analytics for future trends
- Detailed disease history and information
- Interactive charts and graphs

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Add Your Data

Place CSV files in the `data/` folder with naming format:
- `{disease}_{country}.csv`
- Example: `covid19_usa.csv`, `malaria_india.csv`

CSV format:
```csv
date,cases,deaths
2000-01-01,150,5
2000-01-02,175,7
```

### 3. Add Content Files

**History files** in `content/history/`:
- Format: `{disease}_{country}.txt`
- Example: `covid19_usa.txt`
- Length: 200-300 words

**Disease info files** in `content/diseases/`:
- Format: `{disease}_info.txt`
- Example: `covid19_info.txt`
- Length: 300-400 words

## Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Deployment

### Deploy to Streamlit Cloud (Free)

1. Push this repository to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Click "Deploy"

## Project Structure

```
project-board/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── data/                   # CSV datasets (90 files)
├── content/
│   ├── history/           # Disease history texts (90 files)
│   └── diseases/          # Disease info pages (6 files)
└── README.md
```

## Countries

USA, India, Brazil, UK, Germany, South Africa, Japan, Mexico, Australia, Nigeria, Indonesia, France, Kenya, Canada, Spain

## Diseases

COVID-19, Malaria, Tuberculosis, HIV/AIDS, Influenza, Dengue Fever

## Team Roles

- **Developer**: Code the Streamlit app and prediction models
- **Research Associate 1**: Collect 45 datasets and write 45 history articles
- **Research Associate 2**: Collect 45 datasets and write 45 history articles + 6 disease info pages

## Timeline

- **Days 1-2**: Setup & data collection begins
- **Days 3-4**: Data collection continues, charts added
- **Days 5-6**: Content writing, prediction models
- **Days 7-8**: Integration and testing
- **Day 9**: Bug fixes and polishing
- **Day 10**: Deployment

## Data Sources

- Our World in Data (ourworldindata.org)
- WHO (who.int/data)
- COVID-19 Data Repository (github.com/CSSEGISandData/COVID-19)
- Google Dataset Search (datasetsearch.research.google.com)

## License

MIT License
