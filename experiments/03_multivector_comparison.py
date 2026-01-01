"""
Multivector vs Regular Search Performance Comparison

This experiment compares:
1. Regular Search: Using only description vectors (baseline)
2. Hybrid/Multivector Search: Using both structured + description vectors with MAX_SIM strategy

Tests:
- Search accuracy/relevance
- Performance metrics (encoding time, search time)
- Result ranking differences
"""

import sys
from pathlib import Path

# Add backend to path for imports
backend_dir = Path(__file__).parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import time
from typing import List, Tuple, Dict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Import our services
from app.services.embedding_service import get_embedding_service
from app.utils.structured_text import build_structured_text


# Sample apartment listings with structured data
LISTINGS = [
    {
        "id": 1,
        "description": "במיקום מושלם בין כיכר דיזינגוף לחוף פרישמן רחוב קטן ושקט 2 חדרים עם מרפסת 60 מטר סה\"כ שמורה ומקורית לתקופה ארוכה חזיתית ושקטה מיקום פגז",
        "rooms": 2.0,
        "city": "תל אביב",
        "location": "דיזינגוף",
        "has_parking": False,
        "has_elevator": False,
        "furnished": False,
        "price": None,
    },
    {
        "id": 2,
        "description": "דירת 2 חד כ 35 מטר קרקע מתוך 4 קומות דירה שמורה ומתוחזקת היטב יש מקלט בבניין מרוהט חלקי אזור מבוקש, דקה הליכה מקניון רמת אביב 2 דק הליכה לאוניברסיטה",
        "rooms": 2.0,
        "city": "תל אביב",
        "location": "רמת אביב",
        "has_parking": False,
        "has_elevator": False,
        "furnished": True,
        "price": None,
    },
    {
        "id": 3,
        "description": "דירה ברדינג, רמת אביב, זמינה בסוף ינואר 2026 דירת דופלקס יפהפייה של 130 מר בקומה השנייה (ללא מעלית) 4.5 חדרים כולל ממד קומה תחתונה: - סלון ענק עם מטבח פתוח - חדר רחצה עם שירותים - ממד - משרד או חדר שינה קטן קומה עליונה: - 2 חדרי שינה מרווחים - חדר רחצה עם שירותים - 2 מרפסות, אחת מהן בגודל 30 מר עם נוף ירוק סלון ונוף מרהיבים! אין חניה 14,500 שח *לא ניתן למשא ומתן*",
        "rooms": 4.5,
        "city": "תל אביב",
        "location": "רמת אביב",
        "has_parking": False,
        "has_elevator": False,
        "furnished": False,
        "price": 14500,
    },
    {
        "id": 4,
        "description": "דירת 4 חדרים עם שתי מרפסות גדולות כולל מרפסת סוכה 2 חניות ומחסן. ללא ריהוט. ללא תיווך. אפשרות למיידי. טלפון כשר זמין לשיחות בלבד. נא לא לשלוח הודעות",
        "rooms": 4.0,
        "city": "תל אביב",
        "location": None,
        "has_parking": True,
        "has_elevator": False,
        "furnished": False,
        "price": None,
    },
    {
        "id": 5,
        "description": "דירת גג בת 2.5 חדרים, הממוקמת בקומה השנייה מתוך שתי קומות, הכוללת מרפסת בשטח של 30 מטר רוחב המשקיפה לגן הבוטני של האוניברסיטה. הנכס משופץ וממוקם בשכונת נווה שאנן, בסמוך למוזיאון ישראל ובמרחק הליכה מקמפוס האוניברסיטה בגבעת רם. הדירה אינה מתאימה לשותפים. ללא בעלי חיים.",
        "rooms": 2.5,
        "city": "ירושלים",
        "location": "נווה שאנן",
        "has_parking": False,
        "has_elevator": False,
        "furnished": False,
        "price": None,
    },
    {
        "id": 6,
        "description": "דירת 3 חדרים מרווחת במרכז תל אביב עם מעלית, חניה פרטית ומחסן. הדירה משופצת ומרוהטת, קרובה לכל השירותים. זמינה מיידית.",
        "rooms": 3.0,
        "city": "תל אביב",
        "location": "מרכז",
        "has_parking": True,
        "has_elevator": True,
        "has_storage": True,
        "furnished": True,
        "price": 12000,
    },
    {
        "id": 7,
        "description": "סטודיו קטן וחמים בפלורנטין, אזור תוסס עם הרבה מסעדות ובתי קפה. מתאים לסטודנט או זוג צעיר. ללא חניה.",
        "rooms": 1.0,
        "city": "תל אביב",
        "location": "פלורנטין",
        "has_parking": False,
        "has_elevator": False,
        "furnished": False,
        "price": 4500,
    },
    {
        "id": 8,
        "description": "דירת 2 חדרים שקטה בקומה גבוהה עם נוף ים, מעלית וחניה. מרוהטת חלקית. מתאימה לזוג. אזור יוקרתי.",
        "rooms": 2.0,
        "city": "תל אביב",
        "location": "צפון",
        "has_parking": True,
        "has_elevator": True,
        "furnished": True,
        "price": 15000,
    },
]

