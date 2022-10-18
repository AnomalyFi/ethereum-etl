from typing import Callable, List

from web3._utils.rpc_abi import RPC
from web3.method import Method, default_root_munger
from web3.types import BlockIdentifier, ParityBlockTrace, RPCEndpoint

get_block_receipts: Method[Callable[[BlockIdentifier], List[dict]]] = Method(
    RPCEndpoint("eth_getBlockReceipts"),
    mungers=[default_root_munger],
)

