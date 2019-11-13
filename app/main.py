# -*- coding: utf-8 -*-

"""
    Main app code
        It receives a GET call which goes through a mutual certificate authnetication beforehand
        It generates a JWT token
"""
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder

from starlette.requests import Request
from starlette.responses import JSONResponse

import jwt, uuid, time
from jwt.contrib.algorithms.pycrypto import RSAAlgorithm

from jwt.utils import base64url_decode, force_bytes, force_unicode
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import (
        load_pem_private_key,
        load_pem_public_key,
        load_ssh_public_key,
)

from .general_functions.logging_functions import fWriteLog
from .my_config.my_config import fCryptoVars


fName = "Main"

class CustomException(Exception):
    def __init__(self, detail: str, headers: str, statusCode: int, callId: str, elapsed: float):
        self.detail = detail
        self.headers = headers
        self.statusCode = statusCode
        self.callId = callId
        self.elapsed = elapsed

app = FastAPI(title="JWT")


# fastAPI exception_handler
@app.exception_handler(CustomException)
def fExceptionHandler(request: Request, exception: CustomException):
    # log
    fWriteLog(exception.callId, fName, f"{exception.detail}", "error")
    fWriteLog(exception.callId, fName, f"END Call. Duration: {exception.elapsed}", "info")
    return JSONResponse(
        status_code=exception.statusCode,
        headers=exception.headers,
        content={"message": f"Oops! {exception.detail}"}
    )

@app.get("/")
def fTest():
    return {"Hello": "World"}

@app.get("/get/jwt/")
def fGenerateJWT(request: Request) -> str:
    """
        Generate JWT token
    """
    # default response
    response = {'token': ''}

    callId = str(uuid.uuid1())
    start = time.perf_counter()
    fWriteLog(callId, fName, "START Call", "info")
    try:
        reqClient = request.client
        reqHeaders = request.headers
    except Exception as e:
        pass
    else:
        reqDump = {"reqClientHost": reqClient, "reqHeaders": reqHeaders}
        # debug 
        fWriteLog(callId, fName, f"Request: {str(reqDump)}", "debug")

    try:
        xIPAddress = reqHeaders["x-ip-address"]
    except Exception as e:
        raise CustomException(
            statusCode=417,
            detail="Wrong HTTP header - missing key.",
            headers={"X-Error": "Wrong HTTP header - missing key."},
            callId=callId,
            elapsed=round(time.perf_counter() - start, 5)
        )

    nowTime = round(time.time())

    # load default variables
    try:
        myCryptoVars = fCryptoVars()
        myPrivateKeyPath = myCryptoVars["privateKeyPath"]
    except NameError:
        fWriteLog(callId, fName, f"Variables load error: {str(e)}", "error")
        elapsed = round(time.perf_counter() - start, 5)
        fWriteLog(callId, fName, f"END Call. Duration: {str(elapsed)}", "info")
        raise CustomException(
            statusCode=417,
            detail="Variables load error.",
            headers={"X-Error": "Variables load error."},
            callId=callId,
            elapsed=round(time.perf_counter() - start, 5)
        )
    else:
        # debug    
        fWriteLog(callId, fName, f"Default variables loaded correctly.", "debug")
        
    # load the private key
    try:
        with open(myPrivateKeyPath, "r") as rsa_priv_file:
            privateKey = load_pem_private_key(
                force_bytes(rsa_priv_file.read()),
                password=None,
                backend=default_backend(),
            )
    except Exception as e:
        fWriteLog(callId, fName, f"Private key load returned error: {str(e)}", "error")
        elapsed = round(time.perf_counter() - start, 5)
        fWriteLog(callId, fName, f"END Call. Duration: {str(elapsed)}", "info")
        raise CustomException(
            statusCode=417,
            detail="Private key load error.",
            headers={"X-Error": "Private key load error."},
            callId=callId,
            elapsed=round(time.perf_counter() - start, 5)
        )
    else:
        # debug
        fWriteLog(callId, fName, f"Private key correctly read / loaded.", "debug")
        # encode JWT
        try:
            token = jwt.encode({
                'sub': 'endpoint',
                'iss': 'jwtproxy',
                # same as client_id from Gravitee API GW
                'aud': 'jwtendpoint',
                'roles': ['publisher'],
                'iat': nowTime,
                'nbf': round(nowTime - 30),
                'exp': nowTime + 300,
                'ipaddress': xIPAddress,
                'jti': str(uuid.uuid1())
                }, privateKey, algorithm='RS512').decode('utf-8')
        except Exception as e:
            fWriteLog(callId, fName, f"JWT encode returned error: {str(e)}", "error")
            elapsed = round(time.perf_counter() - start, 5)
            fWriteLog(callId, fName, f"END Call. Duration: {str(elapsed)}", "info")
            raise CustomException(
                statusCode=417,
                detail="Cannot generate JWT.",
                headers={"X-Error": "Cannot generate JWT."},
                callId=callId,
                elapsed=round(time.perf_counter() - start, 5)
            )
        else:
            fWriteLog(callId, fName, f"Token generated.", "info")
            # debug
            fWriteLog(callId, fName, f"Token generated: {str(jwt.decode(token, verify=False))}", "debug")
            response = {'token': token}

    elapsed = round(time.perf_counter() - start, 5)
    fWriteLog(callId, fName, f"END Call. Duration: {str(elapsed)}", "info")

    return jsonable_encoder(response)
