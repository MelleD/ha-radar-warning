"""Exceptions for the radar_warnings integration."""

from homeassistant.exceptions import HomeAssistantError


class EntityNotFoundError(HomeAssistantError):
    """When a referenced entity was not found."""
