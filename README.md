# PYGPS JWT

FASTAPI python API endpoint

Main app code:
* It receives an HTTP GET call
* It generates JWT token

As a frontend the API endpoint has an NGINX reverse proxy
NGINX provides:
* client/server mTLS authentication
* SSL tunnel termination
