from typing import Any, ClassVar, Dict, Optional, Set

from pydantic import BaseModel, ConfigDict, Field, field_validator, HttpUrl

from .. import __version__


class RequestModel(BaseModel):
    """Data model for REST client configuration."""

    # Class variables need to be annotated with ClassVar
    VALID_METHODS: ClassVar[Set[str]] = {
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "HEAD",
    }

    DEFAULT_USER_AGENT: ClassVar[str] = f"grpy-request-client/{__version__}"

    DEFAULT_HEADERS: ClassVar[Dict[str, str]] = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": DEFAULT_USER_AGENT,
    }

    base_url: HttpUrl = Field()
    method: str = Field(default="GET")
    endpoint: str = Field(default="")
    timeout: float = Field(default=30, gt=0)
    params: Dict[str, str] = Field(default_factory=dict)
    headers: Dict[str, str] = Field(default_factory=dict)
    data: Optional[Dict[str, Any]] = Field(default=None)

    # Use ConfigDict instead of class Config
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("method")
    def validate_method(cls, v):
        if v not in cls.VALID_METHODS:
            raise ValueError(f"Invalid HTTP method: {v}. Must be one of {cls.VALID_METHODS}")
        return v

    def __init__(self, **data):
        headers = self.DEFAULT_HEADERS.copy()
        if "headers" in data and data["headers"]:
            headers.update(data["headers"])
        data["headers"] = headers

        super().__init__(**data)

    def update_headers(self, headers: Dict[str, str]) -> None:
        """Update the headers for this client.

        Args:
            headers: New headers to add or update
        """

        if not self.headers:
            self.headers = self.DEFAULT_HEADERS
        else:
            self.headers.update(headers)
