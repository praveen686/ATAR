from typing import List, Union

import pandas as pd
from auto_route.auto_route import APIAutoRouter
from nautilus_trader.persistence.catalog import ParquetDataCatalog

catalog_api = APIAutoRouter()
catalog_path = "/home/ruben/PycharmProjects/Genie-Trader/Data/catalog"  # todo change to dynamic and/or buckets
catalog = ParquetDataCatalog(catalog_path)


def default_procedure_for_instrument_ids_to_query(instrument_ids: str or List[str] = None,
                                                  use_literal_ids: bool = False):
    # Set local variables
    instrument_ids_to_query = instrument_ids

    # Get instruments in catalog
    all_instruments_data = catalog.instruments()

    # If single string, convert to list
    if isinstance(instrument_ids_to_query, str):
        instrument_ids_to_query = [instrument_ids_to_query]
    elif instrument_ids_to_query is None:
        return catalog.instruments().to_json()

    # Passed either id's or native symbols with use_literal_ids
    if not use_literal_ids:
        _instrument_ids = []
        for instrument_id in instrument_ids_to_query:
            result_id = all_instruments_data.id[all_instruments_data.id.str.match(instrument_id)].values[0]
            _instrument_ids.append(result_id)

        instrument_ids_to_query = _instrument_ids

    return instrument_ids_to_query


@catalog_api.register()
class CatalogController:

    @catalog_api.route()  # async
    def post_instruments(instrument_ids: str or List[str] = None, use_literal_ids: bool = False):
        instrument_ids_to_query = default_procedure_for_instrument_ids_to_query(instrument_ids, use_literal_ids)

        # Query instruments info for given id's
        selected_instruments_data = catalog.instruments(instrument_ids=instrument_ids_to_query)
        return {
            'data': selected_instruments_data.to_json()
        }

    @catalog_api.route()
    def get_quotes(start_date: Union[str, pd.Timestamp], end_date: Union[str, pd.Timestamp],
                   instrument_ids: Union[str, List[str]] , use_literal_ids: bool = False):
        instrument_ids_to_query = default_procedure_for_instrument_ids_to_query(instrument_ids, use_literal_ids)

        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)

        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date)

        try:
            ticks = catalog.quote_ticks(start=start_date, end=end_date, instrument_ids=instrument_ids_to_query)
            print(f'{ticks.head() = }')
            return {
                'data': ticks.to_json()
            }

        except Exception as e:
            print(f'{e = }')
            return {
                'data': None
            }


if __name__ == '__main__':
    from auto_app.auto_app import APIAutoApp

    # catalog_router_config = AutoLoadRouterConfigObject(
    #         module_path='api.py',
    #         router_names=['catalog_api'],
    #         init_classes=[
    #             InitClassObject(class_name='CatalogController'),
    #         ]
    #     )
    APIAutoApp(routers_list=[catalog_api.router]).run(host='localhost', port=8000)
