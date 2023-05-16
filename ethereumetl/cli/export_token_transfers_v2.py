import click

from ethereumetl.web3_utils import build_web3

from ethereumetl.jobs.export_token_transfers_job_v2 import ExportTokenTransfersJobV2
from ethereumetl.jobs.exporters.token_transfers_v2_item_exporter import token_transfers_v2_item_exporter
from blockchainetl.logging_utils import logging_basic_config
from ethereumetl.providers.auto import get_provider_from_uri
from ethereumetl.thread_local_proxy import ThreadLocalProxy

logging_basic_config()


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-s', '--start-block', default=0, show_default=True, type=int, help='Start block')
@click.option('-e', '--end-block', required=True, type=int, help='End block')
@click.option('-b', '--batch-size', default=100, show_default=True, type=int, help='The number of blocks to filter at a time.')
@click.option('-o', '--output', default='-', show_default=True, type=str, help='The output file. If not specified stdout is used.')
@click.option('-w', '--max-workers', default=5, show_default=True, type=int, help='The maximum number of workers.')
@click.option('-p', '--provider-uri', required=True, type=str,
              help='The URI of the web3 provider e.g. file://$HOME/Library/Ethereum/geth.ipc or http://localhost:8545/')
@click.option('-t', '--tokens', default=None, show_default=True, type=str, multiple=True, help='The list of token addresses to filter by.')
def export_token_transfers_v2(start_block, end_block, batch_size, output, max_workers, provider_uri, tokens):
    """Exports ERC20/ERC721/ERC1155 transfers."""
    job = ExportTokenTransfersJobV2(
        start_block=start_block,
        end_block=end_block,
        batch_size=batch_size,
        web3=ThreadLocalProxy(lambda: build_web3(get_provider_from_uri(provider_uri))),
        token_transfers_v2_exporter=token_transfers_v2_item_exporter(output),
        max_workers=max_workers,
        tokens=tokens)
    job.run()
