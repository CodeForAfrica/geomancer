from json import JSONEncoder
import re
import us
from os.path import join, abspath, dirname
import csv

GAZDIR = join(dirname(abspath(__file__)), 'gazetteers')

class GeoType(object):
    """ 
    Base class for defining geographic types.
    All four static properties should be defined
    """
    human_name = None
    machine_name = None
    formatting_notes = None
    formatting_example = None
    validation_regex = None

    def as_dict(self):
        fields = [
            'human_name',
            'machine_name',
            'formatting_notes',
            'formatting_example',
        ]
        d = {k:getattr(self,k) for k in fields}
        for k,v in d.items():
            d[k] = ' '.join(v.split())
        return d

    def validate(self, values):
        ''' 
        Default is to implement a regex on a subclass that gets
        used here to validate the format. Optionally override this
        method to implement custom validation. If validation_regex
        is not defined on the subclass, this will always return True.

        values - A list (or other iterable) of values to evaluate

        Returns a boolean indicating whether all the members of the values
        list are valid and an optional user friendly message.
        '''

        if self.validation_regex is None:
            return False, None
        else:
            values = list(set([v for v in values if v]))
            for v in values:
                if not re.match(self.validation_regex, v):
                    message = 'The column you selected must be formatted \
                        like "%s" to match on %s geographies. Please pick another \
                        column or change the format of your data.' % \
                        (self.formatting_example, self.human_name)
                    return False, message
            return True, None
      
class GeoTypeEncoder(JSONEncoder):
    ''' 
    Custom JSON encoder so we can have nice things.
    '''
    def default(self, o):
        return o.as_dict()

class County(GeoType):
    human_name = 'County'
    machine_name = 'County'
    formatting_notes = 'County name'
    formatting_example = 'Nairobi'
    
    def validate(self, values):
        values = [v for v in values if v]
        non_matches = set()
        counties = ['Mombasa', 'Kwale', 'Kilifi', 'Tanariver', 'Lamu', 'Taita Taveta', 'Garissa', 'Wajir', 'Mandera', 'Marsabit', 'Isiolo', 'Meru', 'Tharaka', 'Embu', 'Kitui', 'Machakos', 'Makueni', 'Nyandarua', 'Nyeri', 'Kirinyaga', 'Muranga', 'Kiambu', 'Turkana', 'West Pokot', 'Samburu', 'TransNzoia', 'UasinGishu', 'ElgeyoMarakwet', 'Nandi', 'Baringo', 'Laikipia', 'Nakuru', 'Narok', 'Kajiado', 'Bomet', 'Kericho', 'Kakamega', 'Vihiga', 'Bungoma', 'Busia', 'Siaya', 'Kisumu', 'HomaBay', 'Migori', 'Kisii', 'Nyamira', 'Nairobi']
        for val in values:
            if val.lower().replace(' ','').replace('-','') not in counties:
                non_matches.add(val)
        if non_matches:
            return False, '"{0}" do not appear to be valid Census places'\
                .format(', '.join(non_matches))
        else:
            return True, None