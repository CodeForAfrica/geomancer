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

class Wazimap(BaseMancer):
    """
    Subclassing the main BaseMancer class
    """

    name = 'Wazimap Kenya'
    machine_name = 'wazimap_ke'
    base_url = 'https://kenya.wazimap.org'
    info_url = 'https://kenya.wazimap.org'
    description = """
        Kenya data based on counties
    """
    datasets = None

    def get_metadata(self):
        datasets = [
            {
                'table_id': 'waste',
                'human_name': 'Main mode of waste disposal',
                'description': 'Main mode of waste disposal',
                'source_name': self.name,
                'source_url': 'https://kenya.wazimap.org/api/1.0/data/show/latest?table_ids=mainmodeofhumanwastedisposal&geo_ids=',
                'geo_types': [County()],
                'columns': ['total', 'septic tank', 'bucket', 'bush', 'other', 'main sewer', 'cess pool'],
                'count': 7,
                'key': 'mainmodeofhumanwastedisposal'
            },
            {
                'table_id': 'water',
                'human_name': 'Main source of water',
                'description': 'Main source of water',
                'source_name': self.name,
                'source_url': 'https://kenya.wazimap.org/api/1.0/data/show/latest?table_ids=mainsourceofwater&geo_ids=',
                'geo_types': [County()],
                'columns': ['water vendor', 'stream', 'jabia/rain/harvested', 'spring/well/borehole', 'pond/dam', 'lake', 'other','piped into dwelling', 'piped', 'total'],
                'count': 10,
                'key': 'mainsourceofwater'
            },
            {
                'table_id': 'lighting',
                'human_name': 'Main type of lighting fuel',
                'description': 'Main type of lighting fuel',
                'source_name': self.name,
                'source_url': 'https://kenya.wazimap.org/api/1.0/data/show/latest?table_ids=maintypeoflightingfuel&geo_ids=',
                'geo_types': [County()],
                'columns': ['total', 'electricity', 'gas lamps', 'lanterns', 'other', 'pressure lamps', 'solar', 'tin lamps', 'wood'],
                'count': 9,
                'key': 'maintypeoflightingfuel'
            },
            {
                'table_id': 'flooring',
                'human_name': 'Main type of floor material',
                'description': 'Main type of floor material',
                'source_name': self.name,
                'source_url': 'https://kenya.wazimap.org/api/1.0/data/show/latest?table_ids=maintypeoffloormaterial&geo_ids=',
                'geo_types': [County()],
                'columns': ['total', 'cement', 'earth', 'other', 'tiles', 'wood'],
                'count': 6,
                'key': 'maintypeoffloormaterial'
            },
            {
                'table_id': 'wall',
                'human_name': 'Main type of wall material',
                'description': 'Main type of wall material',
                'source_name': self.name,
                'source_url': 'https://kenya.wazimap.org/api/1.0/data/show/latest?table_ids=maintypeofwallmaterial&geo_ids=',
                'geo_types': [County()],
                'columns': ['total', 'brick/block', 'corrugated iron sheets', 'grass/reeds', 'mud/cement', 'mud/wood', 'other',
                            'stone', 'tin', 'wood only'],
                'count': 10,
                'key': 'maintypeofwallmaterial'
            },
            {
                'table_id': 'roofing',
                'human_name': 'Main type of roofing material',
                'description': 'Main type of roofing material',
                'source_name': self.name,
                'source_url': 'https://kenya.wazimap.org/api/1.0/data/show/latest?table_ids=maintypeofroofingmaterial&geo_ids=',
                'geo_types': [County()],
                'columns': ['total', 'asbestos sheets', 'concrete', 'corrugated iron sheets', 'grass', 'makuti',
                            'other',
                            'mud/dung', 'tin', 'tiles'],
                'count': 10,
                'key': 'maintypeofroofingmaterial'
            },
            {
                'table_id': 'education',
                'human_name': 'Highest education level reached',
                'description': 'Highest education level reached',
                'source_name': self.name,
                'source_url': 'https://kenya.wazimap.org/api/1.0/data/show/latest?table_ids=highesteducationlevelreached&geo_ids=',
                'geo_types': [County()],
                'columns': ['total', 'basic literacy', 'madrassa', 'none', 'pre-primary', 'primary',
                            'secondary',
                            'university', 'tertiary', 'youth polytechnic'],
                'count': 10,
                'key': 'highesteducationlevelreached'
            },

        ]
        self.datasets = datasets
        return datasets

    def lookup_state(self, term, attr='name'):
        return term

    def geo_lookup(self, search_term, geo_type=None):
        lookup_table = [
                        ["county","1","Mombasa"],
                        ["county","2","Kwale"],
                        ["county","3","Kilifi"],
                        ["county","4","TanaRiver"],
                        ["county","5","Lamu"],
                        ["county","6","TaitaTaveta"],
                        ["county","7","Garissa"],
                        ["county","8","Wajir"],
                        ["county","9","Mandera"],
                        ["county","10","Marsabit"],
                        ["county","11","Isiolo"],
                        ["county","12","Meru"],
                        ["county","13","TharakaNithi"],
                        ["county","14","Embu"],
                        ["county","15","Kitui"],
                        ["county","16","Machakos"],
                        ["county","17","Makueni"],
                        ["county","18","Nyandarua"],
                        ["county","19","Nyeri"],
                        ["county","20","Kirinyaga"],
                        ["county","21","Murang'a"],
                        ["county","22","Kiambu"],
                        ["county","23","Turkana"],
                        ["county","24","WestPokot"],
                        ["county","25","Samburu"],
                        ["county","26","TransNzoia"],
                        ["county","27","UasinGishu"],
                        ["county","28","ElgeyoMarakwet"],
                        ["county","29","Nandi"],
                        ["county","30","Baringo"],
                        ["county","31","Laikipia"],
                        ["county","32","Nakuru"],
                        ["county","33","Narok"],
                        ["county","34","Kajiado"],
                        ["county","35","Kericho"],
                        ["county","36","Bomet"],
                        ["county","37","Kakamega"],
                        ["county","38","Vihiga"],
                        ["county","39","Bungoma"],
                        ["county","40","Busia"],
                        ["county","41","Siaya"],
                        ["county","42","Kisumu"],
                        ["county","43","HomaBay"],
                        ["county","44","Migori"],
                        ["county","45","Kisii"],
                        ["county","46","Nyamira"],
                        ["county","47","Nairobi"],
                        ["country","KE","Kenya"],
                    ]
        geoid = None
        for l in lookup_table:
            if search_term.lower().replace(' ', '').replace('-', '') == l[2].lower():
                geoid = l[0] + '-' + l[1]
        results = {
            'term': search_term,
            'geoid': geoid
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
        results = {'header': []}
        for geo_type, geo_id in geo_ids:
            table_id = columns[0]
            details = []
            key = None
            human_name = None
            for y in self.datasets:
                if y['table_id'] == table_id:
                    details = y['columns']
                    key = y['key']
                    human_name = y['human_name']
                    break
            if not results.get(geo_id):
                results[geo_id] = []
            # try:
            info = self.urlopen('%s/api/1.0/data/show/latest?table_ids=%s&geo_ids=%s' % (self.base_url, key, geo_id))
            data_info = json.loads(info)['data'][geo_id][key.upper()]['estimate']
            for k in details:
                if k not in results['header']:
                    h = k
                    if k == 'total': h = 'total ('+ human_name +')'
                    results['header'].append(h.title())
                results[geo_id].append(data_info[k])
            # except Exception, e:
            #     print e
        return results
