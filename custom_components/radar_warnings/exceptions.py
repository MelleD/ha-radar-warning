"""Exceptions for radar_warnings."""
from .const import LOGGER

class RadarWarningConnectionError(Exception):
    """RadarWarning connection exception."""

    def __init__(self, message, status_code=None, details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details
        LOGGER.error(self.__str__())
    
    def __str__(self):
        if self.status_code:
            return f"{self.message} (Status code: {self.status_code}, Details: {self.details})"
        return self.message