"""Config flow for the radar_warnings integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN
from homeassistant.const import (
    CONF_NAME,
    CONF_RADIUS,
    CONF_SCAN_INTERVAL
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

        if user_input is not None:
            return self.async_create_entry(
                        title=user_input[CONF_NAME],
                        data=user_input
                    )

        return self.async_show_form(
            step_id="user",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_NAME, default=self.hass.config.location_name
                    ): str,
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
                         CONF_SCAN_INTERVAL, default=60
                    ): cv.positive_float
                }
            ),
        )
