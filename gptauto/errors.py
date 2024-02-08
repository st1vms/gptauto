"""Custom errors module"""


class DriverNotInitializedError(Exception):
    """Exception for when a scraper operation is called,
    without initializing driver instance"""
