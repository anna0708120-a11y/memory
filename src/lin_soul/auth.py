"""Bearer-token verification for the MCP SDK."""

from __future__ import annotations

import os
import secrets

if not os.environ.get("LIN_SOUL_AUTH_TOKEN"):
    raise RuntimeError("LIN_SOUL_AUTH_TOKEN must be set")


from mcp.server.auth.provider import AccessToken


class LinSoulTokenVerifier:
    """Verify the single static bearer token used by Lin Soul."""

    async def verify_token(self, token: str) -> AccessToken | None:
        expected_token = os.environ.get("LIN_SOUL_AUTH_TOKEN")
        if expected_token is None or not secrets.compare_digest(token, expected_token):
            return None
        return AccessToken(token=token, client_id="lin-soul-client", scopes=[])
