from locust import HttpUser, task, between # type: ignore
from typing import Optional, Callable, Union # For host type hint and wait_time


class HelloWorldUser(HttpUser):
    """
    A simple Locust user that makes a GET request to "/".
    """
    # Type hint for wait_time.
    # between(1,5) returns a callable.
    # If Pyright has issues with 'between' types from locust stubs,
    # type: ignore is a pragmatic way to handle it.
    wait_time: Callable[['HelloWorldUser'], Union[float, int]] = between(1, 5) # type: ignore

    # Type hint for host, matching Optional[str] from the User base class.
    host: Optional[str] = "http://localhost:{{cookiecutter.app_port_host}}"  # Default application port

    @task
    def hello_world(self) -> None:
        """
        Task that sends a GET request to the root endpoint.
        """
        # Example of making a request.
        # The actual endpoint depends on what your target application serves.
        self.client.get("/")
        print("User requested /")

# Example of how you might run this if it were a standalone script (not typical for locust)
# if __name__ == "__main__":
#    # This part is usually handled by the Locust runner
#    # For local testing or understanding, you might instantiate and call tasks,
#    # but it's not how Locust itself operates.
#    user = HelloWorldUser(environment.Environment()) # Needs an Environment
#    user.hello_world()
