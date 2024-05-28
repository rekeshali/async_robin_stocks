import aiohttp
import logging
import asyncio
from aiologger import Logger
from aiologger.handlers.streams import AsyncStreamHandler
from aiologger.formatters.base import Formatter

from .account import (build_holdings, build_user_profile,
                      delete_symbols_from_watchlist,
                      deposit_funds_to_robinhood_account,
                      download_all_documents, download_document,
                      get_all_positions, get_all_watchlists,
                      get_bank_account_info, get_bank_transfers,
                      get_card_transactions, get_day_trades, get_dividends,
                      get_dividends_by_instrument, get_documents,
                      get_historical_portfolio, get_latest_notification,
                      get_linked_bank_accounts, get_margin_calls,
                      get_margin_interest, get_notifications,
                      get_open_stock_positions, get_referrals,
                      get_stock_loan_payments, get_subscription_fees,
                      get_total_dividends, get_watchlist_by_name,
                      get_wire_transfers, load_phoenix_account,
                      post_symbols_to_watchlist, unlink_bank_account,
                      withdrawl_funds_to_bank_account)
from .authentication import login, logout
from .crypto import (get_crypto_currency_pairs, get_crypto_historicals,
                     get_crypto_info, get_crypto_positions, get_crypto_quote,
                     get_crypto_quote_from_id, load_crypto_profile)
from .export import (export_completed_crypto_orders,
                     export_completed_option_orders,
                     export_completed_stock_orders)
from .helper import (filter_data, request_delete, request_document,
                     request_get, request_post)
from .markets import (get_all_stocks_from_market_tag, get_currency_pairs,
                      get_market_hours, get_market_next_open_hours,
                      get_market_next_open_hours_after_date,
                      get_market_today_hours, get_markets, get_top_100,
                      get_top_movers, get_top_movers_sp500)
from .options import (find_options_by_expiration,
                      find_options_by_expiration_and_strike,
                      find_options_by_specific_profitability,
                      find_options_by_strike, find_tradable_options,
                      get_aggregate_open_positions,
                      get_aggregate_positions, get_all_option_positions,
                      get_chains, get_market_options,
                      get_open_option_positions, get_option_historicals,
                      get_option_instrument_data,
                      get_option_instrument_data_by_id, get_option_market_data,
                      get_option_market_data_by_id)
from .orders import (cancel_all_crypto_orders, cancel_all_option_orders,
                     cancel_all_stock_orders, cancel_crypto_order,
                     cancel_option_order, cancel_stock_order,
                     find_stock_orders, get_all_crypto_orders,
                     get_all_open_crypto_orders, get_all_open_option_orders,
                     get_all_open_stock_orders, get_all_option_orders,
                     get_all_stock_orders, get_crypto_order_info,
                     get_option_order_info, get_stock_order_info, order,
                     order_buy_crypto_by_price, order_buy_crypto_by_quantity,
                     order_buy_crypto_limit, order_buy_crypto_limit_by_price,
                     order_buy_fractional_by_price,
                     order_buy_fractional_by_quantity, order_buy_limit,
                     order_buy_market, order_buy_option_limit,
                     order_buy_option_stop_limit, order_buy_stop_limit,
                     order_buy_stop_loss, order_buy_trailing_stop,
                     order_crypto, order_option_credit_spread,
                     order_option_debit_spread, order_option_spread,
                     order_sell_crypto_by_price, order_sell_crypto_by_quantity,
                     order_sell_crypto_limit, order_sell_crypto_limit_by_price,
                     order_sell_fractional_by_price,
                     order_sell_fractional_by_quantity, order_sell_limit,
                     order_sell_market, order_sell_option_limit,
                     order_sell_option_stop_limit, order_sell_stop_limit,
                     order_sell_stop_loss, order_sell_trailing_stop)
from .profiles import (load_account_profile, load_basic_profile,
                       load_investment_profile, load_portfolio_profile,
                       load_security_profile, load_user_profile)
