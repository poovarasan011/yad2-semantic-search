"""
Streamlit UI for Yad2 Semantic Search Engine
Simple interface for searching apartment listings using natural language.
"""

import streamlit as st
import requests
from typing import Optional, Dict, Any
import os


# Page configuration
st.set_page_config(
    page_title="Yad2 Semantic Search",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_V1_PREFIX = "/api/v1"
SEARCH_ENDPOINT = f"{API_BASE_URL}{API_V1_PREFIX}/search"


def format_price(price: Optional[int]) -> str:
    """Format price for display."""
    if price is None:
        return "לא צוין"
    return f"₪{price:,}"


def format_rooms(rooms: Optional[float]) -> str:
    """Format rooms for display."""
    if rooms is None:
        return "לא צוין"
    if rooms == int(rooms):
        return f"{int(rooms)}"
    return f"{rooms}"


def format_boolean(value: Optional[bool]) -> str:
    """Format boolean for display."""
    if value is None:
        return "לא צוין"
    return "כן" if value else "לא"


def search_listings(
    query: str,
    limit: int = 10,
    filters: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Call the search API endpoint.
    
    Args:
        query: Search query text
        limit: Maximum number of results
        filters: Optional filter dictionary
        
    Returns:
        API response dictionary or None if error
    """
    try:
        params = {"query": query, "limit": limit}
        if filters:
            params.update({k: v for k, v in filters.items() if v is not None})
        
        response = requests.get(SEARCH_ENDPOINT, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"שגיאה בחיפוש: {str(e)}")
        return None


def display_listing(result: Dict[str, Any], index: int):
    """Display a single listing result."""
    listing = result["listing"]
    score = result["score"]
    rank = result["rank"]
    
    # Create expandable card for each listing
    with st.expander(
        f"#{rank} - {listing.get('title', 'ללא כותרת')} | דמיון: {score:.2%}",
        expanded=(index == 0)
    ):
        # Main details in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("מחיר", format_price(listing.get("price")))
        
        with col2:
            st.metric("חדרים", format_rooms(listing.get("rooms")))
        
        with col3:
            size = listing.get("size_sqm")
            if size:
                st.metric("גודל", f"{size} מ²")
            else:
                st.metric("גודל", "לא צוין")
        
        with col4:
            st.metric("דמיון", f"{score:.1%}")
        
        # Location info
        location_parts = []
        if listing.get("city"):
            location_parts.append(listing["city"])
        if listing.get("location"):
            location_parts.append(listing["location"])
        if listing.get("neighborhood"):
            location_parts.append(listing["neighborhood"])
        
        if location_parts:
            st.write(f"**מיקום:** {', '.join(location_parts)}")
        
        # Floor info
        floor_info = []
        if listing.get("floor") is not None:
            floor_info.append(f"קומה {listing['floor']}")
        if listing.get("total_floors") is not None:
            floor_info.append(f"מתוך {listing['total_floors']} קומות")
        if floor_info:
            st.write(f"**קומה:** {', '.join(floor_info)}")
        
        # Features
        features = []
        if listing.get("has_parking"):
            features.append("🚗 חניה")
        if listing.get("has_elevator"):
            features.append("🛗 מעלית")
        if listing.get("has_balcony"):
            features.append("🌳 מרפסת")
        if listing.get("has_storage"):
            features.append("📦 מחסן")
        if listing.get("furnished"):
            features.append("🛋️ מרוהט")
        if listing.get("pets_allowed") is True:
            features.append("🐾 חיות מחמד")
        
        if features:
            st.write(f"**תכונות:** {' | '.join(features)}")
        
        # Description
        if listing.get("description"):
            st.divider()
            st.write("**תיאור:**")
            st.write(listing["description"])


# Main UI
def main():
    # Header
    st.title("🏠 Yad2 Semantic Search")
    st.markdown("חפש דירות באמצעות שפה טבעית בעברית")
    st.markdown("---")
    
    # Sidebar for filters
    with st.sidebar:
        st.header("🔍 פילטרים")
        
        # Price filters
        st.subheader("מחיר")
        price_min = st.number_input(
            "מחיר מינימום (₪)",
            min_value=0,
            value=None,
            step=500,
            format="%d",
        )
        price_max = st.number_input(
            "מחיר מקסימום (₪)",
            min_value=0,
            value=None,
            step=500,
            format="%d",
        )
        
        # Rooms filters
        st.subheader("חדרים")
        rooms_min = st.number_input(
            "מינימום חדרים",
            min_value=0.0,
            value=None,
            step=0.5,
            format="%.1f",
        )
        rooms_max = st.number_input(
            "מקסימום חדרים",
            min_value=0.0,
            value=None,
            step=0.5,
            format="%.1f",
        )
        
        # Location filters
        st.subheader("מיקום")
        city = st.text_input("עיר")
        location = st.text_input("אזור/שכונה")
        
        # Feature filters
        st.subheader("תכונות")
        has_parking = st.selectbox(
            "חניה",
            options=[None, True, False],
            format_func=lambda x: "כל התשובות" if x is None else ("כן" if x else "לא"),
        )
        has_elevator = st.selectbox(
            "מעלית",
            options=[None, True, False],
            format_func=lambda x: "כל התשובות" if x is None else ("כן" if x else "לא"),
        )
        furnished = st.selectbox(
            "מרוהט",
            options=[None, True, False],
            format_func=lambda x: "כל התשובות" if x is None else ("כן" if x else "לא"),
        )
        
        # Results limit
        st.subheader("הגדרות")
        limit = st.slider(
            "מספר תוצאות",
            min_value=1,
            max_value=50,
            value=10,
        )
    
    # Main search interface
    st.header("חיפוש")
    
    # Search query input
    query = st.text_input(
        "מה אתה מחפש?",
        placeholder="לדוגמה: דירה 2 חדרים במרכז תל אביב עם חניה",
        key="search_query",
    )
    
    # Search button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        search_button = st.button("🔍 חפש", type="primary", use_container_width=True)
    
    # Perform search
    if search_button or st.session_state.get("auto_search", False):
        if not query or len(query.strip()) < 1:
            st.warning("אנא הזן שאילתת חיפוש")
        else:
            # Build filters
            filters = {
                "price_min": price_min if price_min and price_min > 0 else None,
                "price_max": price_max if price_max and price_max > 0 else None,
                "rooms_min": rooms_min if rooms_min and rooms_min > 0 else None,
                "rooms_max": rooms_max if rooms_max and rooms_max > 0 else None,
                "city": city.strip() if city else None,
                "location": location.strip() if location else None,
                "has_parking": has_parking,
                "has_elevator": has_elevator,
                "furnished": furnished,
            }
            
            # Remove None values
            filters = {k: v for k, v in filters.items() if v is not None}
            
            # Show loading spinner
            with st.spinner("מחפש..."):
                results = search_listings(query, limit=limit, filters=filters)
            
            # Display results
            if results:
                total_results = results.get("total_results", 0)
                result_list = results.get("results", [])
                
                if total_results > 0:
                    st.success(f"נמצאו {total_results} תוצאות")
                    st.markdown("---")
                    
                    # Display each result
                    for idx, result in enumerate(result_list):
                        display_listing(result, idx)
                        if idx < len(result_list) - 1:
                            st.markdown("---")
                else:
                    st.info("לא נמצאו תוצאות. נסה לשנות את החיפוש או את הפילטרים.")
    
    # Footer/info
    st.markdown("---")
    with st.expander("ℹ️ מידע על החיפוש"):
        st.markdown("""
        **איך זה עובד?**
        
        מערכת החיפוש הסמנטי מבוססת על בינה מלאכותית שמבינה את הכוונה מאחורי החיפוש שלך.
        במקום לחפש רק לפי מילות מפתח, המערכת מבינה את המשמעות וההקשר של השאילתה שלך.
        
        **דוגמאות לחיפושים:**
        - "דירה קטנה לסטודנט בתל אביב"
        - "דירה יוקרתית עם נוף לים"
        - "דירת 3 חדרים עם חניה במרכז"
        - "דירה מרוהטת לזוג צעיר"
        """)
    
    # Connection status
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            status_emoji = "✅" if health_data.get("status") == "healthy" else "⚠️"
            st.sidebar.markdown(f"**סטטוס API:** {status_emoji}")
            st.sidebar.markdown(f"PostgreSQL: {health_data.get('postgresql', 'unknown')}")
            st.sidebar.markdown(f"Qdrant: {health_data.get('qdrant', 'unknown')}")
    except:
        st.sidebar.error("⚠️ API לא נגיש")


if __name__ == "__main__":
    main()

