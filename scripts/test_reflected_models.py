# scripts/test_reflected_models.py
"""
Test that reflected models work correctly.
Uses your existing database.py connection.

Usage:
    python scripts/test_reflected_models.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.database import SessionLocal
from app.models.reflected_models import Base

def test_basic_queries():
    """Test basic database queries using reflected models"""
    
    print("=" * 70)
    print("TESTING REFLECTED MODELS")
    print("=" * 70)
    
    db = SessionLocal()
    try:
        # Try to access BPM_TASK_EVENT
        try:
            BpmTaskEvent = Base.classes.BPM_TASK_EVENT
            count = db.query(BpmTaskEvent).count()
            print(f"\n✅ BPM_TASK_EVENT: {count:,} records")
            
            # Get recent task
            recent = db.query(BpmTaskEvent).order_by(
                BpmTaskEvent.TIME.desc()
            ).first()
            
            if recent:
                print(f"   Most recent task ID: {recent.ID}")
                print(f"   Status: {recent.STATUS}")
                print(f"   Time: {recent.TIME}")
        except Exception as e:
            print(f"⚠️  BPM_TASK_EVENT: {e}")
        
        # Try to access TERP_USER
        try:
            TerpUser = Base.classes.TERP_USER
            user_count = db.query(TerpUser).count()
            print(f"\n✅ TERP_USER: {user_count:,} records")
            
            # Get first user
            user = db.query(TerpUser).first()
            if user:
                print(f"   First user ID: {user.ID}")
                if hasattr(user, 'USERNAME'):
                    print(f"   Username: {user.USERNAME}")
        except Exception as e:
            print(f"⚠️  TERP_USER: {e}")
        
        # Try to access BPM_PROCESS
        try:
            BpmProcess = Base.classes.BPM_PROCESS
            process_count = db.query(BpmProcess).count()
            print(f"\n✅ BPM_PROCESS: {process_count:,} records")
        except Exception as e:
            print(f"⚠️  BPM_PROCESS: {e}")
        
        # Test a join (if relationships work)
        print("\n" + "=" * 70)
        print("TESTING JOINS")
        print("=" * 70)
        
        try:
            BpmTask = Base.classes.BPM_TASK
            BpmTaskEvent = Base.classes.BPM_TASK_EVENT
            
            # Join task events with tasks
            result = db.query(
                BpmTaskEvent.ID,
                BpmTask.TASK_NAME
            ).join(
                BpmTask, BpmTaskEvent.TASK_ID == BpmTask.ID
            ).limit(5).all()
            
            print(f"\n✅ Successfully joined BPM_TASK_EVENT with BPM_TASK")
            print(f"   Found {len(result)} joined records")
            
            for event_id, task_name in result[:3]:
                print(f"   - Event {event_id}: {task_name}")
                
        except Exception as e:
            print(f"⚠️  Join failed: {e}")
        
        # List all available models
        print("\n" + "=" * 70)
        print("AVAILABLE MODELS")
        print("=" * 70)
        
        all_models = [name for name in dir(Base.classes) if not name.startswith('_')]
        print(f"\n📦 Total models available: {len(all_models)}")
        print(f"\nFirst 20 models:")
        for i, model_name in enumerate(sorted(all_models)[:20], 1):
            print(f"   {i:2d}. {model_name}")
        
        if len(all_models) > 20:
            print(f"   ... and {len(all_models) - 20} more")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
    
    print("\n" + "=" * 70)
    print("✅ TESTING COMPLETE")
    print("=" * 70)

def main():
    """Main function"""
    test_basic_queries()

if __name__ == '__main__':
    main()