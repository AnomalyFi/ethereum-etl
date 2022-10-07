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
from typing import Callable, List
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.eth import Eth
from web3._utils.rpc_abi import RPC
from web3.method import Method, default_root_munger
from web3.types import BlockIdentifier, ParityBlockTrace, RPCEndpoint

get_block_receipts: Method[Callable[[BlockIdentifier], List[dict]]] = Method(
    RPCEndpoint("eth_getBlockReceipts"),
    mungers=[default_root_munger],
)
Eth.get_block_receipts = get_block_receipts


def build_web3(provider):
    w3 = Web3(provider, modules={"eth": (Eth,)})
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3
