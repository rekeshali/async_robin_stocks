"""Contains functions for getting market level data."""
import robin_stocks.helper as helper
import robin_stocks.urls as urls
import robin_stocks.stocks as stocks

def get_top_movers_sp500(direction, info=None):
    """Returns a list of the top S&P500 movers up or down for the day.

    :param direction: The direction of movement either 'up' or 'down'
    :type direction: str
    :param info: Will filter the results to get a specific value.
    :type info: Optional[str]
    :returns: Returns a list of dictionaries of key/value pairs for each mover. If info parameter is provided, \
    a list of strings is returned where the strings are the value of the key that matches info.
    :Dictionary Keys: * instrument_url
                      * symbol
                      * updated_at
                      * price_movement
                      * description

    """
    try:
        direction = direction.lower().strip()
    except AttributeError as message:
        print(message)
        return None

    if (direction != 'up' and direction != 'down'):
        print('Error: direction must be "up" or "down"')
        return([None])

    url = urls.movers_sp500()
    payload = {'direction': direction}
    data = helper.request_get(url, 'pagination', payload)

    return(helper.filter(data, info))

def get_top_movers(info=None):
    """Returns a list of the Top 20 movers on Robin Hood.

    :type info: Optional[str]
    :returns: Returns a list of dictionaries of key/value pairs for each mover. If info parameter is provided, \
    a list of strings is returned where the strings are the value of the key that matches info.
    :Dictionary Keys: * ask_price
                      * ask_size
                      * bid_price
                      * bid_size
                      * last_trade_price
                      * last_extended_hours_trade_price
                      * previous_close
                      * adjusted_previous_close
                      * previous_close_date
                      * symbol
                      * trading_halted
                      * has_traded
                      * last_trade_price_source
                      * updated_at
                      * instrument

    """
    url = urls.movers_top()
    data = helper.request_get(url, 'regular')
    data = helper.filter(data, 'instruments')

    symbols = [stocks.get_symbol_by_url(x) for x in data]
    data = stocks.get_quotes(symbols)

    return(helper.filter(data, info))


def get_markets(info=None):
    """Returns a list of available markets.

    :param info: Will filter the results to get a specific value.
    :type info: Optional[str]
    :returns: Returns a list of dictionaries of key/value pairs for each market. If info parameter is provided, \
    a list of strings is returned where the strings are the value of the key that matches info.

    """
    url = urls.markets()
    data = helper.request_get(url, 'pagination')
    return(helper.filter(data, info))


def get_currency_pairs(info=None):
    """Returns currency pairs

    :param info: Will filter the results to get a specific value.
    :type info: Optional[str]
    :returns: Returns a list of dictionaries of key/value pairs for each currency pair. If info parameter is provided, \
    a list of strings is returned where the strings are the value of the key that matches info.

    """

    url = urls.currency()
    data = helper.request_get(url, 'results')
    return(helper.filter(data, info))