# Test queries that should benefit from structured search
TEST_QUERIES = [
    {
        "query": "אני מחפש דירת 2 חדרים במרכז תל אביב, אזור דיזינגוף",
        "expected_structured_match": True,  # Should match structured fields
        "expected_ids": [1],  # Expected top result IDs
    },
    {
        "query": "דירה קטנה לסטודנט בתל אביב עד 5000 ש״ח",
        "expected_structured_match": True,
        "expected_ids": [7],  # Studio, Tel Aviv, cheap
    },
    {
        "query": "דירה יוקרתית בתל אביב עם חניה ומעלית, מרוהטת",
        "expected_structured_match": True,
        "expected_ids": [6, 8],  # Luxury with parking, elevator, furnished
    },
    {
        "query": "מחפש דירה 4 חדרים גדולה בתל אביב",
        "expected_structured_match": True,
        "expected_ids": [3, 4],  # 4+ rooms in Tel Aviv
    },
    {
        "query": "דירה ירושלים קרוב לאוניברסיטה",
        "expected_structured_match": True,
        "expected_ids": [5],  # Jerusalem, near university
    },
]


class MockListing:
    """Mock Listing object for testing."""
    def __init__(self, data: Dict):
        self.id = data["id"]
        self.description = data["description"]
        self.rooms = data.get("rooms")
        self.city = data.get("city")
        self.location = data.get("location")
        self.neighborhood = data.get("location")
        self.has_parking = data.get("has_parking", False)
        self.has_elevator = data.get("has_elevator", False)
        self.has_balcony = data.get("has_balcony", False)
        self.has_storage = data.get("has_storage", False)
        self.furnished = data.get("furnished", False)
        self.price = data.get("price")
        self.size_sqm = data.get("size_sqm")
        self.floor = data.get("floor")
        self.total_floors = data.get("total_floors")


def regular_search(
    query_vector: np.ndarray,
    description_vectors: np.ndarray,
    listings: List[Dict],
) -> List[Tuple[int, float]]:
    """
    Regular search using only description vectors.
    
    Returns ranked list of (listing_id, similarity_score).
    """
    similarities = cosine_similarity(
        query_vector.reshape(1, -1),
        description_vectors
    )[0]
    
    ranked = [
        (listings[i]["id"], float(similarities[i]))
        for i in range(len(listings))
    ]
    ranked.sort(key=lambda x: x[1], reverse=True)
    
    return ranked


def multivector_search(
    query_vector: np.ndarray,
    structured_vectors: np.ndarray,
    description_vectors: np.ndarray,
    listings: List[Dict],
) -> List[Tuple[int, float]]:
    """
    Multivector search using both structured and description vectors.
    
    Uses MAX_SIM strategy: takes maximum similarity from both vectors.
    Returns ranked list of (listing_id, similarity_score).
    """
    # Calculate similarities for structured vectors
    structured_similarities = cosine_similarity(
        query_vector.reshape(1, -1),
        structured_vectors
    )[0]
    
    # Calculate similarities for description vectors
    description_similarities = cosine_similarity(
        query_vector.reshape(1, -1),
        description_vectors
    )[0]
    
    # MAX_SIM: take maximum of both similarities
    max_similarities = np.maximum(structured_similarities, description_similarities)
    
    ranked = [
        (listings[i]["id"], float(max_similarities[i]))
        for i in range(len(listings))
    ]
    ranked.sort(key=lambda x: x[1], reverse=True)
    
    return ranked


