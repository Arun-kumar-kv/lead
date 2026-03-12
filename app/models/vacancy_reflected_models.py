# # app/models/vacancy_reflected_models.py
# """
# Auto-reflected models from existing TERP vacancy-related tables
# Assumes you have tables like: TERP_UNITS, TERP_PROPERTIES, TERP_TENANTS, etc.
# """
# from sqlalchemy.ext.automap import automap_base
# from sqlalchemy import MetaData, Table
# from app.services.database import engine
# from sqlalchemy import inspect
# import logging
# logger = logging.getLogger(__name__)
# metadata = MetaData()
# inspector = inspect(engine)

# schemas = inspector.get_schema_names()

# # Reflect all schemas
# for schema in schemas:
#     try:
#         metadata.reflect(bind=engine, schema=schema)
#     except Exception:
#         pass

# # CRITICAL PART: REMOVE ALL FOREIGN KEYS
# for table in metadata.tables.values():
#     table.foreign_keys.clear()
#     table.constraints = {
#         c for c in table.constraints
#         if c.__class__.__name__ != "ForeignKeyConstraint"
#     }

# Base = automap_base(metadata=metadata)

# # Disable relationship generation completely
# def _no_relationship(*args, **kwargs):
#     return None
# Base.prepare(generate_relationship=_no_relationship)
# try:
#     TerpPropertyUnits = Base.classes.TERP_LS_PROPERTY_UNIT
#     TerpProperty = Base.classes.TERP_LS_PROPERTY
#     TerpPropertyUnitStatus = Base.classes.TERP_LS_PROPERTY_UNIT_STATUS
#     TerpPropertyUnitType = Base.classes.TERP_LS_PROPERTY_UNIT_TYPE
#     # TerpUnitShifting = Base.classes.TERP_LS_UNIT_SHIFTING
#     logger.info("Vacancy-related models reflected successfully")

# except AttributeError as e:
#     logger.error(f"Error reflecting vacancy tables: {e}")
#     raise

# __all__ = [
#     "TerpPropertyUnits",
#     "TerpProperty",
#     "TerpPropertyUnitStatus",
#     "TerpPropertyUnitType",
#     # "TerpUnitShifting",
#     "metadata",
#     "Base"
# ]
# app/models/vacancy_reflected_models.py
"""
Auto-reflected models from existing eq_ls vacancy-related tables
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
        metadata.reflect(bind=engine, schema=schema, resolve_fks=False)
    except Exception:
        pass

# CRITICAL: Remove all foreign keys to avoid automap errors
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


def _get_class(table_name: str):
    """Finds automap class handling schema-prefixed keys like 'public.eq_ls_property'."""
    if table_name in Base.classes:
        return Base.classes[table_name]
    for key in metadata.tables:
        if key == table_name or key.endswith(f".{table_name}"):
            plain = key.split(".")[-1]
            if plain in Base.classes:
                return Base.classes[plain]
    raise AttributeError(f"Table '{table_name}' not found in reflected metadata")


try:
    EqLsPropertyUnit       = _get_class("eq_ls_property_unit")
    EqLsProperty           = _get_class("eq_ls_property")
    EqLsPropertyUnitStatus = _get_class("eq_ls_property_unit_status")
    EqLsPropertyUnitType   = _get_class("eq_ls_property_unit_type")
    logger.info("Vacancy-related models reflected successfully")

except AttributeError as e:
    logger.error(f"Error reflecting vacancy tables: {e}")
    raise

__all__ = [
    "EqLsPropertyUnit",
    "EqLsProperty",
    "EqLsPropertyUnitStatus",
    "EqLsPropertyUnitType",
    "metadata",
    "Base",
]