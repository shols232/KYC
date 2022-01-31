from __future__ import annotations

from typing import Any, Optional

from client.models import Client
from kyc.bvn.models import BVNVerification


class BaseBVNVerificationManager:
    def __init__(self, client: Client) -> None:
        """Init method."""
        self.errors: list[str] = []
        self.provider_failure = False
        self.client = client

    def get_bvn_verification_object_from_api(self, value: str, user_data: dict[str, Any]) -> Optional[BVNVerification]:
        """To be implemented by specifc manager."""
        raise NotImplementedError('provide implementation')
