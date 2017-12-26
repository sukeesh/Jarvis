"""
Module containing weather code lookup and resolution classes
"""

class WeatherCodeRegistry(object):

    """
    A registry class for looking up weather statuses from weather codes.

    :param code_ranges_dict: a dict containing the mapping between weather
        statuses (eg: "sun","clouds",etc) and weather code ranges
    :type code_ranges_dict: dict
    :returns: a *WeatherCodeRegistry* instance

    """

    def __init__(self, code_ranges_dict):
        self._code_ranges_dict = code_ranges_dict

    def status_for(self, code):
        """
        Returns the weather status related to the specified weather status
        code, if any is stored, ``None`` otherwise.

        :param code: the weather status code whose status is to be looked up
        :type code: int
        :returns: the weather status str or ``None`` if the code is not mapped
        """
        is_in = lambda start, end, n: True if start <= n <= end else False
        for status in self._code_ranges_dict:
            for _range in self._code_ranges_dict[status]:
                if is_in(_range['start'],_range['end'],code):
                    return status
        return None

    def __repr__(self):
        return "<%s.%s>" % (__name__, self.__class__.__name__)