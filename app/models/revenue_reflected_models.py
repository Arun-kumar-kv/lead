# app/models/revenue_reflected_models.py
"""
Auto-reflected models for Revenue & Rent tables.
TERP_LS_CONTRACT_CHARGES_VIEW is a DB view with no PK —
reflected via Table() and mapped imperatively with an explicit
primary_key declaration.
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

# ── Reflect all regular tables ───────────────────────────────────────────────
for schema in schemas:
    try:
        metadata.reflect(bind=engine, schema=schema)
    except Exception:
        pass


# ── Helper: reflect view and mark a PK column ────────────────────────────────
def _reflect_view(schema=None):
    kwargs = dict(autoload_with=engine, extend_existing=True)
    if schema is not None:
        kwargs["schema"] = schema
    tbl = Table("TERP_LS_CONTRACT_CHARGES_VIEW", metadata, **kwargs)
    # Views have no PK — mark CONTRACT_ID (or first col) so the mapper works
    if "CONTRACT_ID" in tbl.c:
        tbl.c.CONTRACT_ID.primary_key = True
    else:
        first_col = list(tbl.c)[0]
        first_col.primary_key = True
        logger.warning(
            f"CONTRACT_ID not found in view — using '{first_col.name}' as surrogate PK"
        )
    return tbl


# Try default schema first, then each named schema
_view_table = None

try:
    _view_table = _reflect_view()
    logger.info("Reflected TERP_LS_CONTRACT_CHARGES_VIEW (default schema)")
except Exception as e:
    logger.warning(f"Default schema view reflection failed: {e}")

if _view_table is None:
    for schema in schemas:
        try:
            _view_table = _reflect_view(schema=schema)
            logger.info(f"Reflected TERP_LS_CONTRACT_CHARGES_VIEW under schema '{schema}'")
            break
        except Exception:
            continue

if _view_table is None:
    raise RuntimeError(
        "Could not reflect TERP_LS_CONTRACT_CHARGES_VIEW from any schema. "
        "Verify the view exists and the DB user has SELECT privilege on it."
    )

# ── Remove all foreign keys (same pattern as all other model files) ──────────
for table in metadata.tables.values():
    table.foreign_keys.clear()
    table.constraints = {
        c for c in table.constraints
        if c.__class__.__name__ != "ForeignKeyConstraint"
    }

# ── Automap all regular tables ───────────────────────────────────────────────
Base = automap_base(metadata=metadata)


def _no_relationship(*args, **kwargs):
    return None


Base.prepare(generate_relationship=_no_relationship)


# ── Named model classes ──────────────────────────────────────────────────────

# Contracts
try:
    TerpContract     = Base.classes.TERP_LS_CONTRACT
    TerpPaymentTerms = Base.classes.TERP_LS_PAYMENT_TERMS
except AttributeError as e:
    logger.error(f"Contract model not found: {e}")
    raise

# View — try Base.classes first; fall back to imperative mapping
try:
    TerpContractChargesView = Base.classes.TERP_LS_CONTRACT_CHARGES_VIEW
    logger.info("TerpContractChargesView loaded via Base.classes")
except AttributeError:
    # automap still skipped it — map imperatively
    # Find the table in metadata using explicit string key lookup (no bool checks)
    _tbl_key = "TERP_LS_CONTRACT_CHARGES_VIEW"
    _found_tbl = None

    # Check plain key first
    if _tbl_key in metadata.tables:
        _found_tbl = metadata.tables[_tbl_key]
    else:
        # Search schema-qualified keys
        for key in metadata.tables.keys():
            if key.upper().endswith("TERP_LS_CONTRACT_CHARGES_VIEW"):
                _found_tbl = metadata.tables[key]
                break

    if _found_tbl is None:
        raise AttributeError(
            "TERP_LS_CONTRACT_CHARGES_VIEW not found in metadata after reflection."
        )

    # Determine PK column for imperative mapping
    if "CONTRACT_ID" in _found_tbl.c:
        _pk_cols = [_found_tbl.c.CONTRACT_ID]
    else:
        _pk_cols = [list(_found_tbl.c)[0]]

    from sqlalchemy.orm import registry as _registry

    class TerpContractChargesView:
        pass

    _reg = _registry()
    _reg.map_imperatively(
        TerpContractChargesView,
        _found_tbl,
        primary_key=_pk_cols,
    )
    logger.info("TerpContractChargesView mapped imperatively")

# Property & Units
try:
    TerpProperty         = Base.classes.TERP_LS_PROPERTY
    TerpPropertyUnit     = Base.classes.TERP_LS_PROPERTY_UNIT
    TerpPropertyUnitType = Base.classes.TERP_LS_PROPERTY_UNIT_TYPE
except AttributeError as e:
    logger.error(f"Property/Unit model not found: {e}")
    raise

# Accounting
try:
    TerpAccVoucher            = Base.classes.TERP_ACC_VOUCHER
    TerpAccVoucherTransaction = Base.classes.TERP_ACC_VOUCHER_TRANSACTION
    TerpAccChartLedgers       = Base.classes.TERP_ACC_CHART_OF_ACC_LEDGERS
    TerpAccTenantReceipt      = Base.classes.TERP_ACC_TENANT_RECEIPT
    TerpAccAmountType         = Base.classes.TERP_ACC_AMOUNT_TYPE
    logger.info("Accounting models reflected successfully")
except AttributeError as e:
    logger.error(f"Accounting model not found: {e}")
    raise

logger.info("All revenue-related models loaded successfully")

__all__ = [
    "TerpContract",
    "TerpContractChargesView",
    "TerpPaymentTerms",
    "TerpProperty",
    "TerpPropertyUnit",
    "TerpPropertyUnitType",
    "TerpAccVoucher",
    "TerpAccVoucherTransaction",
    "TerpAccChartLedgers",
    "TerpAccTenantReceipt",
    "TerpAccAmountType",
    "metadata",
    "Base",
]