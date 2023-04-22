from jorm.market.items import Product


class DownturnCalculator:
    @staticmethod
    def calculate(product: Product, from_date) -> dict[int, dict[str, int]]:
        warehouse_id_to_downturn_days: dict[int, dict[str, int]] = {}
        all_leftovers = product.history.get_all_mapped_leftovers()
        downturns = product.history.get_leftovers_downturn(from_date)
        for warehouse_id in downturns:
            if warehouse_id in all_leftovers:
                if warehouse_id not in warehouse_id_to_downturn_days:
                    warehouse_id_to_downturn_days[warehouse_id] = {}
                for specify in downturns[warehouse_id]:
                    if specify in all_leftovers[warehouse_id]:
                        mean_downturn = \
                            abs(downturns[warehouse_id][specify].sum // downturns[warehouse_id][specify].count)
                        warehouse_id_to_downturn_days[warehouse_id][specify] = \
                            all_leftovers[warehouse_id][specify] // mean_downturn if mean_downturn > 0 else -1
                    else:
                        warehouse_id_to_downturn_days[warehouse_id][specify] = 0
        return warehouse_id_to_downturn_days
