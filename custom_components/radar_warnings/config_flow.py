"""Config flow for the radar_warnings integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from homeassistant.const import (
    CONF_NAME,
    CONF_RADIUS,
    CONF_SCAN_INTERVAL,
    CONF_SHOW_ON_MAP
)
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE

class RadarWarningsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the config flow for the radar_warnings integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict = {}

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                errors=errors,
                data_schema=vol.Schema(
                    {
                        vol.Required(
                            CONF_NAME, default=self.hass.config.location_name
                        ): cv.string,
                        vol.Required(
                            CONF_LATITUDE, default=self.hass.config.latitude
                        ): cv.latitude,
                        vol.Required(
                            CONF_LONGITUDE, default=self.hass.config.longitude
                        ): cv.longitude,
                        vol.Required(
                            CONF_RADIUS, default=self.hass.config.radius
                        ): cv.positive_float,
                        vol.Required(
                            CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                        ): cv.positive_int,
                        vol.Required(
                            CONF_SHOW_ON_MAP, default=True
                        ): cv.boolean
                    }
                ),
            )

        identifier = f"{user_input[CONF_NAME]}"
        # Set the unique ID for this config entry.
        await self.async_set_unique_id(identifier)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input
            )
        


