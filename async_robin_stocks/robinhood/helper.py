"""Contains decorator functions and functions for interacting with global data.
"""
from functools import wraps
import aiohttp

def login_required(func):
    """A decorator for indicating which methods require the user to be logged
       in."""
    @wraps(func)
    def login_wrapper(*args, **kwargs):
        client = args[0]
        if not client.LOGGED_IN:
            raise Exception('{} can only be called when logged in'.format(
                func.__name__))
        return(func(*args, **kwargs))
    return(login_wrapper)


def convert_none_to_string(func):
    """A decorator for converting a None Type into a blank string"""
    @wraps(func)
    def string_wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if result:
            return(result)
        else:
            return("")
    return(string_wrapper)


async def id_for_stock(client, symbol):
    """Takes a stock ticker and returns the instrument id associated with the stock.

    :param symbol: The symbol to get the id for.
    :type symbol: str
    :returns:  A string that represents the stocks instrument id.

    """
    try:
        symbol = symbol.upper().strip()
    except AttributeError as message:
        await client.logger.error(message)
        return(None)

    url = 'https://api.robinhood.com/instruments/'
    payload = {'symbol': symbol}
    data = await request_get(client, url, 'indexzero', payload)

    return(await filter_data(client, data, 'id'))


async def id_for_chain(client, symbol):
    """Takes a stock ticker and returns the chain id associated with a stock's option.

    :param symbol: The symbol to get the id for.
    :type symbol: str
    :returns: A string that represents the stock's options chain id.
    """
    try:
        symbol = symbol.upper().strip()
    except AttributeError as message:
        await client.logger.error(message)
        return None

    url = 'https://api.robinhood.com/instruments/'
    payload = {'symbol': symbol}
    data = await request_get(client, url, 'indexzero', payload)

    if data:
        return data['tradable_chain_id']
    else:
        return data


async def id_for_group(client, symbol):
    """Takes a stock ticker and returns the id associated with the group.

    :param symbol: The symbol to get the id for.
    :type symbol: str
    :returns: A string that represents the stock's group id.
    """
    try:
        symbol = symbol.upper().strip()
    except AttributeError as message:
        await client.logger.error(message)
        return None

    url = 'https://api.robinhood.com/options/chains/{0}/'.format(await id_for_chain(client, symbol))
    data = await request_get(client, url)
    return data['underlying_instruments'][0]['id']


async def id_for_option(client, symbol, expirationDate, strike, optionType):
    """Returns the id associated with a specific option order.

    :param symbol: The symbol to get the id for.
    :type symbol: str
    :param expirationData: The expiration date as YYYY-MM-DD
    :type expirationData: str
    :param strike: The strike price.
    :type strike: str
    :param optionType: Either call or put.
    :type optionType: str
    :returns: A string that represents the stock's option id.
    """ 
    symbol = symbol.upper()
    chain_id = await id_for_chain(client, symbol)
    payload = {
        'chain_id': chain_id,
        'expiration_dates': expirationDate,
        'strike_price': strike,
        'type': optionType,
        'state': 'active'
    }
    url = 'https://api.robinhood.com/options/instruments/'
    data = await request_get(client, url, 'pagination', payload)

    listOfOptions = [item for item in data if item["expiration_date"] == expirationDate]
    if len(listOfOptions) == 0:
        await client.logger.warning('Getting the option ID failed. Perhaps the expiration date is wrong format, or the strike price is wrong.')
        return None

    return listOfOptions[0]['id']


def round_price(price):
    """Takes a price and rounds it to an appropriate decimal place that Robinhood will accept.

    :param price: The input price to round.
    :type price: float or int
    :returns: The rounded price as a float.

    """
    price = float(price)
    if price <= 1e-2:
        returnPrice = round(price, 6)
    elif price < 1e0:
        returnPrice = round(price, 4)
    else:
        returnPrice = round(price, 2)

    return returnPrice


async def filter_data(client, data, info):
    """Takes the data and extracts the value for the keyword that matches info.

    :param data: The data returned by request_get.
    :type data: dict or list
    :param info: The keyword to filter from the data.
    :type info: str
    :returns:  A list or string with the values that correspond to the info keyword.

    """
    if (data == None):
        return(data)
    elif (data == [None]):
        return([])
    elif (type(data) == list):
        if (len(data) == 0):
            return([])
        compareDict = data[0]
        noneType = []
    elif (type(data) == dict):
        compareDict = data
        noneType = None

    if info is not None:
        if info in compareDict and type(data) == list:
            return([x[info] for x in data])
        elif info in compareDict and type(data) == dict:
            return(data[info])
        else:
            await client.logger.warning(error_argument_not_key_in_dictionary(info))
            return(noneType)
    else:
        return(data)


def inputs_to_set(inputSymbols):
    """Takes in the parameters passed to *args and puts them in a set and a list.
    The set will make sure there are no duplicates, and then the list will keep
    the original order of the input.

    :param inputSymbols: A list, dict, or tuple of stock tickers.
    :type inputSymbols: list or dict or tuple or str
    :returns:  A list of strings that have been capitalized and stripped of white space.

    """

    symbols_list = []
    symbols_set = set()

    def add_symbol(symbol):
        symbol = symbol.upper().strip()
        if symbol not in symbols_set:
            symbols_set.add(symbol)
            symbols_list.append(symbol)

    if type(inputSymbols) is str:
        add_symbol(inputSymbols)
    elif type(inputSymbols) is list or type(inputSymbols) is tuple or type(inputSymbols) is set:
        inputSymbols = [comp for comp in inputSymbols if type(comp) is str]
        for item in inputSymbols:
            add_symbol(item)

    return(symbols_list)


