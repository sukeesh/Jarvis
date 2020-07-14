from plugin import plugin, alias


@alias("state capital", "state abbreviation")
@plugin("stateinfo")
class stateinfo:
    """
    Get the postal abbreviation and state capital of a given U.S. state
    Usage: stateinfo [command]
    Aliases: state
             state capital
             state abbreviation
    """

    def __call__(self, jarvis, s):
        capital_dict = {
            'alabama': 'montgomery',
            'alaska': 'juneau',
            'arizona': 'phoenix',
            'arkansas': 'little rock',
            'california': 'sacramento',
            'colorado': 'denver',
            'connecticut': 'hartford',
            'delaware': 'dover',
            'florida': 'tallahassee',
            'georgia': 'atlanta',
            'hawaii': 'honolulu',
            'idaho': 'boise',
            'illinios': 'springfield',
            'indiana': 'indianapolis',
            'iowa': 'des monies',
            'kansas': 'topeka',
            'kentucky': 'frankfort',
            'louisiana': 'baton rouge',
            'maine': 'augusta',
            'maryland': 'annapolis',
            'massachusetts': 'boston',
            'michigan': 'lansing',
            'minnesota': 'st. paul',
            'mississippi': 'jackson',
            'missouri': 'jefferson city',
            'montana': 'helena',
            'nebraska': 'lincoln',
            'neveda': 'carson city',
            'new hampshire': 'concord',
            'new jersey': 'trenton',
            'new mexico': 'santa fe',
            'new york': 'albany',
            'north carolina': 'raleigh',
            'north dakota': 'bismarck',
            'ohio': 'columbus',
            'oklahoma': 'oklahoma city',
            'oregon': 'salem',
            'pennsylvania': 'harrisburg',
            'rhoda island': 'providence',
            'south carolina': 'columbia',
            'south dakoda': 'pierre',
            'tennessee': 'nashville',
            'texas': 'austin',
            'utah': 'salt lake city',
            'vermont': 'montpelier',
            'virginia': 'richmond',
            'washington': 'olympia',
            'west virginia': 'charleston',
            'wisconsin': 'madison',
            'wyoming': 'cheyenne'
        }
        abbrev_dict = {
            'alabama': 'al',
            'alaska': 'ak',
            'american samoa': 'as',
            'arizona': 'az',
            'arkansas': 'ar',
            'california': 'ca',
            'colorado': 'co',
            'connecticut': 'ct',
            'delaware': 'de',
            'district of columbia': 'dc',
            'florida': 'fl',
            'georgia': 'ga',
            'guam': 'gu',
            'hawaii': 'hi',
            'idaho': 'id',
            'illinois': 'il',
            'indiana': 'in',
            'iowa': 'ia',
            'kansas': 'ks',
            'kentucky': 'ky',
            'louisiana': 'la',
            'maine': 'me',
            'maryland': 'md',
            'massachusetts': 'ma',
            'michigan': 'mi',
            'minnesota': 'mn',
            'mississippi': 'ms',
            'missouri': 'mo',
            'montana': 'mt',
            'nebraska': 'ne',
            'nevada': 'nv',
            'new hampshire': 'nh',
            'new jersey': 'nj',
            'new mexico': 'nm',
            'new york': 'ny',
            'north carolina': 'nc',
            'north dakota': 'nd',
            'northern mariana islands': 'mp',
            'ohio': 'oh',
            'oklahoma': 'ok',
            'oregon': 'or',
            'pennsylvania': 'pa',
            'puerto rico': 'pr',
            'rhode island': 'ri',
            'south carolina': 'sc',
            'south dakota': 'sd',
            'tennessee': 'tn',
            'texas': 'tx',
            'utah': 'ut',
            'vermont': 'vt',
            'virgin islands': 'vi',
            'virginia': 'va',
            'washington': 'wa',
            'west virginia': 'wv',
            'wisconsin': 'wi',
            'wyoming': 'wy'
        }
        if s:
            try:
                capital = capital_dict[s].title()
                abbreviation = abbrev_dict[s].upper()
                jarvis.say("The capital of " + s.title() + " is " + capital)
                jarvis.say("The postal abbreviation is " + abbreviation)
            except KeyError:
                jarvis.say("Please enter a valid U.S. state")
        else:
            jarvis.say("Please input a state. Usage: stateinfo [state]")
