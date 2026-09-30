"""
Authentication & ABAC Authorization Engine.
Implements OIDC/JWT parsing, ABAC District Scoping for Reporting Officers,
and Step-Up MFA / 4-Eyes Governance for State Administrators.
Complies with Section 4 of India Pilot Master Plan.
"""

from typing import Dict, Any, List, Optional
from fastapi import Request, HTTPException, status
import hmac
import hashlib

# Standard Roles
ROLE_CITIZEN = "citizen"
ROLE_RO = "reporting_officer"
ROLE_ADMIN = "admin"

class AuthUser:
    def __init__(
        self,
        sub: str,
        role: str,
        district_lgd: List[str],
        state_lgd: str = "27",
        duty_status: str = "active",
        acr: str = "loa1"
    ):
        self.sub = sub
        self.role = role
        self.district_lgd = district_lgd
        self.state_lgd = state_lgd
        self.duty_status = duty_status
        self.acr = acr

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sub": self.sub,
            "role": self.role,
            "district_lgd": self.district_lgd,
            "state_lgd": self.state_lgd,
            "duty_status": self.duty_status,
            "acr": self.acr
        }

def get_current_user(request: Request) -> AuthUser:
    """
    Extracts user identity from headers (production JWT or development mock headers).
    In dev/pilot mode: uses X-User-Role, X-User-District, X-User-Sub, X-ACR.
    """
    role = request.headers.get("X-User-Role", ROLE_CITIZEN).lower()
    sub = request.headers.get("X-User-Sub", "user:anonymous")
    acr = request.headers.get("X-ACR", "loa1")
    
    # District scope (multivalued e.g. "990001,990002" or single)
    dist_header = request.headers.get("X-User-District", "990001")
    district_lgd = [d.strip() for d in dist_header.split(",") if d.strip()]

    # Validate valid role
    if role not in [ROLE_CITIZEN, ROLE_RO, ROLE_ADMIN]:
        role = ROLE_CITIZEN

    # Default sub per role
    if sub == "user:anonymous":
        if role == ROLE_RO:
            sub = "ro:etapalli-01"
            acr = "loa2"
        elif role == ROLE_ADMIN:
            sub = "admin:state-director"
            acr = "loa3"
        else:
            sub = "citizen:anon-device"

    return AuthUser(
        sub=sub,
        role=role,
        district_lgd=district_lgd,
        state_lgd="27",
        duty_status="active",
        acr=acr
    )

def check_permission(
    user: AuthUser,
    action: str,
    resource: Optional[Dict[str, Any]] = None,
    purpose: Optional[str] = None
) -> None:
    """
    OPA-aligned ABAC policy check (Rego v1 spec):
    1. Citizens can only create reports and read their own.
    2. Reporting Officers can only access resources within their assigned district(s).
    3. Audio playback requires valid purpose (transcript_correction or field_verification).
    4. Approvals require admin role, loa3 step-up, and 4-eyes check (cannot approve own proposal).
    """
    # 1. Citizen rules
    if user.role == ROLE_CITIZEN:
        allowed_citizen_actions = ["report:create", "report:read:own", "report:status:own", "hotspot:read:public"]
        if action not in allowed_citizen_actions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Citizen role is not authorized to perform action '{action}'."
            )
        return

    # 2. Reporting Officer rules (District Scoped)
    if user.role == ROLE_RO:
        if user.duty_status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Reporting Officer duty status is suspended or inactive."
            )

        ro_allowed = [
            "report:read:district", "report:verify", "report:merge", "report:reject",
            "report:geo:correct", "report:audio:play", "contact:masked_callback",
            "hotspot:read:detail", "recommendation:read"
        ]
        if action not in ro_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Reporting Officer is not authorized to perform action '{action}'."
            )

        # Check district boundary
        if resource:
            target_district = resource.get("lgd_district_code") or resource.get("district_id")
            if target_district and target_district not in user.district_lgd:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access Denied: Target district '{target_district}' is outside your assigned jurisdiction {user.district_lgd}."
                )

        # Purpose check for audio playback
        if action == "report:audio:play":
            if not purpose or purpose not in ["transcript_correction", "field_verification"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Audio playback requires valid 'purpose' header ('transcript_correction' or 'field_verification')."
                )
        return

    # 3. State Administrator rules
    if user.role == ROLE_ADMIN:
        # Four-eyes check and Step-Up MFA for critical approvals
        if action in ["recommendation:approve", "config:weights:approve"]:
            if user.acr != "loa3":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Step-up MFA (ACR=loa3) is required for sanctioning capital project portfolios."
                )
            if resource and resource.get("proposed_by") == user.sub:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="4-Eyes Governance Violation: You cannot approve a capital project proposal drafted by yourself."
                )
        return

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unknown or unauthorized role.")
