"""LMS API client for backend communication."""

import os
import re

import httpx

# Clear proxy environment variables at module load to avoid httpx issues
_PROXY_VARS = [
    "HTTP_PROXY", "HTTPS_PROXY", "FTP_PROXY", "ALL_PROXY",
    "http_proxy", "https_proxy", "ftp_proxy", "all_proxy",
]
_old_proxy_values = {}
for var in _PROXY_VARS:
    if var in os.environ:
        _old_proxy_values[var] = os.environ.pop(var)


class LMSAPIClient:
    """Client for the LMS backend API.

    Uses Bearer token authentication with the LMS_API_KEY.
    """

    def __init__(self, base_url: str, api_key: str) -> None:
        """Initialize the API client.

        Args:
            base_url: Base URL of the LMS backend (e.g., http://localhost:42002)
            api_key: API key for authentication (LMS_API_KEY)
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10.0,
        )

    async def health_check(self) -> dict:
        """Check if the backend is healthy by querying items endpoint.

        Returns:
            Dict with status info.
        """
        try:
            response = await self._client.get("/items/")
            response.raise_for_status()
            items = response.json()
            return {"status": "ok", "message": f"Backend is healthy. {len(items)} items available."}
        except httpx.HTTPError as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": f"Backend unreachable: {e}"}

    async def get_labs(self) -> list[dict]:
        """Get list of available labs.

        Returns:
            List of lab objects.
        """
        try:
            response = await self._client.get("/items/")
            response.raise_for_status()
            items = response.json()
            # Extract labs where type == "lab"
            labs = []
            for item in items:
                if item.get("type") == "lab":
                    lab_id = f"lab-{item['id']:02d}"
                    title = item.get("title", f"Lab {item['id']}")
                    labs.append({"id": lab_id, "name": title, "item_id": item["id"]})
            return labs
        except httpx.HTTPError as e:
            return []
        except Exception:
            return []

    def _lab_name_to_id(self, lab_name: str) -> str | None:
        """Convert lab name like 'lab-07' or 'lab 7' to item ID.

        Args:
            lab_name: Lab identifier (e.g., "lab-07", "lab-1", "7")

        Returns:
            Item ID or None if not found.
        """
        # Extract number from lab name
        match = re.search(r"(\d+)", lab_name)
        if not match:
            return None
        lab_num = int(match.group(1))
        return lab_num

    async def get_scores(self, lab_name: str) -> dict:
        """Get scores for a specific lab.

        Args:
            lab_name: The lab identifier (e.g., "lab-04", "lab-07")

        Returns:
            Dict with scores data.
        """
        try:
            # Get lab item ID from name
            lab_id = self._lab_name_to_id(lab_name)
            if not lab_id:
                return {"error": f"Invalid lab name: {lab_name}"}

            # Get score distribution from analytics
            response = await self._client.get(f"/analytics/scores?lab=lab-{lab_id:02d}")
            response.raise_for_status()
            scores = response.json()

            # Get group stats
            groups_response = await self._client.get(f"/analytics/groups?lab=lab-{lab_id:02d}")
            groups_response.raise_for_status()
            groups = groups_response.json()

            # Calculate totals from score buckets
            total_students = sum(bucket["count"] for bucket in scores)
            
            # Calculate average score (weighted by bucket midpoints)
            bucket_midpoints = {"0-25": 12.5, "26-50": 38, "51-75": 63, "76-100": 88}
            weighted_sum = sum(
                bucket_midpoints.get(bucket["bucket"], 50) * bucket["count"]
                for bucket in scores
            )
            avg_score = weighted_sum / total_students if total_students > 0 else 0

            # Count students who passed (score >= 51)
            passed = sum(bucket["count"] for bucket in scores if bucket["bucket"] in ["51-75", "76-100"])
            pass_rate = (passed / total_students * 100) if total_students > 0 else 0

            return {
                "lab_id": f"lab-{lab_id:02d}",
                "total_students": total_students,
                "passed": passed,
                "pass_rate": pass_rate,
                "avg_score": avg_score,
                "groups": len(groups),
                "score_distribution": scores,
            }

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": f"Lab '{lab_name}' not found"}
            return {"error": f"API error: {e}"}
        except httpx.HTTPError as e:
            return {"error": f"Backend error: {e}"}
        except Exception as e:
            return {"error": f"Unexpected error: {e}"}

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
