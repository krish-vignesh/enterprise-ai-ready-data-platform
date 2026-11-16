"""Company-level permission definitions and role authorization policy."""

from enum import Enum

from app.models.company_membership import CompanyRole


class CompanyPermission(str, Enum):
    """Actions that can be authorized within a company."""

    VIEW_COMPANY_RESOURCES = "VIEW_COMPANY_RESOURCES"
    CREATE_SOURCE_SYSTEM = "CREATE_SOURCE_SYSTEM"
    CREATE_DATASET = "CREATE_DATASET"
    UPLOAD_DOCUMENT = "UPLOAD_DOCUMENT"
    MANAGE_MEMBERS_AND_ROLES = "MANAGE_MEMBERS_AND_ROLES"
    DELETE_COMPANY = "DELETE_COMPANY"


COMPANY_ROLE_PERMISSIONS: dict[CompanyRole, frozenset[CompanyPermission]] = {
    CompanyRole.OWNER: frozenset(
        {
            CompanyPermission.VIEW_COMPANY_RESOURCES,
            CompanyPermission.CREATE_SOURCE_SYSTEM,
            CompanyPermission.CREATE_DATASET,
            CompanyPermission.UPLOAD_DOCUMENT,
            CompanyPermission.MANAGE_MEMBERS_AND_ROLES,
            CompanyPermission.DELETE_COMPANY,
        }
    ),
    CompanyRole.ADMIN: frozenset(
        {
            CompanyPermission.VIEW_COMPANY_RESOURCES,
            CompanyPermission.CREATE_SOURCE_SYSTEM,
            CompanyPermission.CREATE_DATASET,
            CompanyPermission.UPLOAD_DOCUMENT,
        }
    ),
    CompanyRole.MEMBER: frozenset(
        {
            CompanyPermission.VIEW_COMPANY_RESOURCES,
            CompanyPermission.CREATE_SOURCE_SYSTEM,
            CompanyPermission.UPLOAD_DOCUMENT,
        }
    ),
}


def role_has_permission(
    role: CompanyRole,
    permission: CompanyPermission,
) -> bool:
    """Return whether a company role is allowed to perform a permission."""

    allowed_permissions = COMPANY_ROLE_PERMISSIONS.get(role, frozenset())

    return permission in allowed_permissions
