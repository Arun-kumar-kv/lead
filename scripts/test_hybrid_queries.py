# scripts/test_hybrid_queries.py
"""Test both live and snapshot queries"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.database import SessionLocal
from app.repositories.leads_repo import LeadsRepository

def test_queries():
    db = SessionLocal()
    try:
        repo = LeadsRepository(db)
        
        print("=" * 70)
        print("TESTING LIVE QUERIES")
        print("=" * 70)
        
        # Test live queries
        total = repo.get_total_leads_live()
        print(f"\n✅ Total active leads: {total:,}")
        
        breakdown = repo.get_conversion_breakdown_live()
        print(f"\n✅ Conversion breakdown:")
        for stage, count in breakdown.items():
            print(f"   {stage}: {count}")
        
        ratings = repo.get_leads_by_ratings_live()
        print(f"\n✅ Ratings breakdown:")
        for rating in ratings:
            print(f"   {rating['rating']}: {rating['lead_count']}")
        
        # print("\n" + "=" * 70)
        # print("TESTING SNAPSHOT QUERIES")
        # print("=" * 70)
        
        # # Test snapshot
        # snapshot = repo.get_latest_snapshot()
        # if snapshot:
        #     print(f"\n✅ Latest snapshot date: {snapshot.DATE}")
        #     print(f"   Total leads: {snapshot.TOTAL_LEADS:,}")
        #     print(f"   Conversion rate: {snapshot.CONVERSION_RATE}%")
        #     print(f"   New → Prospect: {snapshot.NEW_LEAD_TO_PROSPECT_RATE}%")
        # else:
        #     print("\n⚠️  No snapshot data yet. Run aggregation first:")
        #     print("   python scripts/run_leads_aggregation.py")
        
        # # Test trend
        # trend = repo.get_conversion_trend_from_snapshot(days=7)
        # print(f"\n✅ Conversion trend (last 7 days): {len(trend)} data points")
        
    finally:
        db.close()

if __name__ == '__main__':
    test_queries()