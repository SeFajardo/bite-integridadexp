"""Integrity helpers: deterministic SHA-256 hashing for cloud reports."""
import hashlib
import json


def compute_report_hash(report_instance) -> str:
    """
    Compute the SHA-256 hash over the critical fields of a report.
    Serialization is deterministic (sort_keys=True) so the same logical
    data always yields the same hex digest.
    """
    critical_data = {
        "project_name": report_instance.project_name,
        "month": report_instance.month,
        "year": report_instance.year,
        "services": report_instance.services,
        "total_cost": str(report_instance.total_cost),
        "currency": report_instance.currency,
    }
    canonical = json.dumps(critical_data, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def verify_report_integrity(report_instance) -> bool:
    """Return True iff the stored hash matches a freshly recomputed one."""
    if not report_instance.report_hash:
        return False
    computed = compute_report_hash(report_instance)
    return computed == report_instance.report_hash
