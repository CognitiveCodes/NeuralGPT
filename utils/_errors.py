from requests.exceptions import HTTPError, RequestException


class HuggingFaceHubError(Exception):
    """Base class for Hugging Face Hub errors."""
    pass


class ModelNotFound(HuggingFaceHubError):
    """Raised when a model is not found on the Hub."""
    pass


class AuthenticationFailed(HuggingFaceHubError):
    """Raised when authentication fails."""
    pass


class DownloadError(HuggingFaceHubError):
    """Raised when a download error occurs."""
    pass


class CacheError(HuggingFaceHubError):
    """Raised when a caching error occurs."""
    pass


class UsageError(HuggingFaceHubError):
    """Raised when there is an error in how the user is using the package."""
    pass


class ModelCardError(HuggingFaceHubError):
    """Raised when there is an error with the model card."""
    pass


class ModelConfigurationError(HuggingFaceHubError):
    """Raised when there is an error with the model configuration."""
    pass


class ModelLoadError(HuggingFaceHubError):
    """Raised when there is an error loading the model."""
    pass


class ModelMismatch(HuggingFaceHubError):
    """Raised when the loaded model doesn't match the requested model."""
    pass


class ModelHubError(HuggingFaceHubError):
    """Raised when there is an error with the model hub."""
    pass


class PipelineException(HuggingFaceHubError):
    """Raised when there is an error with the model pipeline."""
    pass


class UnidentifiedObjectError(HuggingFaceHubError):
    """Raised when an object cannot be identified."""
    pass


class UnrecognizedFileType(HuggingFaceHubError):
    """Raised when a file type is not recognized."""
    pass


class UnrecognizedTaskError(HuggingFaceHubError):
    """Raised when a task is not recognized."""
    pass


class UnrecognizedVerbosityLevel(HuggingFaceHubError):
    """Raised when a verbosity level is not recognized."""
    pass


class UnsupportedFeature(HuggingFaceHubError):
    """Raised when a feature is not supported."""
    pass


class UnsupportedLanguageError(HuggingFaceHubError):
    """Raised when a language is not supported."""
    pass


class UnsupportedPipelineException(PipelineException):
    """Raised when a pipeline is not supported."""
    pass


class ConfigurationError(HuggingFaceHubError):
    """Raised when there is an error with the configuration."""
    pass


class DatasetError(HuggingFaceHubError):
    """Raised when there is an error with the dataset."""
    pass


class TrainerError(HuggingFaceHubError):
    """Raised when there is an error with the trainer."""
    pass


class ValidationError(HuggingFaceHubError):
    """Raised when there is a validation error."""
    pass


class MaxRetryError(HuggingFaceHubError):
    """Raised when the maximum number of retries has been exceeded."""
    pass


class RetryError(HuggingFaceHubError):
    """Raised when there is an error with the retry mechanism."""
    pass


class RequestError(RequestException):
    """Raised when there is an error with the request."""
    pass


class HTTPError(RequestException):
    """Raised when an HTTP error occurs."""
    pass