from ethereumetl.executors.batch_work_executor import BatchWorkExecutor
from blockchainetl.jobs.base_job import BaseJob
from ethereumetl.mappers.token_transfer_v2_mapper import EthTokenTransferV2Mapper
from ethereumetl.mappers.receipt_log_mapper import EthReceiptLogMapper
from ethereumetl.service.token_transfer_v2_extractor import EthTokenTransferV2Extractor, TRANSFER_EVENT_TOPICS
from ethereumetl.utils import validate_range


class ExportTokenTransfersJobV2(BaseJob):
    def __init__(
            self,
            start_block,
            end_block,
            batch_size,
            web3,
            token_transfers_v2_exporter,
            max_workers,
            tokens=None):
        validate_range(start_block, end_block)
        self.start_block = start_block
        self.end_block = end_block

        self.web3 = web3
        self.tokens = tokens

        self.token_transfers_v2_exporter = token_transfers_v2_exporter

        self.batch_work_executor = BatchWorkExecutor(batch_size, max_workers)

        self.receipt_log_mapper = EthReceiptLogMapper()
        
        self.token_transfer_v2_mapper = EthTokenTransferV2Mapper()

        self.token_transfer_v2_extractor = EthTokenTransferV2Extractor()

    def _start(self):
        self.token_transfers_v2_exporter.open()

    def _export(self):
        self.batch_work_executor.execute(
            range(self.start_block, self.end_block + 1),
            self._export_batch,
            total_items=self.end_block - self.start_block + 1
        )

    def _export_batch(self, block_number_batch):
        assert len(block_number_batch) > 0
        # https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getfilterlogs
        filter_params = {
            'fromBlock': block_number_batch[0],
            'toBlock': block_number_batch[-1],
            'topics': TRANSFER_EVENT_TOPICS
        }

        if self.tokens is not None and len(self.tokens) > 0:
            filter_params['address'] = self.tokens

        event_filter = self.web3.eth.filter(filter_params)
        events = event_filter.get_all_entries()
        for event in events:
            log = self.receipt_log_mapper.web3_dict_to_receipt_log(event)
            
            token_transfers_list_v2 = self.token_transfer_v2_extractor.extract_transfer_from_log(log)
            if token_transfers_list_v2 is not None:
                for token_transfer_v2 in token_transfers_list_v2:
                    self.token_transfers_v2_exporter.export_item(self.token_transfer_v2_mapper.token_transfer_to_dict(token_transfer_v2))

        self.web3.eth.uninstallFilter(event_filter.filter_id)

    def _end(self):
        self.batch_work_executor.shutdown()
        self.token_transfers_v2_exporter.close()
