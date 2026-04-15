from locust import HttpUser, task, between

class VMUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def login(self):
        self.client.post(
            "/login",
            json={
                "username": "testuser",
                "password": "testpass"
            },
            headers={
                "Content-Type": "application/json"
            }
        )