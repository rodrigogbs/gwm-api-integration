import aiohttp
import async_timeout

class HavalAPI:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.token = None

    async def login(self):
        async with aiohttp.ClientSession() as session:
            async with async_timeout.timeout(30):
                async with session.post(
                    "https://api.gwm.com.br/app/auth/login",
                    json={
                        "username": self.email,
                        "password": self.password
                    }
                ) as response:
                    data = await response.json()
                    self.token = data["data"]["accessToken"]

    async def get_status(self):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with async_timeout.timeout(30):
                async with session.get(
                    "https://api.gwm.com.br/app/vehicle/status"
                ) as response:
                    data = await response.json()
                    return data["data"]
