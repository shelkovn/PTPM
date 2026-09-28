from abc import ABC, abstractmethod

class ExternalServiceInterface(ABC):
    @abstractmethod
    def send_result(self, result_str: str) -> None:
        pass

class ExternalService(ExternalServiceInterface):
    def send_result(self, result_str: str) -> None:
        print(f"[ExternalService] sent: '{result_str}'")