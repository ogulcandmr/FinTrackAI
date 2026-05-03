# FinTrack AI - A+ Luxury Financial Suite

## Vision
FinTrack AI is not just an asset tracker—it is a high-end finance terminal that supports investor decisions with modern tooling.

---

## Module 1: Ultra-Luxury Foundation
This module defines the product identity and technical skeleton.

### Design standards
- **Standalone experience:** Streamlit chrome is hidden for a clean web-app feel.
- **Micro-animations:** Eased transitions on forms and buttons.
- **Unified auth:** Login and registration on one animated card.
- **Outfit typography:** Premium, readable type.

### Stack
- **Backend:** Python + Streamlit (custom CSS).
- **Auth:** Supabase real-time auth.
- **Navigation:** Custom sidebar (no auto multi-page).

### Setup
```bash
pip install streamlit supabase yfinance ccxt prophet plotly textblob
streamlit run app.py
```
