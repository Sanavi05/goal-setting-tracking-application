class EntraIdService:
    """Placeholder for Microsoft Entra ID SSO and group-to-role mapping."""

    GROUP_ROLE_MAP = {
        "goalgrid-admins": "ADMIN",
        "goalgrid-managers": "MANAGER",
        "goalgrid-employees": "EMPLOYEE",
    }

    def exchange_code_for_profile(self, authorization_code: str) -> dict:
        raise NotImplementedError("Wire Microsoft Graph token exchange here when SSO is enabled.")

    def role_from_groups(self, groups: list[str]) -> str:
        for group in groups:
            if group in self.GROUP_ROLE_MAP:
                return self.GROUP_ROLE_MAP[group]
        return "EMPLOYEE"