def compare_search_results(
    regular_ranked: List[Tuple[int, float]],
    multivector_ranked: List[Tuple[int, float]],
    top_k: int = 5,
) -> Dict:
    """Compare search results between regular and multivector approaches."""
    regular_top = [item[0] for item in regular_ranked[:top_k]]
    multivector_top = [item[0] for item in multivector_ranked[:top_k]]
    
    # Calculate overlap
    overlap = set(regular_top) & set(multivector_top)
    overlap_count = len(overlap)
    overlap_ratio = overlap_count / top_k
    
    # Check if top result changed
    top_changed = regular_ranked[0][0] != multivector_ranked[0][0]
    
    return {
        "regular_top_ids": regular_top,
        "multivector_top_ids": multivector_top,
        "overlap_count": overlap_count,
        "overlap_ratio": overlap_ratio,
        "top_changed": top_changed,
        "regular_top_score": regular_ranked[0][1],
        "multivector_top_score": multivector_ranked[0][1],
        "score_improvement": multivector_ranked[0][1] - regular_ranked[0][1],
    }


def run_experiment():
    """Run the multivector comparison experiment."""
    print("=" * 80)
    print("MULTIVECTOR vs REGULAR SEARCH COMPARISON")
    print("=" * 80)
    print(f"\nTesting with {len(LISTINGS)} listings and {len(TEST_QUERIES)} queries\n")
    
    # Initialize embedding service
    print("Loading embedding service...")
    embedding_service = get_embedding_service()
    print(f"Model: {embedding_service.get_model_info()['model_name']}")
    print(f"Vector size: {embedding_service.get_vector_size()}\n")
    
    # Convert listings to mock objects
    mock_listings = [MockListing(listing) for listing in LISTINGS]
    
    # Generate structured texts and encode listings
    print("Encoding listings...")
    encode_start = time.time()
    
    structured_texts = [build_structured_text(listing) for listing in mock_listings]
    descriptions = [listing.description for listing in mock_listings]
    
    # Encode structured texts
    structured_vectors = embedding_service.encode_batch(structured_texts, show_progress=True)
    
    # Encode descriptions
    description_vectors = embedding_service.encode_batch(descriptions, show_progress=True)
    
    encode_time = time.time() - encode_start
    print(f"Encoded {len(LISTINGS)} listings in {encode_time:.3f} seconds\n")
    
    # Store results
    all_results = []
    
    # Test each query
    for query_idx, query_data in enumerate(TEST_QUERIES, 1):
        query = query_data["query"]
        print("=" * 80)
        print(f"Query {query_idx}: {query}")
        print("=" * 80)
        
        # Encode query
        query_start = time.time()
        query_vector = embedding_service.encode(query)
        query_encode_time = time.time() - query_start
        
        # Regular search
        regular_start = time.time()
        regular_ranked = regular_search(query_vector, description_vectors, LISTINGS)
        regular_time = time.time() - regular_start
        
        # Multivector search
        multivector_start = time.time()
        multivector_ranked = multivector_search(
            query_vector, structured_vectors, description_vectors, LISTINGS
        )
        multivector_time = time.time() - multivector_start
        
        # Compare results
        comparison = compare_search_results(regular_ranked, multivector_ranked)
        
        # Print results
        print(f"\nQuery encoding time: {query_encode_time*1000:.2f}ms")
        print(f"Regular search time: {regular_time*1000:.2f}ms")
        print(f"Multivector search time: {multivector_time*1000:.2f}ms")
        
        print(f"\n📊 Regular Search (Top 3):")
        for rank, (listing_id, score) in enumerate(regular_ranked[:3], 1):
            listing = next(l for l in LISTINGS if l["id"] == listing_id)
            desc_preview = listing["description"][:60] + "..."
            print(f"  {rank}. ID {listing_id} (score: {score:.4f}): {desc_preview}")
        
        print(f"\n🔀 Multivector Search (Top 3):")
        for rank, (listing_id, score) in enumerate(multivector_ranked[:3], 1):
            listing = next(l for l in LISTINGS if l["id"] == listing_id)
            desc_preview = listing["description"][:60] + "..."
            print(f"  {rank}. ID {listing_id} (score: {score:.4f}): {desc_preview}")
        
        print(f"\n📈 Comparison:")
        print(f"  Overlap in top 5: {comparison['overlap_count']}/5 ({comparison['overlap_ratio']*100:.1f}%)")
        print(f"  Top result changed: {'Yes' if comparison['top_changed'] else 'No'}")
        print(f"  Score improvement: {comparison['score_improvement']:+.4f}")
        
        if comparison['top_changed']:
            print(f"  ⚠️  Top result changed from ID {regular_ranked[0][0]} to ID {multivector_ranked[0][0]}")
        
        # Check if multivector found expected results
        if query_data.get("expected_ids"):
            expected = set(query_data["expected_ids"])
            multivector_top_3_ids = {item[0] for item in multivector_ranked[:3]}
            regular_top_3_ids = {item[0] for item in regular_ranked[:3]}
            
            multivector_found = bool(expected & multivector_top_3_ids)
            regular_found = bool(expected & regular_top_3_ids)
            
            print(f"\n✅ Expected results check:")
            print(f"  Regular search found expected: {'Yes' if regular_found else 'No'}")
            print(f"  Multivector search found expected: {'Yes' if multivector_found else 'No'}")
            if multivector_found and not regular_found:
                print(f"  🎯 Multivector found expected results that regular search missed!")
            elif regular_found and not multivector_found:
                print(f"  ⚠️  Regular search found expected results that multivector missed")
        
        all_results.append({
            "query": query,
            "query_encode_time": query_encode_time,
            "regular_time": regular_time,
            "multivector_time": multivector_time,
            "comparison": comparison,
        })
        
        print("\n")
    
    # Print summary
    print_summary(all_results, encode_time)
    
    print("\n" + "=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)


def print_summary(all_results: List[Dict], encode_time: float):
    """Print summary statistics."""
    print("\n" + "=" * 80)
    print("PERFORMANCE SUMMARY")
    print("=" * 80)
    
    # Average times
    avg_query_encode = np.mean([r["query_encode_time"] for r in all_results]) * 1000
    avg_regular_time = np.mean([r["regular_time"] for r in all_results]) * 1000
    avg_multivector_time = np.mean([r["multivector_time"] for r in all_results]) * 1000
    
    print(f"\n⏱️  Timing Statistics:")
    print(f"  Listing encoding time: {encode_time:.3f}s")
    print(f"  Avg query encoding time: {avg_query_encode:.2f}ms")
    print(f"  Avg regular search time: {avg_regular_time:.2f}ms")
    print(f"  Avg multivector search time: {avg_multivector_time:.2f}ms")
    print(f"  Multivector overhead: {(avg_multivector_time - avg_regular_time):.2f}ms ({(avg_multivector_time/avg_regular_time - 1)*100:.1f}% slower)")
    
    # Comparison statistics
    top_changed_count = sum(1 for r in all_results if r["comparison"]["top_changed"])
    avg_overlap = np.mean([r["comparison"]["overlap_ratio"] for r in all_results])
    avg_score_improvement = np.mean([r["comparison"]["score_improvement"] for r in all_results])
    
    print(f"\n📊 Result Comparison:")
    print(f"  Queries where top result changed: {top_changed_count}/{len(all_results)}")
    print(f"  Average overlap in top 5: {avg_overlap*100:.1f}%")
    print(f"  Average score improvement: {avg_score_improvement:+.4f}")
    
    # Performance impact
    print(f"\n💡 Insights:")
    if avg_score_improvement > 0:
        print(f"  ✓ Multivector search improves relevance scores on average")
    else:
        print(f"  ⚠️  Multivector search shows lower scores (may need tuning)")
    
    if top_changed_count > len(all_results) / 2:
        print(f"  ✓ Multivector significantly changes ranking (may improve relevance)")
    else:
        print(f"  → Multivector has moderate impact on ranking")
    
    overhead_pct = (avg_multivector_time / avg_regular_time - 1) * 100
    if overhead_pct < 20:
        print(f"  ✓ Multivector overhead is minimal ({overhead_pct:.1f}%)")
    else:
        print(f"  ⚠️  Multivector has noticeable overhead ({overhead_pct:.1f}%)")


if __name__ == "__main__":
    run_experiment()