from .stocks import (find_instrument_data, get_earnings, get_events,
                     get_fundamentals, get_instrument_by_url,
                     get_instruments_by_symbols, get_latest_price,
                     get_name_by_symbol, get_name_by_url, get_news,
                     get_pricebook_by_id, get_pricebook_by_symbol, get_quotes,
                     get_ratings, get_splits, get_stock_historicals,
                     get_stock_quote_by_id, get_stock_quote_by_symbol,
                     get_symbol_by_url)

class LogFormatter(Formatter):
    def format(self, record):
        log_level = record.levelname
        message = record.msg
        return f"[{log_level}] {message}"

class AsyncIORobinStocksClient:
    LOGGED_IN = False

    # Initial headers for the session
    HEADERS = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate,br",
        "Accept-Language": "en-US,en;q=1",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "X-Robinhood-API-Version": "1.431.4",
        "Connection": "keep-alive",
        "User-Agent": "*"
    }

    def __init__(self, logger=None, log_level=logging.INFO):
        self.logger = logger if logger else self._async_robin_stocks_logger(log_level)
        self.SESSION = aiohttp.ClientSession(headers=self.HEADERS)

    async def close(self):
        await self.SESSION.close()
    
    def _async_robin_stocks_logger(self, log_level):
        logger = Logger(name="async-robin-stocks-client-logger", level=log_level)
        
        # Adding a file handler with a custom formatter
        stream_handler = AsyncStreamHandler()
        custom_formatter = LogFormatter()
        stream_handler.formatter = custom_formatter
        
        # Add the custom handler to the logger
        logger.add_handler(stream_handler)
        
        return logger
    
    def set_login_state(self, logged_in):
        """Sets the login state"""
        self.LOGGED_IN = logged_in

    def update_session(self, key, value):
        """Updates the session header used by the aiohttp library.

        :param key: The key value to update or add to session header.
        :type key: str
        :param value: The value that corresponds to the key.
        :type value: str
        :returns: None. Updates the session header with a value.
        """
        self.HEADERS[key] = str(value)

    async def login(self, *args, **kwargs):
        return await login(self, *args, **kwargs)
    

    async def logout(self, *args, **kwargs):
        return await logout(self, *args, **kwargs)


    async def build_holdings(self, *args, **kwargs):
        return await build_holdings(self, *args, **kwargs)
    

    async def build_user_profile(self, *args, **kwargs):
        return await build_user_profile(self, *args, **kwargs)
    

    async def delete_symbols_from_watchlist(self, *args, **kwargs):
        return await delete_symbols_from_watchlist(self, *args, **kwargs)
    

    async def deposit_funds_to_robinhood_account(self, *args, **kwargs):
        return await deposit_funds_to_robinhood_account(self, *args, **kwargs)
    

    async def download_all_documents(self, *args, **kwargs):
        return await download_all_documents(self, *args, **kwargs)
    

    async def download_document(self, *args, **kwargs):
        return await download_document(self, *args, **kwargs)
    

    async def get_all_positions(self, *args, **kwargs):
        return await get_all_positions(self, *args, **kwargs)
    

    async def get_all_watchlists(self, *args, **kwargs):
        return await get_all_watchlists(self, *args, **kwargs)
    

    async def get_bank_account_info(self, *args, **kwargs):
        return await get_bank_account_info(self, *args, **kwargs)
    

    async def get_bank_transfers(self, *args, **kwargs):
        return await get_bank_transfers(self, *args, **kwargs)
    

    async def get_card_transactions(self, *args, **kwargs):
        return await get_card_transactions(self, *args, **kwargs)
    

    async def get_day_trades(self, *args, **kwargs):
        return await get_day_trades(self, *args, **kwargs)
    

    async def get_dividends(self, *args, **kwargs):
        return await get_dividends(self, *args, **kwargs)
    

    async def get_dividends_by_instrument(self, *args, **kwargs):
        return await get_dividends_by_instrument(self, *args, **kwargs)
    

    async def get_documents(self, *args, **kwargs):
        return await get_documents(self, *args, **kwargs)
    

    async def get_historical_portfolio(self, *args, **kwargs):
        return await get_historical_portfolio(self, *args, **kwargs)
    

    async def get_latest_notification(self, *args, **kwargs):
        return await get_latest_notification(self, *args, **kwargs)
    

    async def get_linked_bank_accounts(self, *args, **kwargs):
        return await get_linked_bank_accounts(self, *args, **kwargs)
    

    async def get_margin_calls(self, *args, **kwargs):
        return await get_margin_calls(self, *args, **kwargs)
    

    async def get_margin_interest(self, *args, **kwargs):
        return await get_margin_interest(self, *args, **kwargs)
    

    async def get_notifications(self, *args, **kwargs):
        return await get_notifications(self, *args, **kwargs)
    

    async def get_open_stock_positions(self, *args, **kwargs):
        return await get_open_stock_positions(self, *args, **kwargs)
    

    async def get_referrals(self, *args, **kwargs):
        return await get_referrals(self, *args, **kwargs)
    

    async def get_stock_loan_payments(self, *args, **kwargs):
        return await get_stock_loan_payments(self, *args, **kwargs)
    

    async def get_subscription_fees(self, *args, **kwargs):
        return await get_subscription_fees(self, *args, **kwargs)
    

    async def get_total_dividends(self, *args, **kwargs):
        return await get_total_dividends(self, *args, **kwargs)
    

    async def get_watchlist_by_name(self, *args, **kwargs):
        return await get_watchlist_by_name(self, *args, **kwargs)
    

    async def get_wire_transfers(self, *args, **kwargs):
        return await get_wire_transfers(self, *args, **kwargs)
    

    async def load_phoenix_account(self, *args, **kwargs):
        return await load_phoenix_account(self, *args, **kwargs)
    

    async def post_symbols_to_watchlist(self, *args, **kwargs):
        return await post_symbols_to_watchlist(self, *args, **kwargs)
    

    async def unlink_bank_account(self, *args, **kwargs):
        return await unlink_bank_account(self, *args, **kwargs)
    

    async def withdrawl_funds_to_bank_account(self, *args, **kwargs):
        return await withdrawl_funds_to_bank_account(self, *args, **kwargs)
    

    async def get_crypto_currency_pairs(self, *args, **kwargs):
        return await get_crypto_currency_pairs(self, *args, **kwargs)
    

    async def get_crypto_historicals(self, *args, **kwargs):
        return await get_crypto_historicals(self, *args, **kwargs)
    

    async def get_crypto_info(self, *args, **kwargs):
        return await get_crypto_info(self, *args, **kwargs)
    

    async def get_crypto_positions(self, *args, **kwargs):
        return await get_crypto_positions(self, *args, **kwargs)
    

    async def get_crypto_quote(self, *args, **kwargs):
        return await get_crypto_quote(self, *args, **kwargs)
    

    async def get_crypto_quote_from_id(self, *args, **kwargs):
        return await get_crypto_quote_from_id(self, *args, **kwargs)
    

    async def load_crypto_profile(self, *args, **kwargs):
        return await load_crypto_profile(self, *args, **kwargs)
    

    async def export_completed_crypto_orders(self, *args, **kwargs):
        return await export_completed_crypto_orders(self, *args, **kwargs)
    

    async def export_completed_option_orders(self, *args, **kwargs):
        return await export_completed_option_orders(self, *args, **kwargs)
    

    async def export_completed_stock_orders(self, *args, **kwargs):
        return await export_completed_stock_orders(self, *args, **kwargs)
    

    async def filter_data(self, *args, **kwargs):
        return await filter_data(self, *args, **kwargs)
    

    async def request_delete(self, *args, **kwargs):
        return await request_delete(self, *args, **kwargs)
    

    async def request_document(self, *args, **kwargs):
        return await request_document(self, *args, **kwargs)
    

    async def request_get(self, *args, **kwargs):
        return await request_get(self, *args, **kwargs)
    

    async def request_post(self, *args, **kwargs):
        return await request_post(self, *args, **kwargs)
    

    async def get_all_stocks_from_market_tag(self, *args, **kwargs):
        return await get_all_stocks_from_market_tag(self, *args, **kwargs)
    

    async def get_currency_pairs(self, *args, **kwargs):
        return await get_currency_pairs(self, *args, **kwargs)
    

    async def get_market_hours(self, *args, **kwargs):
        return await get_market_hours(self, *args, **kwargs)
    

    async def get_market_next_open_hours(self, *args, **kwargs):
        return await get_market_next_open_hours(self, *args, **kwargs)
    

    async def get_market_next_open_hours_after_date(self, *args, **kwargs):
        return await get_market_next_open_hours_after_date(self, *args, **kwargs)
    

    async def get_market_today_hours(self, *args, **kwargs):
        return await get_market_today_hours(self, *args, **kwargs)
    

    async def get_markets(self, *args, **kwargs):
        return await get_markets(self, *args, **kwargs)
    

    async def get_top_100(self, *args, **kwargs):
        return await get_top_100(self, *args, **kwargs)
    

    async def get_top_movers(self, *args, **kwargs):
        return await get_top_movers(self, *args, **kwargs)
    

    async def get_top_movers_sp500(self, *args, **kwargs):
        return await get_top_movers_sp500(self, *args, **kwargs)
    

    async def find_options_by_expiration(self, *args, **kwargs):
        return await find_options_by_expiration(self, *args, **kwargs)
    

    async def find_options_by_expiration_and_strike(self, *args, **kwargs):
        return await find_options_by_expiration_and_strike(self, *args, **kwargs)
    

    async def find_options_by_specific_profitability(self, *args, **kwargs):
        return await find_options_by_specific_profitability(self, *args, **kwargs)
    

    async def find_options_by_strike(self, *args, **kwargs):
        return await find_options_by_strike(self, *args, **kwargs)
    

    async def find_tradable_options(self, *args, **kwargs):
        return await find_tradable_options(self, *args, **kwargs)
    

    async def get_aggregate_open_positions(self, *args, **kwargs):
        return await get_aggregate_open_positions(self, *args, **kwargs)
    

    async def get_aggregate_positions(self, *args, **kwargs):
        return await get_aggregate_positions(self, *args, **kwargs)
    

    async def get_all_option_positions(self, *args, **kwargs):
        return await get_all_option_positions(self, *args, **kwargs)
    

    async def get_chains(self, *args, **kwargs):
        return await get_chains(self, *args, **kwargs)
    

    async def get_market_options(self, *args, **kwargs):
        return await get_market_options(self, *args, **kwargs)
    

    async def get_open_option_positions(self, *args, **kwargs):
        return await get_open_option_positions(self, *args, **kwargs)
    

    async def get_option_historicals(self, *args, **kwargs):
        return await get_option_historicals(self, *args, **kwargs)
    

    async def get_option_instrument_data(self, *args, **kwargs):
        return await get_option_instrument_data(self, *args, **kwargs)
    

    async def get_option_instrument_data_by_id(self, *args, **kwargs):
        return await get_option_instrument_data_by_id(self, *args, **kwargs)
    

    async def get_option_market_data(self, *args, **kwargs):
        return await get_option_market_data(self, *args, **kwargs)
    

    async def get_option_market_data_by_id(self, *args, **kwargs):
        return await get_option_market_data_by_id(self, *args, **kwargs)
    

    async def cancel_all_crypto_orders(self, *args, **kwargs):
        return await cancel_all_crypto_orders(self, *args, **kwargs)
    

    async def cancel_all_option_orders(self, *args, **kwargs):
        return await cancel_all_option_orders(self, *args, **kwargs)
    

    async def cancel_all_stock_orders(self, *args, **kwargs):
        return await cancel_all_stock_orders(self, *args, **kwargs)
    

    async def cancel_crypto_order(self, *args, **kwargs):
        return await cancel_crypto_order(self, *args, **kwargs)
    

    async def cancel_option_order(self, *args, **kwargs):
        return await cancel_option_order(self, *args, **kwargs)
    

    async def cancel_stock_order(self, *args, **kwargs):
        return await cancel_stock_order(self, *args, **kwargs)
    

    async def find_stock_orders(self, *args, **kwargs):
        return await find_stock_orders(self, *args, **kwargs)
    

    async def get_all_crypto_orders(self, *args, **kwargs):
        return await get_all_crypto_orders(self, *args, **kwargs)
    

    async def get_all_open_crypto_orders(self, *args, **kwargs):
        return await get_all_open_crypto_orders(self, *args, **kwargs)
    

    async def get_all_open_option_orders(self, *args, **kwargs):
        return await get_all_open_option_orders(self, *args, **kwargs)
    

    async def get_all_open_stock_orders(self, *args, **kwargs):
        return await get_all_open_stock_orders(self, *args, **kwargs)
    

    async def get_all_option_orders(self, *args, **kwargs):
        return await get_all_option_orders(self, *args, **kwargs)
    

    async def get_all_stock_orders(self, *args, **kwargs):
        return await get_all_stock_orders(self, *args, **kwargs)
    

    async def get_crypto_order_info(self, *args, **kwargs):
        return await get_crypto_order_info(self, *args, **kwargs)
    

    async def get_option_order_info(self, *args, **kwargs):
        return await get_option_order_info(self, *args, **kwargs)
    

    async def get_stock_order_info(self, *args, **kwargs):
        return await get_stock_order_info(self, *args, **kwargs)
    

    async def order(self, *args, **kwargs):
        return await order(self, *args, **kwargs)
    

    async def order_buy_crypto_by_price(self, *args, **kwargs):
        return await order_buy_crypto_by_price(self, *args, **kwargs)
    

    async def order_buy_crypto_by_quantity(self, *args, **kwargs):
        return await order_buy_crypto_by_quantity(self, *args, **kwargs)
    

    async def order_buy_crypto_limit(self, *args, **kwargs):
        return await order_buy_crypto_limit(self, *args, **kwargs)
    

    async def order_buy_crypto_limit_by_price(self, *args, **kwargs):
        return await order_buy_crypto_limit_by_price(self, *args, **kwargs)
    

    async def order_buy_fractional_by_price(self, *args, **kwargs):
        return await order_buy_fractional_by_price(self, *args, **kwargs)
    

    async def order_buy_fractional_by_quantity(self, *args, **kwargs):
        return await order_buy_fractional_by_quantity(self, *args, **kwargs)
    

    async def order_buy_limit(self, *args, **kwargs):
        return await order_buy_limit(self, *args, **kwargs)
    

    async def order_buy_market(self, *args, **kwargs):
        return await order_buy_market(self, *args, **kwargs)
    

    async def order_buy_option_limit(self, *args, **kwargs):
        return await order_buy_option_limit(self, *args, **kwargs)
    

    async def order_buy_option_stop_limit(self, *args, **kwargs):
        return await order_buy_option_stop_limit(self, *args, **kwargs)
    

    async def order_buy_stop_limit(self, *args, **kwargs):
        return await order_buy_stop_limit(self, *args, **kwargs)
    

    async def order_buy_stop_loss(self, *args, **kwargs):
        return await order_buy_stop_loss(self, *args, **kwargs)
    

    async def order_buy_trailing_stop(self, *args, **kwargs):
        return await order_buy_trailing_stop(self, *args, **kwargs)
    

    async def order_crypto(self, *args, **kwargs):
        return await order_crypto(self, *args, **kwargs)
    

    async def order_option_credit_spread(self, *args, **kwargs):
        return await order_option_credit_spread(self, *args, **kwargs)
    

    async def order_option_debit_spread(self, *args, **kwargs):
        return await order_option_debit_spread(self, *args, **kwargs)
    

    async def order_option_spread(self, *args, **kwargs):
        return await order_option_spread(self, *args, **kwargs)
    

    async def order_sell_crypto_by_price(self, *args, **kwargs):
        return await order_sell_crypto_by_price(self, *args, **kwargs)
    

    async def order_sell_crypto_by_quantity(self, *args, **kwargs):
        return await order_sell_crypto_by_quantity(self, *args, **kwargs)
    

    async def order_sell_crypto_limit(self, *args, **kwargs):
        return await order_sell_crypto_limit(self, *args, **kwargs)
    

    async def order_sell_crypto_limit_by_price(self, *args, **kwargs):
        return await order_sell_crypto_limit_by_price(self, *args, **kwargs)
    

    async def order_sell_fractional_by_price(self, *args, **kwargs):
        return await order_sell_fractional_by_price(self, *args, **kwargs)
    

    async def order_sell_fractional_by_quantity(self, *args, **kwargs):
        return await order_sell_fractional_by_quantity(self, *args, **kwargs)
    

    async def order_sell_limit(self, *args, **kwargs):
        return await order_sell_limit(self, *args, **kwargs)
    

    async def order_sell_market(self, *args, **kwargs):
        return await order_sell_market(self, *args, **kwargs)
    

    async def order_sell_option_limit(self, *args, **kwargs):
        return await order_sell_option_limit(self, *args, **kwargs)
    

    async def order_sell_option_stop_limit(self, *args, **kwargs):
        return await order_sell_option_stop_limit(self, *args, **kwargs)
    

    async def order_sell_stop_limit(self, *args, **kwargs):
        return await order_sell_stop_limit(self, *args, **kwargs)
    

    async def order_sell_stop_loss(self, *args, **kwargs):
        return await order_sell_stop_loss(self, *args, **kwargs)
    

    async def order_sell_trailing_stop(self, *args, **kwargs):
        return await order_sell_trailing_stop(self, *args, **kwargs)
    

    async def load_account_profile(self, *args, **kwargs):
        return await load_account_profile(self, *args, **kwargs)
    

    async def load_basic_profile(self, *args, **kwargs):
        return await load_basic_profile(self, *args, **kwargs)
    

    async def load_investment_profile(self, *args, **kwargs):
        return await load_investment_profile(self, *args, **kwargs)
    

    async def load_portfolio_profile(self, *args, **kwargs):
        return await load_portfolio_profile(self, *args, **kwargs)
    

    async def load_security_profile(self, *args, **kwargs):
        return await load_security_profile(self, *args, **kwargs)
    

    async def load_user_profile(self, *args, **kwargs):
        return await load_user_profile(self, *args, **kwargs)
    

    async def find_instrument_data(self, *args, **kwargs):
        return await find_instrument_data(self, *args, **kwargs)
    

    async def get_earnings(self, *args, **kwargs):
        return await get_earnings(self, *args, **kwargs)
    

    async def get_events(self, *args, **kwargs):
        return await get_events(self, *args, **kwargs)
    

    async def get_fundamentals(self, *args, **kwargs):
        return await get_fundamentals(self, *args, **kwargs)
    

    async def get_instrument_by_url(self, *args, **kwargs):
        return await get_instrument_by_url(self, *args, **kwargs)
    

    async def get_instruments_by_symbols(self, *args, **kwargs):
        return await get_instruments_by_symbols(self, *args, **kwargs)
    

    async def get_latest_price(self, *args, **kwargs):
        return await get_latest_price(self, *args, **kwargs)
    

    async def get_name_by_symbol(self, *args, **kwargs):
        return await get_name_by_symbol(self, *args, **kwargs)
    

    async def get_name_by_url(self, *args, **kwargs):
        return await get_name_by_url(self, *args, **kwargs)
    

    async def get_news(self, *args, **kwargs):
        return await get_news(self, *args, **kwargs)
    

    async def get_pricebook_by_id(self, *args, **kwargs):
        return await get_pricebook_by_id(self, *args, **kwargs)
    

    async def get_pricebook_by_symbol(self, *args, **kwargs):
        return await get_pricebook_by_symbol(self, *args, **kwargs)
    

    async def get_quotes(self, *args, **kwargs):
        return await get_quotes(self, *args, **kwargs)
    

    async def get_ratings(self, *args, **kwargs):
        return await get_ratings(self, *args, **kwargs)
    

    async def get_splits(self, *args, **kwargs):
        return await get_splits(self, *args, **kwargs)
    

    async def get_stock_historicals(self, *args, **kwargs):
        return await get_stock_historicals(self, *args, **kwargs)
    

    async def get_stock_quote_by_id(self, *args, **kwargs):
        return await get_stock_quote_by_id(self, *args, **kwargs)
    

    async def get_stock_quote_by_symbol(self, *args, **kwargs):
        return await get_stock_quote_by_symbol(self, *args, **kwargs)
    

    async def get_symbol_by_url(self, *args, **kwargs):
        return await get_symbol_by_url(self, *args, **kwargs)
    


    
    
