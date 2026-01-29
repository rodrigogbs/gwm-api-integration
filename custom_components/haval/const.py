DOMAIN = "haval"

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_CHASSIS = "chassis"  # VIN / chassis code (used as deviceid in login, as per Postman/original)
CONF_DEVICE_ID = "device_id"  # kept for backward compat (we will store same as chassis)
CONF_COMMAND_PASSWORD = "command_password"

# Endpoints (from Postman collection)
AUTH_BASE = "https://br-front-service.gwmcloud.com/br-official-commerce/br-official-gateway/pc-api/api/v1.0"
APP_BASE = "https://br-app-gateway.gwmcloud.com/app-api/api/v1.0/"

PLATFORMS = ["sensor", "device_tracker", "climate"]
DEFAULT_POLL_SECONDS = 300
