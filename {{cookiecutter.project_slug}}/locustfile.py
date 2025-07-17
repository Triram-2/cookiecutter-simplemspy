from locust import HttpUser, constant, task  # type: ignore
from typing import Callable, Optional, Union


class HealthUser(HttpUser):
    """Locust user that spams ``/health`` requests."""

    wait_time: Callable[["HealthUser"], Union[float, int]] = constant(0)
    host: Optional[str] = "http://localhost:{{cookiecutter.app_port_host}}"

    @task
    def health(self) -> None:
        """Send a ``GET`` request to the ``/health`` endpoint."""
        self.client.get("/health")


# Example of how you might run this if it were a standalone script (not typical for locust)
# if __name__ == "__main__":
#    # This part is usually handled by the Locust runner
#    # For local testing or understanding, you might instantiate and call tasks,
#    # but it's not how Locust itself operates.
#    user = HealthUser(environment.Environment())  # Needs an Environment
#    user.health()
