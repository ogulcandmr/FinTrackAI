# FinTrack AI - Premium Wealth Intelligence

FinTrack AI is an advanced, high-tech financial terminal built to provide real-time portfolio management, dividend simulations, and AI-driven predictive insights.

## Requirements

Before installing FinTrack AI, ensure your system meets the following exact version requirements.

* **Python:** 3.12.x
* **Streamlit:** 1.43.0
* **Pandas:** 2.2.3
* **Plotly:** 6.0.0
* **yfinance:** 0.2.54
* **Prophet:** 1.3.0
* **TextBlob:** 0.19.0
* **Supabase:** 2.13.0
* **python-dotenv:** 1.2.2
* **requests:** 2.32.3

## Installation

Follow these steps sequentially to set up the project on your local machine.

1. Clone the repository to your local system.
2. Navigate to the project root directory.
3. Create a virtual environment to isolate the exact package versions.
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
4. Install the exact requirements using the provided requirements file.
   ```bash
   pip install -r requirements.txt
   ```
5. Configure your secure credentials. Create a `.streamlit` folder and a `secrets.toml` file inside it.
   ```bash
   mkdir -p .streamlit
   touch .streamlit/secrets.toml
   ```

## Usage

Follow these steps to run and interact with the application.

1. Open the `.streamlit/secrets.toml` file and add your required API keys.
   ```toml
   SUPABASE_URL = "your-supabase-url"
   SUPABASE_KEY = "your-supabase-key"
   NEWS_API_KEY = "optional-news-api-key"
   FINNHUB_API_KEY = "optional-finnhub-key"
   ```
2. Start the Streamlit server from the root directory.
   ```bash
   streamlit run app.py
   ```
3. Open your web browser and navigate to the Local URL provided in the terminal.
4. Register a new user account through the "Register" tab to initialize your database profile.
5. Log in to access the Dashboard, Portfolio Management, Dividend Simulator, and AI Analysis modules.
