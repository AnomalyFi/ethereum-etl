
from blockchainetl.jobs.exporters.composite_item_exporter import CompositeItemExporter

FIELDS_TO_EXPORT = [
    'contract_address',
    'from_address',
    'to_address',
    'amount',
    'token_type',
    'token_id',
    'transaction_hash',
    'log_index',
    'block_number',
    'chain_id'
]


def token_transfers_v2_item_exporter(token_transfer_output, converters=()):
    return CompositeItemExporter(
        filename_mapping={
            'token_transfer_v2': token_transfer_output
        },
        field_mapping={
            'token_transfer_v2': FIELDS_TO_EXPORT
        },
        converters=converters
    )
