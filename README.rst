.. image:: docs/source/_static/pics/title.PNG

Asynchronous Robin-Stocks API Client
====================================
Blew up your port and unimpressed with the AWS free tier thread count? 
Use async_robin_stocks to manage all your positions concurrently.
(not financial advice)

Serious: This library has been enhanced to support asynchronous operations (only the robinhood part).
No changes have been made to the API itself, just set up the client and call functions as you normally would (+ await).
I have tested many of the stocks, options, and accounts methods and found no issues. 
I have not tested order placing or post requests in general besides logging in.

Key changes include:
All major functions and methods have been refactored to use async and await, enabling non-blocking execution.
The session global has been replaced with a client class that now uses aiohttp for asynchronous HTTP requests.
Logging is handled by aiologger, ensuring that log operations do not block the main event loop.
File I/O utilizes aiofile for asynchronous context (although I've not tested it).

Here is an example that gets data from multiple user accounts concurrently:
.. code-block:: python

    import asyncio
    import logging
    from robin_stocks.robinhood import AsyncIORobinStocksClient
    from robin_stocks.robinhood.helper import requests_get

    async def len_open_positions(user):
        r = AsyncIORobinStocksClient(log_level=logging.DEBUG) # or pass a custom aiologger to 'logger' kwarg here
        try:
            user_name, pickle_name = user
            await r.login(pickle_name=pickle_name)
            await r.logger.info(f"{user_name} has {len(await r.get_open_stock_positions())} open stock positions")

            # Advanced usage API requires you pass the client to it
            advanced_get = await requests_get(r, 'https://robinhood.com/your/favorite/endpoint')

            await r.logout()
        except:
            r.close()

    # Process multiple users concurrently
    async def main():
        users = [("user1", "pickle1"), ("user2", "pickle2"), ("user3", "pickle3")]
        tasks = [main(user) for user in users]
        await asyncio.gather(*tasks)

    if __name__ == "__main__":
        asyncio.run(main())


Also see "examples/robinhood examples/get_option_historicals.py" for another working example.

NOTE: I'm a big fan of this library thanks all who have worked on this. 

WARNING: THIS LIBRARY IS NOT FULLY TESTED USE AT YOUR OWN RISK.

Robin-Stocks API Library
========================
This library provides a pure python interface to interact with the Robinhood API, Gemini API,
and TD Ameritrade API. The code is simple to use, easy to understand, and easy to modify.
With this library you can view information on stocks, options, and crypto-currencies in real time, 
create your own robo-investor or trading algorithm, and improve your programming skills.

To join our Slack channel where you can discuss trading and coding, click the link https://join.slack.com/t/robin-stocks/shared_invite/zt-7up2htza-wNSil5YDa3zrAglFFSxRIA

Supported APIs
==============
The supported APIs are Robinhood, Gemini, and TD Ameritrade. For more information about how to use the different APIs, visit the README
documents for `Robinhood Documentation`_, `Gemini Documentation`_, and `TDA Documentation`_.

Below are examples on how to call each of those modules.

>>> import robin_stocks.robinhood as rh
>>> import robin_stocks.gemini as gem
>>> import robin_stocks.tda as tda
>>> # Here are some example calls
>>> gem.get_pubticker("btcusd") # gets ticker information for Bitcoin from Gemini
>>> rh.get_all_open_crypto_orders() # gets all cypto orders from Robinhood
>>> tda.get_price_history("tsla") # get price history from TD Ameritrade 

Contributing
============
If you would like to contribute to this project, follow our contributing guidelines `Here <https://github.com/jmfernandes/robin_stocks/blob/master/contributing.md>`_.

Automatic Testing
^^^^^^^^^^^^^^^^^

If you are contributing to this project and would like to use automatic testing for your changes, you will need to install pytest and pytest-dotenv. To do this type into terminal or command prompt:

>>> pip install pytest
>>> pip install pytest-dotenv

You will also need to fill out all the fields in .test.env. I recommend that you rename the file as .env once you are done adding in all your personal information. After that, you can simply run:

>>> pytest

to run all the tests. If you would like to run specific tests or run all the tests in a specific class then type:

>>> pytest tests/test_robinhood.py -k test_name_apple # runs only the 1 test
>>> pytest tests/test_gemini.py -k TestTrades # runs every test in TestTrades but nothing else

Finally, if you would like the API calls to print out to terminal, then add the -s flag to any of the above pytest calls.


Installing
========================
There is no need to download these files directly. This project is published on PyPi,
so it can be installed by typing into terminal (on Mac) or into command prompt (on PC):

>>> pip install robin_stocks

Also be sure that Python 3 is installed. If you need to install python you can download it from `Python.org <https://www.python.org/downloads/>`_.
Pip is the package installer for python, and is automatically installed when you install python. To learn more about Pip, you can go to `PyPi.org <https://pypi.org/project/pip/>`_.

If you would like to be able to make changes to the package yourself, clone the repository onto your computer by typing into terminal or command prompt:

>>> git clone https://github.com/jmfernandes/robin_stocks.git
>>> cd robin_stocks

Now that you have cd into the repository you can type

>>> pip install .

and this will install whatever you changed in the local files. This will allow you to make changes and experiment with your own code.

List of Functions and Example Usage
===================================

For a complete list of all Robinhood API functions and what the different parameters mean, 
go to `robin-stocks.com Robinhood Page <http://www.robin-stocks.com/en/latest/robinhood.html>`_. If you would like to
see some example code and instructions on how to set up two-factor authorization for Robinhood,
go to the `Robinhood Documentation`_.

For a complete list of all TD Ameritrade API functions and what the different parameters mean, 
go to `robin-stocks.com TDA Page <http://www.robin-stocks.com/en/latest/tda.html>`_. For detailed instructions on 
how to generate API keys for TD Ameritrade and how to use the API, go to the `TDA Documentation`_.

For a complete list of all Gemini API functions and what the different parameters mean, 
go to `robin-stocks.com Gemeni Page <http://www.robin-stocks.com/en/latest/gemini.html>`_. For detailed instructions on 
how to generate API keys for Gemini and how to use both the private and public API, go to the `Gemini Documentation`_.

.. _Robinhood Documentation: Robinhood.rst
.. _Gemini Documentation: gemini.rst
.. _TDA Documentation: tda.rst