"""MongoDB query functions used by the SFILS application."""


REFERENCE_COLLECTIONS = {
    "patron_type": ("patron_types", "patron_type_code", "patron_type_definition"),
    "home_library": ("home_libraries", "home_library_code", "home_library_definition"),
    "notification_medium": (
        "notification_media",
        "notification_medium_code",
        "notification_medium_definition",
    ),
}

USAGE_FIELDS = {
    "_id": 0,
    "usage_id": 1,
    "age_range": 1,
    "checkout_total": 1,
    "renewal_total": 1,
    "patron_type_code": 1,
    "home_library_code": 1,
}


def get_reference_data(database, collection_name):
    """Return code and definition documents from an allowed reference collection."""
    if collection_name not in REFERENCE_COLLECTIONS:
        raise ValueError("Unknown reference collection")

    actual_name, code_field, definition_field = REFERENCE_COLLECTIONS[collection_name]
    projection = {"_id": 0, code_field: 1, definition_field: 1}
    return list(
        database[actual_name].find({}, projection).sort(code_field, 1)
    )


def search_by_age(database, age_range):
    """Find up to 100 usage documents matching an age range."""
    return list(
        database.library_usage.find(
            {"age_range": age_range}, USAGE_FIELDS
        ).sort("usage_id", 1).limit(100)
    )


def search_by_library(database, library_code):
    """Find up to 100 usage documents matching a home library code."""
    return list(
        database.library_usage.find(
            {"home_library_code": library_code}, USAGE_FIELDS
        ).sort("usage_id", 1).limit(100)
    )


def get_usage_summary(database):
    """Group checkouts and renewals by patron type using an aggregation pipeline."""
    pipeline = [
        {
            "$lookup": {
                "from": "patron_types",
                "localField": "patron_type_code",
                "foreignField": "patron_type_code",
                "as": "patron_type_info",
            }
        },
        {
            "$unwind": {
                "path": "$patron_type_info",
                "preserveNullAndEmptyArrays": True,
            }
        },
        {
            "$group": {
                "_id": {
                    "code": "$patron_type_code",
                    "definition": "$patron_type_info.patron_type_definition",
                },
                "record_count": {"$sum": 1},
                "total_checkouts": {"$sum": {"$ifNull": ["$checkout_total", 0]}},
                "total_renewals": {"$sum": {"$ifNull": ["$renewal_total", 0]}},
            }
        },
        {
            "$project": {
                "_id": 0,
                "patron_type_code": "$_id.code",
                "patron_type_definition": "$_id.definition",
                "record_count": 1,
                "total_checkouts": 1,
                "total_renewals": 1,
            }
        },
        {"$sort": {"total_checkouts": -1}},
    ]
    return list(database.library_usage.aggregate(pipeline))


def update_checkout_total(database, usage_id, new_total):
    """Update one usage document and return the number of matched documents."""
    if new_total < 0:
        raise ValueError("Checkout total cannot be negative")

    result = database.library_usage.update_one(
        {"usage_id": usage_id},
        {"$set": {"checkout_total": new_total}},
    )
    return result.matched_count
