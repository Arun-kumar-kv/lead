"""
Utility script to inspect reflected models from your database.
Uses your existing database.py connection.

Usage:
    python scripts/generate_models_from_db.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.database import engine
from sqlalchemy import MetaData, inspect

def inspect_database():
    """Inspect database and show all tables"""
    
    print("=" * 70)
    print("DATABASE INSPECTION")
    print("=" * 70)
    
    # Get inspector
    inspector = inspect(engine)
    
    # Get all table names
    tables = inspector.get_table_names()
    
    print(f"\n✅ Connected to database successfully!")
    print(f"📊 Found {len(tables)} tables\n")
    
    # Show tables with their columns
    print("=" * 70)
    print("TABLES AND COLUMNS")
    print("=" * 70)
    
    for table_name in sorted(tables)[:10]:  # Show first 10 as example
        print(f"\n📋 {table_name}")
        columns = inspector.get_columns(table_name)
        
        for col in columns[:5]:  # Show first 5 columns
            col_type = str(col['type'])
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            print(f"   - {col['name']:<30} {col_type:<20} {nullable}")
        
        if len(columns) > 5:
            print(f"   ... and {len(columns) - 5} more columns")
    
    if len(tables) > 10:
        print(f"\n... and {len(tables) - 10} more tables")
    
    # Show foreign keys for some tables
    print("\n" + "=" * 70)
    print("FOREIGN KEY RELATIONSHIPS")
    print("=" * 70)
    
    for table_name in sorted(tables)[:5]:
        fks = inspector.get_foreign_keys(table_name)
        if fks:
            print(f"\n📋 {table_name}")
            for fk in fks:
                print(f"   - {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")

def test_reflection():
    """Test that models can be reflected and used"""
    
    print("\n" + "=" * 70)
    print("TESTING MODEL REFLECTION")
    print("=" * 70)
    
    try:
        from app.models.reflected_models import Base, metadata
        
        print(f"\n✅ Successfully reflected {len(metadata.tables)} tables")
        
        # List available model classes
        print(f"\n📦 Available model classes:")
        
        model_names = [name for name in dir(Base.classes) if not name.startswith('_')]
        
        for i, name in enumerate(sorted(model_names)[:20], 1):
            print(f"   {i:2d}. {name}")
        
        if len(model_names) > 20:
            print(f"   ... and {len(model_names) - 20} more models")
        
        print(f"\n💡 Usage example:")
        print(f"   from app.models.reflected_models import BpmTaskEvent")
        print(f"   tasks = db.query(BpmTaskEvent).all()")
        
    except Exception as e:
        print(f" Error during reflection: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    
    print("\n" + "=" * 70)
    print("DATABASE MODEL GENERATOR")
    print("Inspecting your existing database using app/database.py")
    print("=" * 70)
    
    try:
        # Inspect database structure
        inspect_database()
        
        # Test model reflection
        test_reflection()
        
        print("\n" + "=" * 70)
        print("✅ INSPECTION COMPLETE")
        print("=" * 70)
        print("\n📝 Next steps:")
        print("   1. Import models: from app.models.reflected_models import Base")
        print("   2. Use any table as: Base.classes.TABLE_NAME")
        print("   3. Common models already exported (BpmTaskEvent, TerpUser, etc.)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()