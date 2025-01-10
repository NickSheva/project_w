from currency_exchange import converter

# Initialize the library
currency_client = converter.CurrencyConverter()

# Get the supported currency rates
all_currencies = currency_client.currencies()
print(f"All supported currencies: {all_currencies}")

# Check support of specific currency rate
# NOTE: currency code are case-insensitive
currency = currency_client.currencies('rub')
print(f"Currency name: {currency}")

currency = currency_client.currencies("RUB")
print(f"Currency name: {currency}")

# Get exchange rate between two currencies
# NOTE: currency codes are case-insensitive
rate = currency_client.get_exchange_rate('USD', 'RUB')
print(f"USD to RUS rate: {rate}")

rate = currency_client.get_exchange_rate('usd', 'rub')
print(f"USD to RUB rate: {rate}")

# Get historical exchange rate between two currencies for particular date
# NOTE: currency codes are case-insensitive
currency_client.currency_date = "2024-10-20"
historical_rate = currency_client.get_exchange_rate("USD", "RUB")
print(f"USD to RUB rate at {currency_client.currency_date}: {historical_rate}")

# Convert currencies based on latest rates
# NOTE: currency codes are case-insensitive
currency_convert = currency_client.convert(2400, 'usd', 'rub')
print(f"Convert USD to RUB: {currency_convert}")

# Convert currencies by rates based on historical data
# NOTE: currency codes are case-insensitive
currency_client.currency_date = '2024-11-20'
currency_convert = currency_client.convert(2400, 'usd', 'rub')
print(f"Converting USD to RUB at {currency_client.currency_date} date: {currency_convert}")