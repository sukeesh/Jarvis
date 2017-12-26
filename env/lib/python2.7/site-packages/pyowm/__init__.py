#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The PyOWM init file

**Author**: Claudio Sparpaglione, @csparpa <csparpa@gmail.com>

**Platform**: platform independent

"""

from pyowm import constants
from pyowm.utils import timeutils  # Convenience import


def OWM(API_key=constants.DEFAULT_API_KEY, version=constants.LATEST_OWM_API_VERSION,
        config_module=None, language=None, subscription_type=None):
    """
    A parametrized factory method returning a global OWM instance that
    represents the desired OWM web API version (or the currently supported one
    if no version number is specified)

    :param API_key: the OWM web API key (defaults to a test value)
    :type API_key: str
    :param version: the OWM web API version. Defaults to ``None``, which means
        use the latest web API version
    :type version: str
    :param config_module: the Python path of the configuration module you want
        to provide for instantiating the library. Defaults to ``None``, which
        means use the default configuration values for the web API version
        support you are currently requesting. Please be aware that malformed
        user-defined configuration modules can lead to unwanted behaviour!
    :type config_module: str (eg: 'mypackage.mysubpackage.myconfigmodule')
    :param language: the language in which you want text results to be returned.
          It's a two-characters string, eg: "en", "ru", "it". Defaults to:
          ``None``, which means use the default language.
    :type language: str
    :param subscription_type: the type of OWM web API subscription to be wrapped.
           Can be 'free' (free subscription) or 'pro' (paid subscription),
           Defaults to: 'free'
    :type subscription_type: str
    :returns: an instance of a proper *OWM* subclass
    :raises: *ValueError* when unsupported OWM API versions are provided
    """
    if version == '2.5':
        if config_module is None:
            config_module = "pyowm.webapi25.configuration25"
        cfg_module = __import__(config_module,  fromlist=[''])
        from pyowm.webapi25.owm25 import OWM25
        if language is None:
            language = cfg_module.language
        if subscription_type is None:
            subscription_type = cfg_module.API_SUBSCRIPTION_TYPE
            if subscription_type not in ['free', 'pro']:
                subscription_type = 'free'
        return OWM25(cfg_module.parsers, API_key, cfg_module.cache,
                     language, subscription_type)
    raise ValueError("Unsupported OWM web API version")
