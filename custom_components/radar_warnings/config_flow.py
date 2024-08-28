"""Config flow for the radar_warnings integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers import entity_registry as er
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import EntitySelector, EntitySelectorConfig

from .const import CONF_ZONE_ENTITY, DOMAIN
from homeassistant.const import (
    CONF_NAME,
    CONF_RADIUS
)
from .exceptions import EntityNotFoundError
from .util import get_zone_position_data

class RadarWarningsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the config flow for the radar_warnings integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict = {}
        position = None

        if user_input is not None:
            zone_enity = user_input[CONF_ZONE_ENTITY]
            if zone_enity is None:
                errors["base"] = "zone_entity_not_found"

            radius = user_input[CONF_RADIUS]
            registry = er.async_get(self.hass)
            entity_entry = registry.async_get(zone_enity)


            if entity_entry is None:
                errors["base"] = "zone_entity_not_found"

            if radius is None:
                radius = 10
            
            try:
                position = get_zone_position_data(self.hass, entity_entry.id)
            except EntityNotFoundError:
                errors["base"] = "zone_entity_not_found"
            except AttributeError:
                errors["base"] = "attribute_not_found"

            # Position is valid here, because the API call was successful.
            if not errors and position is not None and entity_entry is not None:
                    # Set the unique ID for this config entry.
                await self.async_set_unique_id(entity_entry.id)
                self._abort_if_unique_id_configured()


            return self.async_create_entry(
                        title=user_input[CONF_NAME],
                        data=user_input,
                    )

        return self.async_show_form(
            step_id="user",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_NAME
                    ): cv.string,
                    vol.Required(CONF_ZONE_ENTITY): EntitySelector(
                        EntitySelectorConfig(domain="zone")
                    ),
                     vol.Optional(CONF_RADIUS): cv.string,
                }
            ),
        )
