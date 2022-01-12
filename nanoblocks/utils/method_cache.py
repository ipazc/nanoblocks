"""
This is a decorator for methods that caches the output for a given time.
This means that following calls to the method will output the same value for a certain number of seconds,
without executing again the method itself, until the time threshold is met.

This is useful when dealing with expensive calls, like for example querying a node.
"""
from nanoblocks import rcParams
from nanoblocks.utils import TimedVariable


def clear_expired_keys(cachemod_dict, counter_expiration_key="___expiration_counter___"):
    """
    Checks for expired keys and clears them from the cache.
    The cache must contain TimedVariable values in order to be cleared.

    :param cachemod_dict:
        Cache dictionary to explore for expired keys. Its values must be of type TimedVariable.

    :param counter_expiration_key:
        Name of the key to store expiration date.
        A global counter is stored in the cache (under this key name) that contains a global timestamp of the last
        clear_expired_keys() execution. This allows the function to know when to clear again.

    :return:
        Clean cache dictionary (without expired keys).
    """

    counter = cachemod_dict.get(counter_expiration_key)

    if counter is None:
        counter = TimedVariable(None)
        cachemod_dict[counter_expiration_key] = counter

    cache_expiration_time = rcParams["global.cache.expiration_interval_seconds"]

    if counter.last_update_elapsed_time >= cache_expiration_time:
        counter.refresh()

        # Here we clear the cache dictionary from expired keys.
        cachemod_dict = {k: v for k, v in cachemod_dict.items()
                         if v.last_update_elapsed_time < cache_expiration_time and k != counter_expiration_key}

    return cachemod_dict


def cache(seconds=1, cache_parameters=True):
    """
    Decorates a method of a class for caching its output.

    The cache is stored inside the object under the attribute '_cachemod_internal_cache'. This cache is a dictionary
    containing TimedVariable objects wrapping the outputs of each of the cached functions.
    Periodically, a cache clear is triggered when the time threshold specified by the option
    rcParams['global.cache.expiration_interval_seconds'] is met.

    When a method is decorated with this decorator, its output is cached in the cache for the given seconds. This
    implies that further calls to the method within the `seconds` time window after the first cache will provide
    directly the same output without entering the method execution.

    The cache time of a method can be dynamically modified by the caller by specifying the parameter `_cache_time=X` in
    the method call. This is a volatile parameter, meaning that it only affects once for the caller. The cache can be
    bypassed by setting `_cache_time=0`.

    :param seconds:
        Number of seconds to keep this entry in the cache after its first cache.

    :param cache_parameters:
        Specifies whether the cache key should take into consideration parameters or not.

    :return:
        Decorated function.
    """
    def pseudo_decorator(func):

        def real_wrapper(instance, *args, **kwargs):
            # 1. We create the cache dictionary inside the object if it doesn't exist.

            cache_dict = clear_expired_keys(instance._cachemod_internal_cache if hasattr(instance, "_cachemod_internal_cache") else {})
            instance._cachemod_internal_cache = cache_dict

            # Then, build the caching key based on the function reference. It will include parameters if cache_parameters is True.
            key = str(func) + ((str(args) + str(kwargs)) if cache_parameters else '')

            result = cache_dict.get(key)

            if result is None:
                # We store the output of the function wrapped in a TimedVariable inside the cache dictionary.
                # The timed variable allows us to track last update and know if it is expired.
                result = TimedVariable(func(instance, *args, **kwargs))
                cache_dict[key] = result

            elif result.last_update_elapsed_time >= kwargs.get("_cache_time", seconds):
                # In case the key exist but expired, we update its value with the output of the function.
                # An update triggers a refresh of the internal `last_update` registry.
                result.value = func(instance, *args, **kwargs)

            return result.value

        return real_wrapper

    return pseudo_decorator
