#!/usr/bin/env python

def all_same(l):
    first_item = iter(l).next()
    for cur_item in l:
        if cur_item != first_item:
            return False
    return True



def find_diffs(data):
    diffchars = []
    for item_num, items in enumerate(zip(*data)):
        if not all_same(items):
            diffchars.append( item_num)
    return diffchars



if __name__ == '__main__':
    import unittest
    class H(unittest.TestCase):
        def test_all_same_string_false(self):
            self.assertEqual(False, all_same(iter('aazaa')))

        def test_all_same_string_true(self):
            self.assertEqual(True, all_same(iter('aaaaa')))

        def test_all_same_list_False(self):
            self.assertEqual(False, all_same(['A','v','A','A']))


        def test_all_same_list_True(self):
            self.assertEqual(True, all_same(['A','A','A','A']))
        
        def test_all_same_raw_string_true(self):
            self.assertEqual(True, all_same('aaaaa'))


    class I(unittest.TestCase):
        def test_track(self):
            self.assertEqual([5,6], find_diffs( ['track%.2d.whatever' % n  for n in range(12) ]))

        def test_track(self):
            self.assertEqual([5,6], find_diffs( ['track%.2d.whatever' % n  for n in range(12) ]))


    unittest.main()
