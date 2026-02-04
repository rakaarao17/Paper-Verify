"""Custom exceptions for paper-verify."""


class PaperVerifyError(Exception):
    """Base exception for paper-verify."""
    pass


class FileNotFoundError(PaperVerifyError):
    """Raised when a required file is not found."""
    pass


class ParseError(PaperVerifyError):
    """Raised when parsing fails."""
    pass


class ValidationError(PaperVerifyError):
    """Raised when validation encounters an error."""
    pass


class ConfigurationError(PaperVerifyError):
    """Raised when configuration is invalid."""
    pass
