"""
Mock scraper for testing ETL pipeline.
Returns sample Hebrew apartment listings.
"""

from typing import List, Dict, Any
from datetime import datetime


def get_mock_listings() -> List[Dict[str, Any]]:
    """
    Get mock apartment listings for testing.
    
    Returns:
        List of listing dictionaries
    """
    return [
        {
            "external_id": "yad2_mock_001",
            "title": "דירה יפה במרכז תל אביב",
            "description": "במיקום מושלם בין כיכר דיזינגוף לחוף פרישמן רחוב קטן ושקט 2 חדרים עם מרפסת 60 מטר סה\"כ שמורה ומקורית לתקופה ארוכה חזיתית ושקטה מיקום פגז",
            "price": 8000,
            "rooms": 2.0,
            "size_sqm": 60,
            "city": "תל אביב",
            "location": "דיזינגוף",
            "neighborhood": "דיזינגוף",
            "floor": 3,
            "total_floors": 5,
            "has_parking": False,
            "has_elevator": False,
            "has_balcony": True,
            "has_storage": False,
            "furnished": False,
            "pets_allowed": None,
        },
        {
            "external_id": "yad2_mock_002",
            "title": "דירה שמורה ברמת אביב",
            "description": "דירת 2 חד כ 35 מטר קרקע מתוך 4 קומות דירה שמורה ומתוחזקת היטב יש מקלט בבניין מרוהט חלקי אזור מבוקש, דקה הליכה מקניון רמת אביב 2 דק הליכה לאוניברסיטה",
            "price": 6500,
            "rooms": 2.0,
            "size_sqm": 35,
            "city": "תל אביב",
            "location": "רמת אביב",
            "neighborhood": "רמת אביב",
            "floor": 0,
            "total_floors": 4,
            "has_parking": False,
            "has_elevator": False,
            "has_balcony": False,
            "has_storage": True,
            "furnished": True,
            "pets_allowed": True,
        },
        {
            "external_id": "yad2_mock_003",
            "title": "דופלקס יוקרתי ברמת אביב",
            "description": "דירה ברדינג, רמת אביב, זמינה בסוף ינואר 2026 דירת דופלקס יפהפייה של 130 מר בקומה השנייה (ללא מעלית) 4.5 חדרים כולל ממד קומה תחתונה: - סלון ענק עם מטבח פתוח - חדר רחצה עם שירותים - ממד - משרד או חדר שינה קטן קומה עליונה: - 2 חדרי שינה מרווחים - חדר רחצה עם שירותים - 2 מרפסות, אחת מהן בגודל 30 מר עם נוף ירוק סלון ונוף מרהיבים! אין חניה 14,500 שח *לא ניתן למשא ומתן*",
            "price": 14500,
            "rooms": 4.5,
            "size_sqm": 130,
            "city": "תל אביב",
            "location": "רמת אביב",
            "neighborhood": "רמת אביב",
            "floor": 2,
            "total_floors": 3,
            "has_parking": False,
            "has_elevator": False,
            "has_balcony": True,
            "has_storage": False,
            "furnished": False,
            "pets_allowed": None,
        },
        {
            "external_id": "yad2_mock_004",
            "title": "דירה גדולה עם חניה",
            "description": "דירת 4 חדרים עם שתי מרפסות גדולות כולל מרפסת סוכה 2 חניות ומחסן. ללא ריהוט. ללא תיווך. אפשרות למיידי. טלפון כשר זמין לשיחות בלבד. נא לא לשלוח הודעות",
            "price": 12000,
            "rooms": 4.0,
            "size_sqm": 110,
            "city": "תל אביב",
            "location": None,
            "neighborhood": None,
            "floor": 2,
            "total_floors": 6,
            "has_parking": True,
            "has_elevator": True,
            "has_balcony": True,
            "has_storage": True,
            "furnished": False,
            "pets_allowed": False,
        },
        {
            "external_id": "yad2_mock_005",
            "title": "דירת גג בירושלים",
            "description": "דירת גג בת 2.5 חדרים, הממוקמת בקומה השנייה מתוך שתי קומות, הכוללת מרפסת בשטח של 30 מטר רוחב המשקיפה לגן הבוטני של האוניברסיטה. הנכס משופץ וממוקם בשכונת נווה שאנן, בסמוך למוזיאון ישראל ובמרחק הליכה מקמפוס האוניברסיטה בגבעת רם. הדירה אינה מתאימה לשותפים. ללא בעלי חיים.",
            "price": 5500,
            "rooms": 2.5,
            "size_sqm": 75,
            "city": "ירושלים",
            "location": "נווה שאנן",
            "neighborhood": "נווה שאנן",
            "floor": 2,
            "total_floors": 2,
            "has_parking": False,
            "has_elevator": False,
            "has_balcony": True,
            "has_storage": False,
            "furnished": False,
            "pets_allowed": False,
        },
    ]


def scrape_listings() -> List[Dict[str, Any]]:
    """
    Scrape listings - wrapper function for consistency.
    
    Returns:
        List of listing dictionaries
    """
    return get_mock_listings()

