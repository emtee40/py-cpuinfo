


import unittest
from test_example import TestExample
from test_debian_8_x86_64 import TestDebian


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(TestExample))
	suite.addTest(unittest.makeSuite(TestDebian))

	runner = unittest.TextTestRunner()
	runner.run(suite)

