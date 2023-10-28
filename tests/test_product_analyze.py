import unittest
from datetime import datetime

from jorm.market.items import Product

from jarvis_calc.calculators.product_analyze import DownturnCalculator, TurnoverCalculator, DownturnInfo
from tests.base_test import BaseCalcTest


class ProductAnalyzeTest(BaseCalcTest):
    def test_downturn_calculations(self):
        product_history = self.create_test_product_history()
        product = Product("product", 1000, 1, 3.4, "brand", "seller", "g", "g", product_history)
        downturn = DownturnCalculator().calculate(product, datetime.utcnow())
        self.assertEqual({
            123: {
                's': DownturnInfo(leftover=0, days=-1),
                'l': DownturnInfo(leftover=20, days=4),
                'p': DownturnInfo(leftover=35, days=-2)
            },
            321: {
                's': DownturnInfo(leftover=0, days=-1),
                'l': DownturnInfo(leftover=25, days=-2),
                'p': DownturnInfo(leftover=30, days=6)
            }
        }, downturn)

    def test_turnover_calculations(self):
        product_history = self.create_test_product_history()
        product = Product("product", 1000, 1, 3.4, "brand", "seller", "g", "g", product_history)
        turnover = TurnoverCalculator().calculate(product, datetime.utcnow())
        self.assertEqual({
            123: {
                's': 15.0,
                'l': 135.0,
                'p': 0
            },
            321: {
                's': 15.0,
                'l': 0,
                'p': 195.0
            }
        }, turnover)


if __name__ == '__main__':
    unittest.main()
