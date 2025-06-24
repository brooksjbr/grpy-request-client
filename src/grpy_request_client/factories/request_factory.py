from src.grpy_request_client.models.request_model import RequestModel


class RequestFactory:
    """Factory class for creating RequestModel instances."""

    @staticmethod
    def create_request(data: dict):
        return RequestModel(data)
