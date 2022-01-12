
rcParams = {
    # The date format to display datetimes when printed
    "display.date_format": "%Y/%m/%d %H:%M:%S %z",

    # Units to express the amounts when printed
    "currency.unit": "NANO",

    # Interval in seconds for cleaning up unreferenced accounts from the cache of network.accounts
    "accounts.cache.cleanup_interval_seconds": 100,

    # Interval in seconds to purge expired keys from the cache
    "global.cache.expiration_interval_seconds": 100,

    # Number of seconds to consider a timeout when requesting with requests module
    "requests.timeout": 5,
}
