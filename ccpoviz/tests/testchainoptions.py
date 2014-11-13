"""
Tests for the options chainer
=============================

In this test, the default and user values are both given as python data
structure directly to test the core functionality of the code without being
dependent upon any particular option file format.

"""

import unittest

from ccpoviz import chainoptions as co


class ChainOptionsTest(unittest.TestCase):

    """Tests the options chainer based on a toy setting"""

    def setUp(self):

        """Sets up a toy option default and a default update"""

        self.default = {
            'string-option': 'default value',
            'boolean-option': False,
            'number-option': 1,
            'list-option-1': [1, 2, 3],
            'list-option-2': [],
            'list-option-2...prototype': {'value': 1, 'const2': 2},
            'map-option-1': {'op1': 1, 'const2': 2},
            'map-option-2': {},
            'map-option-2...update': 'extend',
            'map-option-2...prototype': [1, 2],
            'map-option-2...prototype...update': 'append',
        }

        self.dummy_update = {
            'boolean-option': True,
            }

        self.chainer = co.ChainOptions()

    #
    # Correct update testing
    # ----------------------
    #
    # Here all the user inputs are correct.
    #

    def test_update_atom(self):

        """Tests the update of the atoms"""

        update = {
            'string-option': 'new_value',
            'number-option': 3
            }

        res = self.chainer.chain_options(
            update, self.dummy_update, self.default
            )

        self.assertEqual(res['string-option'], 'new_value')
        self.assertEqual(res['boolean-option'], True)
        self.assertEqual(res['number-option'], 3)

    def test_update_list(self):

        """Tests the update of the lists"""

        update = {
            'list-option-1': [12, 12, 14],
            'list-option-2': [
                {'value': 5},
                {'value': 6}
                ],
            }

        res = self.chainer.chain_options(
            update, self.dummy_update, self.default
            )

        self.assertEqual(res['boolean-option'], True)
        self.assertEqual(res['list-option-1'], [12, 12, 14])
        self.assertEqual(res['list-option-2'][0]['value'], 5)
        self.assertEqual(res['list-option-2'][1]['value'], 6)
        self.assertEqual(res['list-option-2'][1]['const2'], 2)

    def test_update_map(self):

        """Tests the update of the two maps"""

        update = {
            'map-option-1': {'op1': 3},
            'map-option-2': {
                'key1': [-1, -2],
                'key2': [99, 88],
                },
            }

        res = self.chainer.chain_options(
            update, self.dummy_update, self.default
            )

        self.assertEqual(res['map-option-1']['op1'], 3)
        self.assertEqual(res['map-option-1']['const2'], 2)
        self.assertEqual(len(res['map-option-2']), 2)
        self.assertEqual(res['map-option-2']['key1'], [1, 2, -1, -2])
        self.assertEqual(res['map-option-2']['key2'], [1, 2, 99, 88])

    #
    # Exception test
    # --------------
    #
    # Now we test if correct error can be detected and reported for erroneous
    # user inputs.
    #

    def test_atomic_type_error(self):

        """Tests with wrong type for atoms"""

        for update in [{'boolean-option': 14},
                       {'number-option': 'sdas'},
                       {'string-option': False}]:
            with self.assertRaises(co.UpdateError) as cm:
                self.chainer.chain_options(
                    update, self.dummy_update, self.default
                    )
            update_exc = cm.exception
            self.assertEqual(update_exc.args[0], ('', update.keys()[0]))

    def test_invalid_key_error(self):

        """Tests with updating a map with invalid key"""

        update = {'non-existant-op': 123}
        with self.assertRaises(co.UpdateError) as cm:
            self.chainer.chain_options(
                update, self.dummy_update, self.default
                )
        update_exc = cm.exception
        self.assertEqual(update_exc.args[0], ('', 'non-existant-op'))

        update = {
            'list-option-2': [{'value': 11},
                              {'value22': 22}],
            }
        with self.assertRaises(co.UpdateError) as cm:
            self.chainer.chain_options(
                update, self.dummy_update, self.default
                )
        update_exc = cm.exception
        self.assertEqual(
            update_exc.args[0],
            ('', 'list-option-2', 1, 'prototype', 'value22')
            )

    def test_invalid_value_for_proto(self):

        """Tests updating a map with a value not compatible with the proto"""

        update = {
            'map-option-2': {'key': ['asdas', 'asdas']},
        }

        with self.assertRaises(co.UpdateError) as cm:
            self.chainer.chain_options(
                update, self.dummy_update, self.default
                )
        update_exc = cm.exception
        self.assertEqual(
            update_exc.args[0],
            ('', 'map-option-2', 'key', 'prototype', 0, 'prototype')
            )
