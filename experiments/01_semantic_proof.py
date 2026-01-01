"""
Phase 1: Semantic Search Proof of Concept

This script tests the core semantic search functionality with Hebrew text:
1. Converts Hebrew text listings to vectors using embedding models
2. Converts search queries to vectors
3. Calculates similarity and finds the best matches
4. Benchmarks performance across 3 different models
"""

import time
from typing import List, Tuple, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Sample apartment listings in Hebrew (representing our DB)
LISTINGS = [
    {
        "id": 1,
        "description": "במיקום מושלם בין כיכר דיזינגוף לחוף פרישמן רחוב קטן ושקט 2 חדרים עם מרפסת 60 מטר סה\"כ שמורה ומקורית לתקופה ארוכה חזיתית ושקטה מיקום פגז"
    },
    {
        "id": 2,
        "description": "דירת 2 חד כ 35 מטר קרקע מתוך 4 קומות דירה שמורה ומתוחזקת היטב יש מקלט בבניין מרוהט חלקי אזור מבוקש, דקה הליכה מקניון רמת אביב 2 דק הליכה לאוניברסיטה"
    },
    {
        "id": 3,
        "description": "דירה ברדינג, רמת אביב, זמינה בסוף ינואר 2026 דירת דופלקס יפהפייה של 130 מר בקומה השנייה (ללא מעלית) 4.5 חדרים כולל ממד קומה תחתונה: - סלון ענק עם מטבח פתוח - חדר רחצה עם שירותים - ממד - משרד או חדר שינה קטן קומה עליונה: - 2 חדרי שינה מרווחים - חדר רחצה עם שירותים - 2 מרפסות, אחת מהן בגודל 30 מר עם נוף ירוק סלון ונוף מרהיבים! אין חניה 14,500 שח *לא ניתן למשא ומתן* "
    },
    {
        "id": 4,
        "description": "דירת 4 חדרים עם שתי מרפסות גדולות כולל מרפסת סוכה 2 חניות ומחסן. ללא ריהוט. ללא תיווך. אפשרות למיידי. טלפון כשר זמין לשיחות בלבד. נא לא לשלוח הודעות"
    },
    {
        "id": 5,
        "description": "דירת גג בת 2.5 חדרים, הממוקמת בקומה השנייה מתוך שתי קומות, הכוללת מרפסת בשטח של 30 מטר רוחב המשקיפה לגן הבוטני של האוניברסיטה. הנכס משופץ וממוקם בשכונת נווה שאנן, בסמוך למוזיאון ישראל ובמרחק הליכה מקמפוס האוניברסיטה בגבעת רם. הדירה אינה מתאימה לשותפים .ללא בעלי חיים."
    }
]

# Test queries
TEST_QUERIES = [
    "אני מחפש דירת 2 חדרים במרכז תל אביב, אזור דיזינגוף",
    "דירה  קטנה לסטודנט בתל אביב",
    "אני מחפש דירה יוקרתית בתל אביב, שתהיה מרוהטת וגדולה",
    "מחפש דירה שתתאים למשפחה דתית",
    "מחפש דירה לזוג באזור ירושלים"
]

# Models to test
# Note: You can change multilingual-e5-base to multilingual-e5-large for better accuracy (slower)
MODELS = [
    {
        "name": "multilingual-e5-base",
        "model_name": "intfloat/multilingual-e5-base",  # Change to "intfloat/multilingual-e5-large" for larger model
        "description": "E5 Base model (multilingual)"
    },
    {
        "name": "paraphrase-multilingual-MiniLM",
        "model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "description": "Paraphrase MiniLM (multilingual)"
    },
    {
        "name": "alephbert",
        "model_name": "imvladikon/sentence-transformers-alephbert",
        "description": "AlephBERT (Hebrew-optimized)"
    }
]


def load_model(model_name: str) -> SentenceTransformer:
    """Load a sentence transformer model."""
    print(f"Loading model: {model_name}...")
    start_time = time.time()
    model = SentenceTransformer(model_name)
    load_time = time.time() - start_time
    print(f"Model loaded in {load_time:.2f} seconds\n")
    return model


def encode_texts(model: SentenceTransformer, texts: List[str]) -> np.ndarray:
    """Convert texts to embeddings."""
    return model.encode(texts, convert_to_numpy=True, show_progress_bar=False)


def calculate_similarities(query_vector: np.ndarray, listing_vectors: np.ndarray) -> np.ndarray:
    """Calculate cosine similarity between query and all listings."""
    # Reshape query vector to 2D if needed
    if query_vector.ndim == 1:
        query_vector = query_vector.reshape(1, -1)
    return cosine_similarity(query_vector, listing_vectors)[0]


