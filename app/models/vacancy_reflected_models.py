# app/models/vacancy_reflected_models.py
"""
Auto-reflected models from existing TERP vacancy-related tables
Assumes you have tables like: TERP_UNITS, TERP_PROPERTIES, TERP_TENANTS, etc.
"""

from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData, Table
from app.services.database import engine
from sqlalchemy import inspect
import logging
logger = logging.getLogger(__name__)
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
    TerpPropertyUnits = Base.classes.TERP_LS_PROPERTY_UNIT
    TerpProperty = Base.classes.TERP_LS_PROPERTY
    TerpPropertyUnitStatus = Base.classes.TERP_LS_PROPERTY_UNIT_STATUS
    TerpPropertyUnitType = Base.classes.TERP_LS_PROPERTY_UNIT_TYPE
    # TerpUnitShifting = Base.classes.TERP_LS_UNIT_SHIFTING
    logger.info("✅ Vacancy-related models reflected successfully")

except AttributeError as e:
    logger.error(f"❌ Error reflecting vacancy tables: {e}")
    raise

__all__ = [
    "TerpPropertyUnits",
    "TerpProperty",
    "TerpPropertyUnitStatus",
    "TerpPropertyUnitType",
    # "TerpUnitShifting",
    "metadata",
    "Base"
]