from collections import OrderedDict
from unittest import TestCase
from sphinxql import indexes

from sphinxql.configuration.configurations import IndexConfiguration
from sphinxql.configuration.configurators import add_source_conf_param
from sphinxql.exceptions import ImproperlyConfigured


class ConfiguratorTestCase(TestCase):
    def test_format(self):
        index_configurator = IndexConfiguration('test',
                                                OrderedDict([('source', 'test1'),
                                                             ('type', 'tes1'),
                                                             ('path', 'mypath')]))

        expected = "index test \n{\n    source = test1\n    type = tes1\n    path = mypath\n}\n"

        self.assertEqual(index_configurator.format_output(), expected)

    def test_multi_parameter_format(self):
        index_configurator = IndexConfiguration('test',
                                                OrderedDict([('source', 'test1'),
                                                             ('type', 'test1'),
                                                             ('rt_field', ['test1', 'test2']),
                                                             ('path', 'mypath')]))

        expected = "index test \n{\n" \
                   "    source = test1\n" \
                   "    type = test1\n" \
                   "    rt_field = test1\n" \
                   "    rt_field = test2\n" \
                   "    path = mypath\n" \
                   "}\n"

        self.assertEqual(index_configurator.format_output(), expected)

    def test_wrong_parameter(self):
        self.assertRaises(ImproperlyConfigured,
                          IndexConfiguration, 'test', {'source': 'test1',
                                                       'typERROR': 'tes1',
                                                       'path': 'mypath'})

    def test_missing_mandatory(self):
        self.assertRaises(ImproperlyConfigured,
                          IndexConfiguration, 'test', {'source': 'test1',
                                                       'type': 'tes1'})

    def test_wrong_source_param(self):
        self.assertRaises(ImproperlyConfigured, add_source_conf_param, {}, 'asdas', 1)

    def test_wrong_typed_parameter(self):
        with self.assertRaises(ImproperlyConfigured):
            IndexConfiguration('test',
                               {'source': 'test1',
                                'type': {'test1': 'test2'},
                                'path': 'mypath'})

    def test_wrong_typed_items(self):
        with self.assertRaises(ImproperlyConfigured):
            IndexConfiguration('test',
                               {'source': 'test1',
                                'type': 'test1',
                                'rt_field': [{'test1'}, 'test2'],
                                'path': 'mypath'})

    def test_not_a_model(self):
        with self.assertRaises(ImproperlyConfigured):
            class Index(indexes.Index):
                class Meta:
                    model = OrderedDict
