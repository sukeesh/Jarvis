# -*- coding: utf-8 -*-

from datetime import datetime, date, time, timedelta
from dateutil.relativedelta import relativedelta
import re

def parse_number(string, numwords=None):
    """
    Parse the given string to an integer.

    This supports pure numerals with or without ',' as a separator between digets.
    Other supported formats include literal numbers like 'four' and mixed numerals
    and literals like '24 thousand'.
    :return: (skip, value) containing the number of words separated by whitespace,
             that were parsed for the number and the value of the integer itself.
    """
    if numwords is None:
        numwords = {}
    if not numwords:
        units = ["zero", "one", "two", "three",
                 "four", "five", "six", "seven", "eight", "nine", "ten",
                 "eleven", "twelve", "thirteen", "fourteen", "fifteen",
                 "sixteen", "seventeen", "eighteen", "nineteen"]
        tens = ["", "", "twenty", "thirty", "forty", "fifty",
                "sixty", "seventy", "eighty", "ninety"]
        scales = ["hundred", "thousand", "million", "billion", "trillion"]

        numwords["and"] = (1, 0)
        for idx, word in enumerate(units):
            numwords[word] = (1, idx)
        for idx, word in enumerate(tens):
            numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales):
            numwords[word] = (10 ** (idx * 3 or 2), 0)

    skip = 0
    value = 0
    elements = string.replace(",", "").split()
    current = 0
    for d in elements:
        number = d.split("-")
        for word in number:
            if word not in numwords:
                try:
                    scale, increment = (1, int(word))
                except ValueError:
                    value += current
                    return skip, value
            else:
                scale, increment = numwords[word]
                if not current and scale > 100:
                    current = 1
            current = current * scale + increment
            if scale > 100:
                value += current
                current = 0
        skip += 1
    value += current
    return skip, value

DATE_PATTERNS = {
    #Date formats
    r'^[0-9]{2}-[0-1][0-9]-[0-3][0-9]$': 
        lambda x: (1, datetime.strptime(x, "%y-%m-%d").date()),
    r'^[1-9][0-9]{3}-[0-1][0-9]-[0-3][0-9]$': 
        lambda x: (1, datetime.strptime(x, "%Y-%m-%d").date()),
    r'^[0-3][0-9]\.[0-1][0-9]\.[0-9]{2}$': 
        lambda x: (1, datetime.strptime(x, "%d.%m.%y").date()),
    r'^[0-3][0-9]\.[0-1][0-9]\.[1-9][0-9]{3}$': 
        lambda x: (1, datetime.strptime(x, "%d.%m.%Y").date()),
    
    # Time formats
    r'^[0-1][0-9]:[0-5][0-9][AP]M$': 
        lambda x: (1, datetime.strptime(x, "%I:%M%p").time()),
    r'^[1-9]:[0-5][0-9][AP]M$': 
        lambda x: (1, datetime.strptime("0" + x, "%I:%M%p").time()),
    r'^[0-2][0-9]:[0-5][0-9]$': 
        lambda x: (1, datetime.strptime(x, "%H:%M").time()),
    r'^[1-9]:[0-5][0-9]$': 
        lambda x: (1, datetime.strptime("0" + x, "%H:%M").time()),
}

# Relative time units and their handlers
TIME_UNITS = {
    'year': lambda v: relativedelta(years=v),
    'month': lambda v: relativedelta(months=v),
    'week': lambda v: timedelta(weeks=v),
    'day': lambda v: timedelta(days=v),
    'hour': lambda v: timedelta(hours=v),
    'minute': lambda v: timedelta(minutes=v),
    'second': lambda v: timedelta(seconds=v),
}

def parse_next_weekday(weekday: str):
    """Parse next weekday"""
    try:
        date_str = f"{weekday} {datetime.now().strftime('%Y %W')}"
        result = datetime.strptime(date_str, "%a %Y %W")
    except ValueError:
        try:
            result = datetime.strptime(date_str, "%A %Y %W")
        except ValueError:
            return None
    
    if result.date() <= datetime.now().date():
        result += timedelta(days=7)
        
    return (2, result)

def parse_single_time_unit(words: list):
    """Parse a single time unit (e.g., '2 days' or 'one hour')"""
    if not words:
        return None, 0, None
        
    skip, value = parse_number(" ".join(words))
    if not skip:
        return None, 0, None
    
    if skip >= len(words):
        return None, skip, value
        
    unit_word = words[skip].lower()
    for unit, handler in TIME_UNITS.items():
        if unit in unit_word:
            delta = handler(value)
            return delta, skip + 1, None
            
    return None, skip, value

def parse_time_delta(words: list):
    """Parse time delta including compound expressions"""
    if not words:
        return None
        
    total_skip = 0
    total_delta = timedelta()
    base_time = datetime.now()
    
    while total_skip < len(words):
        if words[total_skip].lower() == 'and':
            total_skip += 1
            continue
            
        delta, skip, value = parse_single_time_unit(words[total_skip:])
        if not delta and not value:
            break
            
        if delta:
            total_delta += delta
        
        total_skip += skip
        
        if total_skip >= len(words) or words[total_skip].lower() != 'and':
            break
    
    if total_skip > 0:
        return (total_skip +1, base_time + total_delta)
    return None

def handle_relative_date(words: list):
    """Handle relative date expressions"""
    if not words:
        return None
        
    if words[0] == "next" and len(words) > 1:
        return parse_next_weekday(words[1])
        
    if words[0] == "in":
        words = words[1:]
        return parse_time_delta(words)
        
    return None

def parse_date(string: str):
    """
    Parse the given string for a date or timespan.

    The number for a timespan can be everything supported by parseNumber().

    Supported date formats:
        2017-03-22 and 17-03-22
        22.03.2017 and 22.03.17
    Supported time formats:
        17:30
        5:30PM
    Supported timespan formats:
        in one second/minute/hour/day/week/month/year
        in 2 days and 3 hours
        next monday
    :return: (skip, time) containing the number of words separated by whitespace,
             that were parsed for the date and the date itself as datetime.
    """
    elements = string.split()
    current_date = datetime.now().date()
    current_time = datetime.now().time()
    skip = 0
    
    for i, word in enumerate(elements):
        if skip > i:
            continue
            
        # Try pattern matching first
        for pattern, parser in DATE_PATTERNS.items():
            if re.match(pattern, word):
                skip_words, result = parser(word)
                skip = i + skip_words
                if isinstance(result, date):
                    current_date = result
                else:
                    current_time = result
                break
        
        # Handle relative dates if no pattern matched
        if skip <= i:
            relative_result = handle_relative_date(elements[i:])
            if relative_result:
                skip_words, new_datetime = relative_result
                skip = i + skip_words
                current_date = new_datetime.date()
                current_time = new_datetime.time()
            else:
                break
    
    return (skip, datetime.combine(current_date, current_time))