#############
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData
from sqlalchemy import inspect
from app.services.database import engine

metadata = MetaData()
inspector = inspect(engine)
# Step 1: Reflect all schemas
# First attempt: reflect entire schema at once (fast).
# Fallback: reflect table-by-table, skipping broken ones.
# This handles cross-schema FK crashes (e.g. TERP_LEGAL_CASE_DETAILS).

schemas = inspector.get_schema_names()

for schema in schemas:
    try:
        metadata.reflect(bind=engine, schema=schema, resolve_fks=False)
    except Exception:
        # Bulk reflect failed — fall back to per-table reflection
        print(f"Info: Bulk reflect failed for '{schema}', switching to per-table mode...")
        reflected, skipped = 0, 0
        for tname in inspector.get_table_names(schema=schema):
            try:
                metadata.reflect(
                    bind=engine,
                    schema=schema,
                    only=[tname],
                    resolve_fks=False,
                )
                reflected += 1
            except Exception:
                skipped += 1
        print(f"Info: Schema '{schema}' — reflected {reflected} tables, skipped {skipped}.")


# Step 2: Remove all foreign keys to avoid automap errors

for table in metadata.tables.values():
    table.foreign_keys.clear()
    table.constraints = {
        c for c in table.constraints
        if c.__class__.__name__ != "ForeignKeyConstraint"
    }


# Step 3: Build automap base

Base = automap_base(metadata=metadata)

def _no_relationship(*args, **kwargs):
    return None

Base.prepare(generate_relationship=_no_relationship)


# Step 4: Helper — resolve table regardless of schema prefix

def _get_class(table_name: str):
    """
    Finds the automap class for a table, handling schema-prefixed
    keys like 'EQUAL_PROPERTY_AI.TERP_LS_LEADS_ENQUIRY' transparently.
    """
    if table_name in Base.classes:
        return Base.classes[table_name]
    for key in metadata.tables:
        if key == table_name or key.endswith(f".{table_name}"):
            plain = key.split(".")[-1]
            if plain in Base.classes:
                return Base.classes[plain]
    raise AttributeError(f"Table '{table_name}' not found in reflected metadata")


# Step 5: Assign models — fail loudly with helpful message

REQUIRED_TABLES = {
    # TERP_LEADS core tables
    "EqLsLeads":                "eq_ls_leads",
    "EqLsLeadsConversion":      "eq_ls_leads_conversion",
    "EqLsLeadsChannel":         "eq_ls_leads_channel",
    "EqLsLeadsRatings":         "eq_ls_leads_ratings",
    "EqLsLeadsStatus":          "eq_ls_leads_status",
    "EqLsLeadsFollowup":        "eq_ls_leads_followup",
    "EqLsLeadsMeeting":         "eq_ls_leads_meeting",
    "EqLsLeadsMeetingDocs":     "eq_ls_leads_meeting_docs",
    "EqLsLeadsMeetingEnquiry":  "eq_ls_leads_meeting_enquiry",
    "EqLsLeadsMeetingReschedule": "eq_ls_leads_meeting_reschedule",
    "EqLsLeadsMeetingStatus":   "eq_ls_leads_meeting_status",
    "EqLsLeadsEnquiry":         "eq_ls_leads_enquiry",
    "EqLsLeadsEnquiryProp":     "eq_ls_leads_enquiry_prop",
    "EqLsLeadsEnquiryPropUnit": "eq_ls_leads_enquiry_prop_unit",
    "EqLsLeadsAttendees":       "eq_ls_leads_attendees",
    "EqLsLeadsAdditionalContacts": "eq_ls_leads_additional_contacts",
    "EqLsLeadAssignees":        "eq_ls_lead_assignees",
    "EqLsLeadInterestLevels":   "eq_ls_lead_interest_levels",
    "EqLsLeadResourceHistory":  "eq_ls_lead_resource_history",
    "EqLsLeadStaging":          "eq_ls_lead_staging",
    "EqLsLeadsRescheduleAttendees": "eq_ls_leads_reschedule_attendees",
    # TERP_LS listing tables
    
    "EqLsPropertyUnit":        "eq_ls_property_unit",
    "EqLsPropertyUnitStatus":  "eq_ls_property_unit_status",
    "EqLsProperty":            "eq_ls_property",
    "EqLsTenantType":           "eq_ls_tenant_type"
}

available = list(Base.classes.keys())
missing = []

for var_name, table_name in REQUIRED_TABLES.items():
    try:
        globals()[var_name] = _get_class(table_name)
    except AttributeError:
        missing.append(f"  - {var_name} (table: {table_name})")

if missing:
    raise RuntimeError(
        f"\n[reflected_models] Failed to reflect the following tables:\n"
        + "\n".join(missing)
        + f"\n\nTables actually found in DB: {available}"
        + "\n\nCheck: (1) DB connection is working, "
          "(2) table names match exactly (case-sensitive), "
          "(3) table has a primary key (automap skips tables without PKs)."
    )