# MIT License
#
# Copyright (c) 2018 Evgeny Medvedev, evge.medvedev@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import json

from blockchainetl.jobs.base_job import BaseJob
from ethereumetl.executors.batch_work_executor import BatchWorkExecutor
from ethereumetl.json_rpc_requests import generate_get_block_receipts_json_rpc, generate_get_alchemy_transaction_receipts_json_rpc
from ethereumetl.mappers.receipt_log_mapper import EthReceiptLogMapper
from ethereumetl.mappers.receipt_mapper import EthReceiptMapper
from ethereumetl.utils import rpc_response_batch_to_results, rpc_response_to_result
from ethereumetl.utils import validate_range
from ethereumetl.web3_utils import build_web3
from web3 import Web3


# Exports receipts and logs
class ExportReceiptsJob(BaseJob):
    def __init__(
            self,
            start_block,
            end_block,
            #transaction_hashes_iterable,
            batch_size,
            batch_web3_provider,
            max_workers,
            item_exporter,
            export_receipts=True,
            export_logs=True):
        validate_range(start_block, end_block)
        self.start_block = start_block
        self.end_block = end_block
        self.batch_web3_provider = batch_web3_provider
        #self.transaction_hashes_iterable = transaction_hashes_iterable
        # TODO: use batch_size for non alchemy requests
        self.batch_work_executor = BatchWorkExecutor(1, max_workers)
        self.item_exporter = item_exporter

        self.export_receipts = export_receipts
        self.export_logs = export_logs
        if not self.export_receipts and not self.export_logs:
            raise ValueError('At least one of export_receipts or export_logs must be True')

        self.receipt_mapper = EthReceiptMapper()
        self.receipt_log_mapper = EthReceiptLogMapper()

    def _start(self):
        self.item_exporter.open()

    def _export(self):
        #self.batch_work_executor.execute(self.transaction_hashes_iterable, self._export_receipt)
        self.batch_work_executor.execute(
            range(self.start_block, self.end_block + 1),
            self._export_receipts,
            total_items=self.end_block - self.start_block + 1
        )

    def _export_receipts(self, block_number_batch):
        assert len(block_number_batch) == 1
        block_number = block_number_batch[0]

        #receipts_rpc = list(generate_get_block_receipts_json_rpc(block_number_batch))
        receipts_rpc = generate_get_alchemy_transaction_receipts_json_rpc(block_number)
        response = self.batch_web3_provider.make_batch_request(json.dumps(receipts_rpc))
        result = rpc_response_to_result(response)
        #for res in results:
            #result = rpc_response_to_result(res)

        receipts = [self.receipt_mapper.json_dict_to_receipt(json_receipt) for json_receipt in result["receipts"]]
        for receipt in receipts:
            self._export_receipt(receipt)

    def _export_receipt(self, receipt):
        if self.export_receipts:
            #for x in receipts:
            self.item_exporter.export_item(self.receipt_mapper.receipt_to_dict(receipt))
        if self.export_logs:
            for log in receipt.logs:
                self.item_exporter.export_item(self.receipt_log_mapper.receipt_log_to_dict(log))

    # def _export_receipt(self, block_number_batch):
    #     assert len(block_number_batch) == 1
    #     block_number = block_number_batch[0]

    #     all_receipts = []

    #     # TODO: Change to traceFilter when this issue is fixed
    #     # https://github.com/paritytech/parity-ethereum/issues/9822
    #     block_hex = Web3.toHex(block_number)
    #     w3 = build_web3(self.batch_web3_provider)
    #     json_reciepts = w3.eth.get_block_receipts(block_hex)  # type: ignore

    #     if json_reciepts is None:
    #         raise ValueError('Response from the node is None. Is the node fully synced? Is the node started with receipts enabled? Is get_block_recipts API enabled?')

    #     receipts = [self.receipt_mapper.json_dict_to_receipt(json_receipt) for json_receipt in json_reciepts]
    #     all_receipts.extend(receipts)
            
    #     if self.export_receipts:
    #         for x in receipts:
    #             self.item_exporter.export_item(self.receipt_mapper.receipt_to_dict(x))
    #     if self.export_logs:
    #         for receipt in receipts: 
    #             for log in receipt.logs:
    #                 self.item_exporter.export_item(self.receipt_log_mapper.receipt_log_to_dict(log))

    
        
    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()