def rank_listings(similarities: np.ndarray, listings: List[Dict]) -> List[Tuple[int, float, str]]:
    """Rank listings by similarity score."""
    ranked = [(listings[i]["id"], similarities[i], listings[i]["description"][:50] + "...") 
              for i in range(len(listings))]
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked


def test_model(model_config: Dict, listings: List[Dict], queries: List[str]) -> Dict:
    """Test a single model with all queries."""
    model_name = model_config["model_name"]
    model_display_name = model_config["name"]
    
    print("=" * 80)
    print(f"Testing Model: {model_config['description']}")
    print(f"Model ID: {model_display_name}")
    print("=" * 80)
    
    # Load model
    model = load_model(model_name)
    
    # Extract listing texts
    listing_texts = [listing["description"] for listing in listings]
    
    # Encode all listings (batch encoding)
    print("Encoding listings...")
    encode_start = time.time()
    listing_vectors = encode_texts(model, listing_texts)
    encode_time = time.time() - encode_start
    print(f"Encoded {len(listings)} listings in {encode_time:.3f} seconds")
    print(f"Vector dimension: {listing_vectors.shape[1]}\n")
    
    results = {
        "model_name": model_display_name,
        "model_description": model_config["description"],
        "embedding_dimension": listing_vectors.shape[1],
        "listing_encode_time": encode_time,
        "query_results": []
    }
    
    # Test each query
    for query_idx, query in enumerate(queries, 1):
        print(f"\n--- Query {query_idx}: {query} ---")
        
        # Encode query
        query_start = time.time()
        query_vector = encode_texts(model, [query])[0]
        query_encode_time = time.time() - query_start
        
        # Calculate similarities
        similarity_start = time.time()
        similarities = calculate_similarities(query_vector, listing_vectors)
        similarity_time = time.time() - similarity_start
        
        # Rank results
        ranked = rank_listings(similarities, listings)
        
        print(f"Query encoding time: {query_encode_time*1000:.2f}ms")
        print(f"Similarity calculation time: {similarity_time*1000:.2f}ms")
        print("\nTop 3 Results:")
        for rank, (listing_id, score, description) in enumerate(ranked[:3], 1):
            print(f"  {rank}. Listing {listing_id} (score: {score:.4f}): {description}")
        
        results["query_results"].append({
            "query": query,
            "query_encode_time": query_encode_time,
            "similarity_time": similarity_time,
            "top_result_id": ranked[0][0],
            "top_result_score": ranked[0][1],
            "rankings": ranked
        })
    
    print("\n")
    return results


def print_summary(all_results: List[Dict]):
    """Print a summary comparing all models."""
    print("\n" + "=" * 80)
    print("PERFORMANCE SUMMARY")
    print("=" * 80)
    
    print("\nModel Comparison:")
    print(f"{'Model':<40} {'Embedding Dim':<15} {'Avg Query Time (ms)':<20} {'Listing Encode Time (s)':<25}")
    print("-" * 100)
    
    for result in all_results:
        avg_query_time = np.mean([q["query_encode_time"] for q in result["query_results"]]) * 1000
        print(f"{result['model_description']:<40} "
              f"{result['embedding_dimension']:<15} "
              f"{avg_query_time:<20.2f} "
              f"{result['listing_encode_time']:<25.3f}")
    
    print("\nAccuracy Check (Top Result Scores):")
    print(f"{'Model':<40} {'Query 1':<12} {'Query 2':<12} {'Query 3':<12} {'Query 4':<12} {'Query 5':<12}")
    print("-" * 100)
    
    for result in all_results:
        scores = [q["top_result_score"] for q in result["query_results"]]
        print(f"{result['model_description']:<40} " + 
              " ".join([f"{score:<12.4f}" for score in scores]))


def main():
    """Main function to run the semantic search proof of concept."""
    print("=" * 80)
    print("SEMANTIC SEARCH PROOF OF CONCEPT")
    print("Testing Hebrew Text Embedding and Similarity Search")
    print("=" * 80)
    print(f"\nTesting with {len(LISTINGS)} listings and {len(TEST_QUERIES)} queries")
    print(f"Models to test: {len(MODELS)}\n")
    
    all_results = []
    
    # Test each model
    for model_config in MODELS:
        try:
            results = test_model(model_config, LISTINGS, TEST_QUERIES)
            all_results.append(results)
        except Exception as e:
            print(f"\n❌ Error testing model {model_config['name']}: {str(e)}\n")
            import traceback
            traceback.print_exc()
            continue
    
    # Print summary
    if all_results:
        print_summary(all_results)
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
