import scrapelib
from urllib import urlencode
import json
import os
import us
from geomancer.helpers import encoded_dict
from geomancer.mancers.base import BaseMancer, MancerError
from geomancer.mancers.geotype import County
from geomancer.app_config import CACHE_DIR
from string import punctuation
import re

SUMLEV_LOOKUP = {
    "county": "050",
}

class CensusReporter(BaseMancer):
    """ 
    Subclassing the main BaseMancer class
    """
    
    name = 'Kenya National Bureau of Statistics'
    machine_name = 'knbs'
    base_url = 'http://api.censusreporter.org/1.0'
    info_url = 'http://www.knbs.or.ke/'
    description = """ 
        Demographic data from the 2009 Kenya Census.
    """

    def get_metadata(self):
        datasets = [
            {
                'table_id': 'households',
                'human_name': 'Number of housholds',
                'description': 'Number of households',
                'source_name': self.name,
                'source_url': 'http://www.knbs.or.ke/index.php?option=com_content&view=article&id=176&Itemid=645',
                'geo_types': [County()],
                'columns': ['Number of households'],
                'count': 1
            },
            {
                'table_id': 'area',
                'human_name': 'Area in Square KM',
                'description': 'Area in square km',
                'source_name': self.name,
                'source_url': 'http://www.knbs.or.ke/index.php?option=com_content&view=article&id=176&Itemid=645',
                'geo_types': [County()],
                'columns': ['Area in sq km'],
                'count': 1
            },
            {
                'table_id': 'density',
                'human_name': 'Population density',
                'description': 'Population density',
                'source_name': self.name,
                'source_url': 'http://www.knbs.or.ke/index.php?option=com_content&view=article&id=176&Itemid=645',
                'geo_types': [County()],
                'columns': ['Population density'],
                'count': 1
            },
            {
                'table_id': 'male',
                'human_name': 'Male',
                'description': 'male',
                'source_name': self.name,
                'source_url': 'http://www.knbs.or.ke/index.php?option=com_content&view=article&id=176&Itemid=645',
                'geo_types': [County()],
                'columns': ['male'],
                'count': 1
            },
            {
                'table_id': 'female',
                'human_name': 'Female',
                'description': 'female',
                'source_name': self.name,
                'source_url': 'http://www.knbs.or.ke/index.php?option=com_content&view=article&id=176&Itemid=645',
                'geo_types': [County()],
                'columns': ['female'],
                'count': 1
            },
            {
                'table_id': 'total',
                'human_name': 'Total',
                'description': 'total',
                'source_name': self.name,
                'source_url': 'http://www.knbs.or.ke/index.php?option=com_content&view=article&id=176&Itemid=645',
                'geo_types': [County()],
                'columns': ['total'],
                'count': 1
            },

        ]
        return datasets

    def lookup_state(self, term, attr='name'):
        return term

    def geo_lookup(self, search_term, geo_type=None):
        """ 
        Search for geoids based upon name of geography

        Returns a response that maps the incoming search term to the geoid:

        {
          'term': <search_term>,
          'geoid': '<full_geoid>',
        }

        """
        results = {
            'term': search_term,
            'geoid': search_term
        }
        return results

    def search(self, geo_ids=None, columns=None):
        """ 
        Response should look like:
        {
            'header': [
                'Sex by Educational Attainment for the Population 25 Years and Over, 5th and 6th grade',
                'Sex by Educational Attainment for the Population 25 Years and Over, 7th and 8th grade'
                '...etc...'
            ],
            '04000US55': [
                1427.0,
                723.0,
                3246.0,
                760.0,
                ...etc...,
            ],
            '04000US56': [
                1567.0,
                743.0,
                4453.0,
                657.0,
                ...etc...,
            ]
        }

        The keys are CensusReporter 'geo_ids' and the value is a list that you
        should be able to call the python 'zip' function on with the 'header' key.
        """
        # these are the tables where we want to leave the table name out
        # of the header cell name in output, for prettiness, b/c
        # there is redundant info in table_title & detail_title

        DATA = [{'mombasa': ['268,700', '3,079.00', '305.1', '486,924', '452,446', '939,370']}, {'kwale': ['122,047', '1,265.00', '513.8', '315,997', '333,934', '649,931']}, {'kilifi': ['199,764', '2,343.00', '473.6', '535,526', '574,209', '1,109,735']}, {'tanariver': ['47,414', '626', '383.5', '119,853', '120,222', '240,075']}, {'lamu': ['22,184', '265', '383.2', '53,045', '48,494', '101,539']}, {'taitataveta': ['71,090', '971', '293.2', '145,334', '139,323', '284,657']}, {'garissa': ['98,590', '861', '723.7', '334,939', '288,121', '623,060']}, {'wajir': ['88,574', '815', '812.2', '363,766', '298,175', '661,941']}, {'mandera': ['125,497', '1,038.00', '988.2', '559,943', '465,813', '1,025,756']}, {'marsabit': ['56,941', '653', '445.9', '151,112', '140,054', '291,166']}, {'isiolo': ['31,326', '397', '360.9', '73,694', '69,600', '143,294']}, {'meru': ['319,616', '3,196.00', '424.4', '670,656', '685,645', '1,356,301']}, {'tharakanithi': ['88,803', '1,102.00', '331.5', '178,451', '186,879', '365,330']}, {'embu': ['131,683', '1,296.00', '398.3', '254,303', '261,909', '516,212']}, {'kitui': ['205,491', '3,587.00', '282.3', '481,282', '531,427', '1,012,709']}, {'machakos': ['264,500', '3,052.00', '360', '543,139', '555,445', '1,098,584']}, {'makueni': ['186,478', '2,344.00', '377.4', '430,710', '453,817', '884,527']}, {'nyandarua': ['143,879', '1,259.00', '473.6', '292,155', '304,113', '596,268']}, {'nyeri': ['201,703', '2,077.00', '333.9', '339,725', '353,833', '693,558']}, {'kirinyaga': ['154,220', '1,401.00', '376.9', '260,630', '267,424', '528,054']}, {'muranga': ['255,696', '2,517.00', '374.5', '457,864', '484,717', '942,581']}, {'kiambu': ['469,244', '4,946.00', '328.2', '802,609', '820,673', '1,623,282']}, {'turkana': ['123,191', '1,520.00', '562.8', '445,069', '410,330', '855,399']}, {'westpokot': ['93,777', '1,407.00', '364.4', '254,827', '257,863', '512,690']}, {'samburu': ['47,354', '542', '413.2', '112,007', '111,940', '223,947']}, {'transnzoia': ['170,117', '1,611.00', '508.2', '407,172', '411,585', '818,757']}, {'uasingishu': ['202,291', '2,112.00', '423.4', '448,994', '445,185', '894,179']}, {'elgiyomarakwet': ['77,555', '1,107.00', '334.2', '183,738', '186,260', '369,998']}, {'nandi': ['154,073', '1,777.00', '423.7', '376,488', '376,477', '752,965']}, {'baringo': ['110,649', '1,970.00', '282', '279,081', '276,480', '555,561']}, {'laikipia': ['103,114', '1,023.00', '390.3', '198,625', '200,602', '399,227']}, {'nakuru': ['409,836', '4,650.00', '344.8', '804,582', '798,743', '1,603,325']}, {'narok': ['169,220', '1,852.00', '459.5', '429,026', '421,894', '850,920']}, {'kajiado': ['173,464', '1,105.00', '351.6', '345,146', '342,166', '687,312']}, {'bomet': ['142,361', '1,630.00', '444.3', '359,727', '364,459', '724,186']}, {'kericho': ['160,134', '1,886.00', '402.1', '381,980', '376,359', '758,339']}, {'kakamega': ['355,679', '3,343.00', '496.8', '800,989', '859,662', '1,660,651']}, {'vihiga': ['123,347', '1,271.00', '436.4', '262,716', '291,906', '554,622']}, {'bungoma': ['321,628', '3,123.00', '522.2', '710,510', '835,339', '1,630,934']}, {'busia': ['103,421', '1,171.00', '416.8', '232,075', '256,000', '488,075']}, {'siaya': ['199,034', '2,183.00', '385.9', '398,652', '443,652', '842,304']}, {'kisumu': ['226,719', '2,407.00', '402.5', '474,760', '494,149', '968,909']}, {'homabay': ['160,935', '1,754.00', '427.2', '357,273', '392,058', '749,331']}, {'migori': ['41,800', '489', '523.7', '125,938', '130,148', '256,086']}, {'kisii': ['245,029', '2,588.00', '445.2', '550,464', '601,818', '1,152,282']}, {'nyamira': ['131,039', '1,291.00', '463.4', '287,048', '311,204', '598,252']}, {'nairobi': ['985,016', '10,323.00', '304', '1,605,230', '1,533,139', '3,138,369']}]
        COLUMNS = ['households', 'area', 'density', 'male', 'female', 'total']
        results = {'header': []}
        for column in columns:
            results['header'].append(column)
            for geo_type, geo_id in geo_ids:
                if not results.get(geo_id):
                    results[geo_id] = []
                try:
                    results[geo_id].append((item for item in DATA if item.keys()[0].lower().replace('-','').replace(' ','') == geo_id.lower().replace('-','').replace(' ','')).next().values()[0][COLUMNS.index(column)])
                except Exception, e:
                    print e
        return results
