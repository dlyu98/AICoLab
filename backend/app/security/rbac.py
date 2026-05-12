ROLE_PERMISSIONS = {
    "clinician": {"read_patient", "run_agents", "read_audit"},
    "care_manager": {"read_patient", "run_agents"},
    "analyst": {"ask_operations", "read_audit"},
    "admin": {"read_patient", "run_agents", "ask_operations", "read_audit", "settings"},
}


def has_permission(role: str, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())