async def request_document(client, url, payload=None):
    """Using a document url, makes a get request and returns the session data.

    :param url: The url to send a get request to.
    :type url: str
    :returns: Returns the session.get() data as opposed to session.get().json() data.
    """
    try:
        async with client.SESSION.get(url, params=payload, headers=client.HEADERS) as res:
            res.raise_for_status()
    except aiohttp.ClientResponseError as message:
        await client.logger.error(message)
        return None

    return res


async def request_get(client, url, dataType='regular', payload=None, jsonify_data=True):
    """For a given url and payload, makes a get request and returns the data.

    :param url: The url to send a get request to.
    :type url: str
    :param dataType: Determines how to filter the data. 'regular' returns the unfiltered data. \
    'results' will return data['results']. 'pagination' will return data['results'] and append it with any \
    data that is in data['next']. 'indexzero' will return data['results'][0].
    :type dataType: Optional[str]
    :param payload: Dictionary of parameters to pass to the url. Will append the requests url as url/?key1=value1&key2=value2.
    :type payload: Optional[dict]
    :param jsonify_data: If this is true, will return requests.post().json(), otherwise will return response from requests.post().
    :type jsonify_data: bool
    :returns: Returns the data from the get request. If jsonify_data=True and requests returns an http code other than <200> \
    then either '[None]' or 'None' will be returned based on what the dataType parameter was set as.
    """
    if (dataType == 'results' or dataType == 'pagination'):
        data = [None]
    else:
        data = None
    res = None
    if jsonify_data:
        try:
            async with client.SESSION.get(url, params=payload, headers=client.HEADERS) as res:
                res.raise_for_status()
                data = await res.json()
        except (aiohttp.ClientResponseError, AttributeError) as message:
            await client.logger.error(message)
            return(data)
    else:
        async with client.SESSION.get(url, params=payload, headers=client.HEADERS) as res:
            return res

    # Only continue to filter data if jsonify_data=True, and client.SESSION.get returned status code <200>.
    if (dataType == 'results'):
        try:
            data = data['results']
        except KeyError as message:
            await client.logger.error("{0} is not a key in the dictionary".format(message))
            return([None])
    elif (dataType == 'pagination'):
        counter = 2
        nextData = data
        try:
            data = data['results']
        except KeyError as message:
            await client.logger.error("{0} is not a key in the dictionary".format(message))
            return([None])

        if nextData['next']:
            await client.logger.debug('Found Additional pages.')
        while nextData['next']:
            try:
                async with client.SESSION.get(nextData['next'], headers=client.HEADERS) as res:
                    res.raise_for_status()
                    nextData = await res.json()
            except:
                await client.logger.warning('Additional pages exist but could not be loaded.')
                return(data)
            await client.logger.debug('Loading page '+str(counter)+' ...')
            counter += 1
            for item in nextData['results']:
                data.append(item)
    elif (dataType == 'indexzero'):
        try:
            data = data['results'][0]
        except KeyError as message:
            await client.logger.error("{0} is not a key in the dictionary".format(message))
            return(None)
        except IndexError as message:
            return(None)

    return(data)


async def request_post(client, url, payload=None, timeout=16, json=False, jsonify_data=True):
    """For a given url and payload, makes a post request and returns the response. Allows for responses other than 200.

    :param url: The url to send a post request to.
    :type url: str
    :param payload: Dictionary of parameters to pass to the url as url/?key1=value1&key2=value2.
    :type payload: Optional[dict]
    :param timeout: The time for the post to wait for a response. Should be slightly greater than multiples of 3.
    :type timeout: Optional[int]
    :param json: This will set the 'content-type' parameter of the session header to 'application/json'
    :type json: bool
    :param jsonify_data: If this is true, will return requests.post().json(), otherwise will return response from requests.post().
    :type jsonify_data: bool
    :returns: Returns the data from the post request.

    """
    data = None
    res = None
    try:
        if json:
            client.update_session('Content-Type', 'application/json')
            async with client.SESSION.post(url, json=payload, timeout=timeout, headers=client.HEADERS) as res:
                client.update_session('Content-Type', 'application/x-www-form-urlencoded; charset=utf-8')
                if res.status not in [200, 201, 202, 204, 301, 302, 303, 304, 307, 400, 401, 402, 403]:
                    raise Exception("Received " + str(res.status))
                data = await res.json()     
        else:
            async with client.SESSION.post(url, data=payload, timeout=timeout, headers=client.HEADERS) as res:
                if res.status not in [200, 201, 202, 204, 301, 302, 303, 304, 307, 400, 401, 402, 403]:
                    raise Exception("Received " + str(res.status))
                data = await res.json()            

    except Exception as message:
        await client.logger.error("Error in request_post: {0}".format(message))
        
    if jsonify_data:
        return data
    else:
        return res


async def request_delete(client, url):
    """For a given url, makes a delete request and returns the response.

    :param url: The url to send a delete request to.
    :type url: str
    :returns: Returns the data from the delete request.

    """
    try:
        async with client.SESSION.delete(url, headers=client.HEADERS) as res:
            res.raise_for_status()
            data = await res.json()
    except Exception as message:
        data = None
        await client.logger.error(f"Error in request_delete: {message}")
        
    return data


def error_argument_not_key_in_dictionary(keyword):
    return('The keyword "{0}" is not a key in the dictionary.'.format(keyword))


def error_ticker_does_not_exist(ticker):
    return('"{0}" is not a valid stock ticker. It is being ignored'.format(ticker))


def error_must_be_nonzero(keyword):
    return('The input parameter "{0}" must be an integer larger than zero and non-negative'.format(keyword))
