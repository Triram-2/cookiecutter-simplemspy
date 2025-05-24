from locust import HttpUser, task, between
from locust.user.wait_time import WaitTime # More specific import for WaitTime
from typing import Optional # For host type hint


class HelloWorldUser(HttpUser):
    """
    A simple Locust user that makes a GET request to "/".
    """
    # Type hint for wait_time.
    # between(1,5) returns an instance of a WaitTime subclass.
    # If Pyright has issues with 'between' or 'WaitTime' types from locust stubs,
    # type: ignore is a pragmatic way to handle it.
    wait_time: WaitTime = between(1, 5) # type: ignore

    # Type hint for host, matching Optional[str] from the User base class.
    host: Optional[str] = "http://localhost:8080" # Example host

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
