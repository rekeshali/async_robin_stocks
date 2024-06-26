"""Contains all functions for the purpose of logging in and out to Robinhood."""
import getpass
import os
import pickle
import random
import aiofiles
import asyncio

from async_robin_stocks.robinhood.helper import *
from async_robin_stocks.robinhood.urls import *

def generate_device_token():
    """This function will generate a token used when loggin on.

    :returns: A string representing the token.

    """
    rands = []
    for i in range(0, 16):
        r = random.random()
        rand = 4294967296.0 * r
        rands.append((int(rand) >> ((3 & i) << 3)) & 255)

    hexa = []
    for i in range(0, 256):
        hexa.append(str(hex(i+256)).lstrip("0x").rstrip("L")[1:])

    id = ""
    for i in range(0, 16):
        id += hexa[rands[i]]

        if (i == 3) or (i == 5) or (i == 7) or (i == 9):
            id += "-"

    return(id)


async def respond_to_challenge(client, challenge_id, sms_code):
    """This function will post to the challenge url.

    :param challenge_id: The challenge id.
    :type challenge_id: str
    :param sms_code: The sms code.
    :type sms_code: str
    :returns:  The response from requests.

    """
    url = challenge_url(challenge_id)
    payload = {
        'response': sms_code
    }
    return(await request_post(client, url, payload))


async def login(client, username=None, password=None, expiresIn=86400, scope='internal', by_sms=True, store_session=True, mfa_code=None, pickle_name=""):
    """This function will effectively log the user into robinhood by getting an
    authentication token and saving it to the session header. By default, it
    will store the authentication token in a pickle file and load that value
    on subsequent logins.

    :param username: The username for your robinhood account, usually your email.
        Not required if credentials are already cached and valid.
    :type username: Optional[str]
    :param password: The password for your robinhood account. Not required if
        credentials are already cached and valid.
    :type password: Optional[str]
    :param expiresIn: The time until your login session expires. This is in seconds.
    :type expiresIn: Optional[int]
    :param scope: Specifies the scope of the authentication.
    :type scope: Optional[str]
    :param by_sms: Specifies whether to send an email(False) or an sms(True)
    :type by_sms: Optional[boolean]
    :param store_session: Specifies whether to save the log in authorization
        for future log ins.
    :type store_session: Optional[boolean]
    :param mfa_code: MFA token if enabled.
    :type mfa_code: Optional[str]
    :param pickle_name: Allows users to name Pickle token file in order to switch
        between different accounts without having to re-login every time.
    :returns:  A dictionary with log in information. The 'access_token' keyword contains the access token, and the 'detail' keyword \
    contains information on whether the access token was generated or loaded from pickle file.

    """
    device_token = generate_device_token()
    home_dir = os.path.expanduser("~")
    data_dir = os.path.join(home_dir, ".tokens")
    # Make directory if it does not exist
    if not await asyncio.to_thread(os.path.exists, data_dir):
        await aiofiles.os.mkdir(data_dir)
    creds_file = "robinhood" + pickle_name + ".pickle"
    pickle_path = os.path.join(data_dir, creds_file)
    # Challenge type is used if not logging in with two-factor authentication.
    if by_sms:
        challenge_type = "sms"
    else:
        challenge_type = "email"

    url = login_url()
    payload = {
        'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS',
        'expires_in': expiresIn,
        'grant_type': 'password',
        'password': password,
        'scope': scope,
        'username': username,
        'challenge_type': challenge_type,
        'device_token': device_token
    }

    if mfa_code:
        payload['mfa_code'] = mfa_code

    # If authentication has been stored in pickle file then load it. Stops login server from being pinged so much.
    if await asyncio.to_thread(os.path.exists, pickle_path):
        # If store_session has been set to false then delete the pickle file, otherwise try to load it.
        # Loading pickle file will fail if the access_token has expired.
        if store_session:
            try:
                async with aiofiles.open(pickle_path, 'rb') as f:
                    data = await f.read()
                    pickle_data = pickle.loads(data)
                    access_token = pickle_data['access_token']
                    token_type = pickle_data['token_type']
                    refresh_token = pickle_data['refresh_token']
                    # Set device_token to be the original device token when first logged in.
                    pickle_device_token = pickle_data['device_token']
                    payload['device_token'] = pickle_device_token
                    # Set login status to True in order to try and get account info.
                    client.set_login_state(True)
                    client.update_session(
                        'Authorization', '{0} {1}'.format(token_type, access_token))
                    # Try to load account profile to check that authorization token is still valid.
                    res = await request_get(client, 
                        positions_url(), 'pagination', {'nonzero': 'true'}, jsonify_data=False)
                    # Raises exception if response code is not 200.
                    res.raise_for_status()
                    return({'access_token': access_token, 'token_type': token_type,
                            'expires_in': expiresIn, 'scope': scope, 'detail': 'logged in using authentication in {0}'.format(creds_file),
                            'backup_code': None, 'refresh_token': refresh_token})
            except:
                await client.loger.error(
                    "There was an issue loading pickle file. Authentication may be expired - logging in normally.")
                client.set_login_state(False)
                client.update_session('Authorization', None)
        else:
            await aiofiles.os.remove(pickle_path)

    # Try to log in normally.
    if not username:
        username = input("Robinhood username: ")
        payload['username'] = username

    if not password:
        password = getpass.getpass("Robinhood password: ")
        payload['password'] = password

    data = await request_post(client, url, payload)
    # Handle case where mfa or challenge is required.
    if data:
        if 'mfa_required' in data:
            mfa_token = input("Please type in the MFA code: ")
            payload['mfa_code'] = mfa_token
            res = await request_post(client, url, payload, jsonify_data=False)
            while res.status != 200:
                mfa_token = input(
                    "That MFA code was not correct. Please type in another MFA code: ")
                payload['mfa_code'] = mfa_token
                res = await request_post(client, url, payload, jsonify_data=False)
            data = await res.json()
        elif 'challenge' in data:
            challenge_id = data['challenge']['id']
            sms_code = input('Enter Robinhood code for validation: ')
            res = await respond_to_challenge(client, challenge_id, sms_code)
            while 'challenge' in res and res['challenge']['remaining_attempts'] > 0:
                sms_code = input('That code was not correct. {0} tries remaining. Please type in another code: '.format(
                    res['challenge']['remaining_attempts']))
                res = await respond_to_challenge(client, challenge_id, sms_code)
            client.update_session(
                'X-ROBINHOOD-CHALLENGE-RESPONSE-ID', challenge_id)
            data = await request_post(client, url, payload)
        # Update Session data with authorization or raise exception with the information present in data.
        if 'access_token' in data:
            token = '{0} {1}'.format(data['token_type'], data['access_token'])
            client.update_session('Authorization', token)
            client.set_login_state(True)
            data['detail'] = "logged in with brand new authentication code."
            if store_session:
                async with aiofiles.open(pickle_path, 'wb') as f:
                    await f.write(pickle.dumps({'token_type': data['token_type'],
                                                'access_token': data['access_token'],
                                                'refresh_token': data['refresh_token'],
                                                'device_token': payload['device_token']}))
        else:
            raise Exception(data['detail'])
    else:
        raise Exception('Error: Trouble connecting to robinhood API. Check internet connection.')
    return data


@login_required
async def logout(client):
    """Removes authorization from the session header.

    :returns: None

    """
    client.set_login_state(False)
    client.update_session('Authorization', None)
    await client.SESSION.close()
