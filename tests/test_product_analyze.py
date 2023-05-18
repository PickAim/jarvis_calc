import unittest
from datetime import datetime

from jorm.market.items import Product

from jarvis_calc.calculators.product_analyze import DownturnCalculator
from tests.base_test import BaseCalcTest


class ProductAnalyzeTest(BaseCalcTest):
    def test_downturn_calculations(self):
        product_history = self.create_test_product_history()
        product = Product("product", 1000, 1, 3.4, "brand", "seller", "g", "g", product_history)
        downturn = DownturnCalculator().calculate(product, datetime.utcnow())
        self.assertEqual({
            123: {
                's': 0,
                'l': 4,
                'p': -1
            },
            321: {
                's': 0,
                'l': -1,
                'p': 6
            }
        }, downturn)


if __name__ == '__main__':
    unittest.main()
