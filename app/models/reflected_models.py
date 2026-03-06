from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData, Table
from app.services.database import engine
from sqlalchemy import inspect

metadata = MetaData()
inspector = inspect(engine)

schemas = inspector.get_schema_names()

# Reflect all schemas
for schema in schemas:
    try:
        metadata.reflect(bind=engine, schema=schema)
    except Exception:
        pass

# 🔥 CRITICAL PART: REMOVE ALL FOREIGN KEYS
for table in metadata.tables.values():
    table.foreign_keys.clear()
    table.constraints = {
        c for c in table.constraints
        if c.__class__.__name__ != "ForeignKeyConstraint"
    }

Base = automap_base(metadata=metadata)

# Disable relationship generation completely
def _no_relationship(*args, **kwargs):
    return None

Base.prepare(generate_relationship=_no_relationship)
try:
    TerpLeads = Base.classes.TERP_LEADS
    TerpLeadsConversion = Base.classes.TERP_LEADS_CONVERSION
    TerpLeadsChannel = Base.classes.TERP_LEADS_CHANNEL
    TerpLeadsRatings = Base.classes.TERP_LEADS_RATINGS
    TerpLeadsStatus = Base.classes.TERP_LEADS_STATUS
except AttributeError as e:
    print(f"Note: Some TERP_LEADS tables not found: {e}")