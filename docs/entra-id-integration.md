# Microsoft Entra ID Integration Placeholder

Future SSO can be added with Microsoft identity platform OAuth/OIDC.

## Intended Flow

1. Frontend redirects users to Microsoft login.
2. Backend exchanges authorization code for tokens.
3. Backend reads user profile and group claims.
4. Group names map to GoalGrid roles.
5. Backend issues the app JWT used by existing APIs.

## Group-to-Role Mapping

- `goalgrid-admins` -> `ADMIN`
- `goalgrid-managers` -> `MANAGER`
- `goalgrid-employees` -> `EMPLOYEE`

The placeholder implementation lives in `backend/app/services/entra.py`.
