#!/usr/bin/env python3

from eth_account.datastructures import SignedTransaction
from web3.datastructures import AttributeDict
from web3.contract import Contract
from web3 import Web3
from web3.types import Wei
from typing import (
    Optional, Union
)
from base64 import b64encode

import json

from ...exceptions import (
    AddressError, NetworkError, UnitError
)
from ...utils import clean_transaction_raw
from ..config import xinfin as config
from .wallet import Wallet
from .htlc import HTLC
from .rpc import get_web3
from .utils import (
    is_network, is_address, to_checksum_address, amount_unit_converter
)
from .solver import (
    FundSolver, WithdrawSolver, RefundSolver
)


class Transaction:
    """
    XinFin Transaction.

    :param network: XinFin network, defaults to ``mainnet``.
    :type network: str
    :param provider: XinFin network provider, defaults to ``http``.
    :type provider: str

    :returns: Transaction -- XinFin transaction instance.

    .. note::
        XinFin has only three networks, ``mainnet`` and ``testnet``.
    """

    def __init__(self, network: str = config["network"], provider: str = config["provider"],
                 token: Optional[str] = None):

        # Check parameter instances
        if not is_network(network=network):
            raise NetworkError(f"Invalid XinFin '{network}' network",
                               "choose only 'mainnet', 'ropsten', 'kovan', 'rinkeby' or 'testnet' networks.")

        self._network: str = network
        self.web3: Web3 = get_web3(
            network=network, provider=provider
        )

        self._transaction: Optional[dict] = None
        self._signature: Optional[dict] = None
        self._type: Optional[str] = None
        self._fee: Optional[Wei] = None

    def fee(self, unit: str = config["unit"]) -> Union[Wei, int, float]:
        """
        Get XinFin transaction fee.

        :param unit: XinFin unit, default to ``Wei``.
        :type unit: str

        :returns: Wei, int, float -- XinFin transaction fee.

        >>> from swap.providers.xinfin.htlc import HTLC
        >>> from swap.providers.xinfin.transaction import FundTransaction
        >>> from swap.utils import sha256, get_current_timestamp
        >>> htlc: HTLC = HTLC(network="mainnet")
        >>> htlc.build_htlc(secret_hash=sha256("Hello Meheret!"), recipient_address="xdcd77E0d2Eef905cfB39c3C4b952Ed278d58f96E1f", sender_address="xdc69e04fe16c9A6A83076B3c2dc4b4Bc21b5d9A20C", endtime=(get_current_timestamp() + 300))
        >>> fund_transaction: FundTransaction = FundTransaction(network="mainnet")
        >>> fund_transaction.build_transaction(address="xdc69e04fe16c9A6A83076B3c2dc4b4Bc21b5d9A20C", htlc=htlc, amount=100_000_000)
        >>> fund_transaction.fee(unit="Wei")
        1532774
        """

        # Check transaction
        if not self._transaction:
            raise ValueError("Transaction is none, build transaction first.")

        if unit not in ["XDC", "Gwei", "Wei"]:
            raise UnitError(f"Invalid XinFin '{unit}' unit", "choose only 'XDC', 'Gwei' or 'Wei' units.")
        return self._fee if unit == "Wei" else \
            amount_unit_converter(amount=self._fee, unit=f"Wei2{unit}")

    def hash(self) -> Optional[str]:
        """
        Get XinFin transaction hash.

        :returns: str -- XinFin transaction hash.

        >>> from swap.providers.xinfin.transaction import WithdrawTransaction
        >>> from swap.providers.xinfin.solver import WithdrawSolver
        >>> withdraw_transaction: WithdrawTransaction = WithdrawTransaction(network="mainnet")
        >>> withdraw_transaction.build_transaction(transaction_hash="0xe49ff507739f8d916ae2c9fd51dd63764658ffa42a5288a49d93bc70a933edc4", secret_key="Hello Meheret!", address="xdc69e04fe16c9A6A83076B3c2dc4b4Bc21b5d9A20C", htlc_transaction_hash="0x728c83cc83bb4b1a67fbfd480a9bdfdd55cb5fc6fd519f6a98fa35db3a2a9160")
        >>> withdraw_solver: WithdrawSolver = WithdrawSolver(xprivate_key="xprv9s21ZrQH143K3Y3pdbkbjreZQ9RVmqTLhRgf86uZyCJk2ou36YdUJt5frjwihGWmV1fQEDioiGZXWXUbHLy3kQf5xmhvhp8dZ2tfn6tgGUj", address=1)
        >>> withdraw_transaction.sign(solver=withdraw_solver)
        >>> withdraw_transaction.hash()
        "0x9bbf83e56fea4cd9d23e000e8273551ba28317e4d3c311a49be919b305feb711"
        """

        # Check transaction
        if not self._transaction:
            raise ValueError("Transaction is none, build transaction first.")

        return self._signature["hash"] if self._signature else None

    def json(self) -> dict:
        """
        Get XinFin transaction fee.

        :returns: Wei, int, float -- XinFin transaction fee.

        >>> from swap.providers.xinfin.htlc import HTLC
        >>> from swap.providers.xinfin.transaction import FundTransaction
        >>> from swap.utils import sha256, get_current_timestamp
        >>> htlc: HTLC = HTLC(network="mainnet")
        >>> htlc.build_htlc(secret_hash=sha256("Hello Meheret!"), recipient_address="xdcd77E0d2Eef905cfB39c3C4b952Ed278d58f96E1f", sender_address="xdc69e04fe16c9A6A83076B3c2dc4b4Bc21b5d9A20C", endtime=(get_current_timestamp() + 300))
        >>> fund_transaction: FundTransaction = FundTransaction(network="mainnet")
        >>> fund_transaction.build_transaction(address="xdc69e04fe16c9A6A83076B3c2dc4b4Bc21b5d9A20C", htlc=htlc, amount=100_000_000)
        >>> fund_transaction.json()
        {'chainId': 1337, 'from': 'xdc69e04fe16c9A6A83076B3c2dc4b4Bc21b5d9A20C', 'value': 3000000000000000000, 'nonce': 0, 'gas': 22488, 'gasPrice': 20000000000, 'to': '0xeaEaC81da5E386E8Ca4De1e64d40a10E468A5b40', 'data': '0xf4fd30623a26da82ead15a80533a02696656b14b5dbfd84eb14790f2e1be5e9e45820eeb000000000000000000000000d77e0d2eef905cfb39c3c4b952ed278d58f96e1f00000000000000000000000069e04fe16c9a6a83076b3c2dc4b4bc21b5d9a20c0000000000000000000000000000000000000000000000000000000060ce0ab6'}
        """

        # Check transaction
        if not self._transaction:
            raise ValueError("Transaction is none, build transaction first.")

        return self._transaction

    def raw(self) -> Optional[str]:
        """
        Get XinFin transaction hash.

        :returns: str -- XinFin transaction hash.

        >>> from swap.providers.xinfin.transaction import RefundTransaction
        >>> from swap.providers.xinfin.solver import RefundSolver
        >>> refund_transaction: RefundTransaction = RefundTransaction(network="mainnet")
        >>> refund_transaction.build_transaction(transaction_hash="0xe49ff507739f8d916ae2c9fd51dd63764658ffa42a5288a49d93bc70a933edc4", address="xdc69e04fe16c9A6A83076B3c2dc4b4Bc21b5d9A20C", htlc_transaction_hash="0x728c83cc83bb4b1a67fbfd480a9bdfdd55cb5fc6fd519f6a98fa35db3a2a9160")
        >>> refund_solver: RefundSolver = RefundSolver(xprivate_key="xprv9s21ZrQH143K3Y3pdbkbjreZQ9RVmqTLhRgf86uZyCJk2ou36YdUJt5frjwihGWmV1fQEDioiGZXWXUbHLy3kQf5xmhvhp8dZ2tfn6tgGUj", address=0)
        >>> refund_transaction.sign(solver=refund_solver)
        >>> refund_transaction.hash()
        "0x9bbf83e56fea4cd9d23e000e8273551ba28317e4d3c311a49be919b305feb711"
        """

        # Check transaction
        if not self._transaction:
            raise ValueError("Transaction is none, build transaction first.")

        return self._signature["rawTransaction"] if self._signature else None

    def type(self) -> str:
        """
        Get XinFin transaction hash.

        :returns: str -- XinFin transaction hash.

        >>> from swap.providers.xinfin.transaction import WithdrawTransaction
        >>> from swap.providers.xinfin.solver import WithdrawSolver
        >>> withdraw_transaction: WithdrawTransaction = WithdrawTransaction(network="mainnet")
        >>> withdraw_transaction.build_transaction(transaction_hash="0xe49ff507739f8d916ae2c9fd51dd63764658ffa42a5288a49d93bc70a933edc4", secret_key="Hello Meheret!", address="xdc69e04fe16c9A6A83076B3c2dc4b4Bc21b5d9A20C", htlc_transaction_hash="0x728c83cc83bb4b1a67fbfd480a9bdfdd55cb5fc6fd519f6a98fa35db3a2a9160")
        >>> withdraw_transaction.type()
        "xinfin_withdraw_unsigned"
        """

        # Check transaction
        if not self._transaction:
            raise ValueError("Transaction is none, build transaction first.")

        return self._type

    def signature(self) -> dict:
        """
        Get XinFin transaction hash.

        :returns: str -- XinFin transaction hash.

        >>> from swap.providers.xinfin.transaction import RefundTransaction
        >>> from swap.providers.xinfin.solver import RefundSolver
        >>> refund_transaction: RefundTransaction = RefundTransaction(network="mainnet")
        >>> refund_transaction.build_transaction(transaction_hash="0xe49ff507739f8d916ae2c9fd51dd63764658ffa42a5288a49d93bc70a933edc4", address="xdc69e04fe16c9A6A83076B3c2dc4b4Bc21b5d9A20C", htlc_transaction_hash="0x728c83cc83bb4b1a67fbfd480a9bdfdd55cb5fc6fd519f6a98fa35db3a2a9160")
        >>> refund_solver: RefundSolver = RefundSolver(xprivate_key="xprv9s21ZrQH143K3Y3pdbkbjreZQ9RVmqTLhRgf86uZyCJk2ou36YdUJt5frjwihGWmV1fQEDioiGZXWXUbHLy3kQf5xmhvhp8dZ2tfn6tgGUj", address=0)
        >>> refund_transaction.sign(solver=refund_solver)
        >>> refund_transaction.signature()
        {'hash': '0x120241e6e89b54d90dc3a3f73d6353f83818c3d404c991d3b74691f000583396', 'rawTransaction': '0xf8f4018504a817c80083021cd094eaeac81da5e386e8ca4de1e64d40a10e468a5b408829a2241af62c0000b884f4fd30623a26da82ead15a80533a02696656b14b5dbfd84eb14790f2e1be5e9e45820eeb000000000000000000000000d77e0d2eef905cfb39c3c4b952ed278d58f96e1f00000000000000000000000069e04fe16c9a6a83076b3c2dc4b4bc21b5d9a20c0000000000000000000000000000000000000000000000000000000060ce40e8820a95a05d598fe47b96ef59b2a5b62a2793f499f1abce31938dc494b496b20969656cf4a063d515ee2a84d323a7f232eae4196e2e449a010eef52e6125b639b0b52fd2d2f', 'r': 42223337416619984402386667584480976881779168344975798352755076934920973937908, 's': 45155461792159514883067068644058913853180508583163102385805265017506142956847, 'v': 2709}
        """

        # Check transaction
        if not self._transaction:
            raise ValueError("Transaction is none, build transaction first.")

        return self._signature

    def transaction_raw(self) -> str:
        """
        Get XinFin fund transaction raw.

        :returns: str -- XinFin fund transaction raw.

        >>> from swap.providers.xinfin.htlc import HTLC
        >>> from swap.providers.xinfin.transaction import FundTransaction
        >>> from swap.utils import sha256, get_current_timestamp
        >>> htlc: HTLC = HTLC(network="mainnet")
        >>> htlc.build_htlc(secret_hash=sha256("Hello Meheret!"), recipient_address="xdcd77E0d2Eef905cfB39c3C4b952Ed278d58f96E1f", sender_address="xdc69e04fe16c9A6A83076B3c2dc4b4Bc21b5d9A20C", endtime=(get_current_timestamp() + 300))
        >>> fund_transaction: FundTransaction = FundTransaction(network="mainnet")
        >>> fund_transaction.build_transaction(address="xdc69e04fe16c9A6A83076B3c2dc4b4Bc21b5d9A20C", htlc=htlc, amount=100_000_000)
        >>> fund_transaction.transaction_raw()
        "eyJmZWUiOiAxMzg0NDgsICJ0cmFuc2FjdGlvbiI6IHsiY2hhaW5JZCI6IDEzMzcsICJmcm9tIjogIjB4NjllMDRmZTE2YzlBNkE4MzA3NkIzYzJkYzRiNEJjMjFiNWQ5QTIwQyIsICJ2YWx1ZSI6IDMwMDAwMDAwMDAwMDAwMDAwMDAsICJub25jZSI6IDEsICJnYXMiOiAxMzg0NDgsICJnYXNQcmljZSI6IDIwMDAwMDAwMDAwLCAidG8iOiAiMHhlYUVhQzgxZGE1RTM4NkU4Q2E0RGUxZTY0ZDQwYTEwRTQ2OEE1YjQwIiwgImRhdGEiOiAiMHhmNGZkMzA2MjNhMjZkYTgyZWFkMTVhODA1MzNhMDI2OTY2NTZiMTRiNWRiZmQ4NGViMTQ3OTBmMmUxYmU1ZTllNDU4MjBlZWIwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDBkNzdlMGQyZWVmOTA1Y2ZiMzljM2M0Yjk1MmVkMjc4ZDU4Zjk2ZTFmMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwNjllMDRmZTE2YzlhNmE4MzA3NmIzYzJkYzRiNGJjMjFiNWQ5YTIwYzAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwNjBjZTQwZTgifSwgInNpZ25hdHVyZSI6IG51bGwsICJuZXR3b3JrIjogInRlc3RuZXQiLCAidHlwZSI6ICJldGhlcmV1bV9mdW5kX3Vuc2lnbmVkIn0"
        """

        # Check transaction
        if not self._transaction:
            raise ValueError("Transaction is none, build transaction first.")

        return clean_transaction_raw(b64encode(str(json.dumps(dict(
            fee=self._fee,
            transaction=self._transaction,
            signature=self._signature,
            network=self._network,
            type=self._type
        ))).encode()).decode())


class FundTransaction(Transaction):
    """
    XinFin Fund transaction.

    :param network: XinFin network, defaults to ``mainnet``.
    :type network: str
    :param provider: XinFin network provider, defaults to ``http``.
    :type provider: str

    :returns: FundTransaction -- XinFin fund transaction instance.

    .. warning::
        Do not forget to build transaction after initialize fund transaction.
    """

    def __init__(self, network: str = config["network"], provider: str = config["provider"]):
        super().__init__(
            network=network, provider=provider
        )

    def build_transaction(self, address: str, htlc: HTLC, amount: Union[Wei, int]) -> "FundTransaction":
        """
        Build XinFin fund transaction.

        :param htlc: XinFin HTLC instance.
        :type htlc: xinfin.htlc.HTLC
        :param address: XinFin sender address.
        :type address: str
        :param amount: XinFin amount.
        :type amount: Wei, int

        :returns: FundTransaction -- XinFin fund transaction instance.

        >>> from swap.providers.xinfin.htlc import HTLC
        >>> from swap.providers.xinfin.transaction import FundTransaction
        >>> from swap.utils import sha256, get_current_timestamp
        >>> htlc: HTLC = HTLC(network="mainnet")
        >>> htlc.build_htlc(secret_hash=sha256("Hello Meheret!"), recipient_address="xdcd77E0d2Eef905cfB39c3C4b952Ed278d58f96E1f", sender_address="xdc69e04fe16c9A6A83076B3c2dc4b4Bc21b5d9A20C", endtime=(get_current_timestamp() + 300))
        >>> fund_transaction: FundTransaction = FundTransaction(network="mainnet")
        >>> fund_transaction.build_transaction(address="xdc69e04fe16c9A6A83076B3c2dc4b4Bc21b5d9A20C", htlc=htlc, amount=100_000_000)
        <swap.providers.xinfin.transaction.FundTransaction object at 0x0409DAF0>
        """

        # Check parameter instances
        if not isinstance(htlc, HTLC):
            raise TypeError("Invalid HTLC instance, only takes xinfin HTLC class")
        if not is_address(address=address):
            raise AddressError(f"Invalid XinFin sender '{address}' address.")
        if to_checksum_address(address=address, prefix="0x") != htlc.agreements["sender_address"]:
            raise AddressError(f"Wrong XinFin sender '{address}' address",
                               "address must be equal with HTLC agreements sender address.")

        htlc_contract: Contract = self.web3.eth.contract(
            address=htlc.contract_address(), abi=htlc.abi()
        )

        htlc_fund_function = htlc_contract.functions.fund(
            htlc.agreements["secret_hash"],  # Secret Hash
            htlc.agreements["recipient_address"],  # Recipient Address
            htlc.agreements["sender_address"],  # Sender Address
            htlc.agreements["endtime"]  # Locktime Seconds
        )

        self._fee = htlc_fund_function.estimateGas({
            "from": to_checksum_address(address=address, prefix="0x"),
            "value": Wei(amount),
            "nonce": self.web3.eth.get_transaction_count(
                to_checksum_address(address=address, prefix="0x")
            ),
            "gasPrice": self.web3.eth.gasPrice
        })

        self._transaction = htlc_fund_function.buildTransaction({
            "from": to_checksum_address(address=address, prefix="0x"),
            "value": Wei(amount),
            "nonce": self.web3.eth.get_transaction_count(
                to_checksum_address(address=address, prefix="0x")
            ),
            "gas": self._fee,
            "gasPrice": self.web3.eth.gasPrice
        })
        self._type = "xinfin_fund_unsigned"
        return self

    def sign(self, solver: FundSolver) -> "FundTransaction":
        """
        Sign XinFin fund transaction.

        :param solver: XinFin fund solver.
        :type solver: xinfin.solver.FundSolver

        :returns: FundTransaction -- XinFin fund transaction instance.

        >>> from swap.providers.xinfin.htlc import HTLC
        >>> from swap.providers.xinfin.transaction import FundTransaction
        >>> from swap.providers.xinfin.solver import FundSolver
        >>> from swap.utils import sha256, get_current_timestamp
        >>> htlc: HTLC = HTLC(network="mainnet")
        >>> htlc.build_htlc(secret_hash=sha256("Hello Meheret!"), recipient_address="xdcd77E0d2Eef905cfB39c3C4b952Ed278d58f96E1f", sender_address="xdc69e04fe16c9A6A83076B3c2dc4b4Bc21b5d9A20C", endtime=(get_current_timestamp() + 300))
        >>> fund_transaction: FundTransaction = FundTransaction(network="mainnet")
        >>> fund_transaction.build_transaction(address="xdc69e04fe16c9A6A83076B3c2dc4b4Bc21b5d9A20C", htlc=htlc, amount=100_000_000)
        >>> fund_solver: FundSolver = FundSolver(xprivate_key="xprv9s21ZrQH143K3Y3pdbkbjreZQ9RVmqTLhRgf86uZyCJk2ou36YdUJt5frjwihGWmV1fQEDioiGZXWXUbHLy3kQf5xmhvhp8dZ2tfn6tgGUj", address=0)
        >>> fund_transaction.sign(solver=fund_solver)
        <swap.providers.xinfin.transaction.FundTransaction object at 0x0409DAF0>
        """

        # Check parameter instances
        if not isinstance(solver, FundSolver):
            raise TypeError(f"Solver must be XinFin FundSolver, not {type(solver).__name__} type.")

        wallet: Wallet = solver.solve()
        signed_fund_transaction: SignedTransaction = self.web3.eth.account.sign_transaction(
            transaction_dict=self._transaction,
            private_key=wallet.private_key()
        )

        self._signature = dict(
            hash=signed_fund_transaction["hash"].hex(),
            rawTransaction=signed_fund_transaction["rawTransaction"].hex(),
            r=signed_fund_transaction["r"],
            s=signed_fund_transaction["s"],
            v=signed_fund_transaction["v"]
        )
        self._type = "xinfin_fund_signed"
        return self


class WithdrawTransaction(Transaction):
    """
    XinFin Withdraw transaction.

    :param network: XinFin network, defaults to ``mainnet``.
    :type network: str
    :param provider: XinFin network provider, defaults to ``http``.
    :type provider: str

    :returns: WithdrawTransaction -- XinFin withdraw transaction instance.

    .. warning::
        Do not forget to build transaction after initialize withdraw transaction.
    """

    def __init__(self, network: str = config["network"], provider: str = config["provider"]):
        super().__init__(
            network=network, provider=provider
        )

    def build_transaction(self, transaction_hash: str, address: str, secret_key: str,
                          htlc_transaction_hash: Optional[str] = None) -> "WithdrawTransaction":
        """
        Build XinFin withdraw transaction.

        :param transaction_hash: XinFin HTLC funded transaction hash.
        :type transaction_hash: str
        :param address: XinFin recipient address.
        :type address: str
        :param secret_key: Secret password/passphrase.
        :type secret_key: str
        :param htlc_transaction_hash: XinFin HTLC transaction hash, defaults to ``None``.
        :type htlc_transaction_hash: str

        :returns: WithdrawTransaction -- XinFin withdraw transaction instance.

        >>> from swap.providers.xinfin.transaction import WithdrawTransaction
        >>> withdraw_transaction: WithdrawTransaction = WithdrawTransaction(network="mainnet")
        >>> withdraw_transaction.build_transaction(transaction_hash="0xe49ff507739f8d916ae2c9fd51dd63764658ffa42a5288a49d93bc70a933edc4", secret_key="Hello Meheret!", address="xdc69e04fe16c9A6A83076B3c2dc4b4Bc21b5d9A20C", htlc_transaction_hash="0x728c83cc83bb4b1a67fbfd480a9bdfdd55cb5fc6fd519f6a98fa35db3a2a9160")
        <swap.providers.xinfin.transaction.WithdrawTransaction object at 0x0409DAF0>
        """

        # Check parameter instances
        if not is_address(address=address):
            raise AddressError(f"Invalid XinFin recipient '{address}' address.")

        htlc: HTLC = HTLC(
            transaction_hash=htlc_transaction_hash, network=self._network
        )
        htlc_contract: Contract = self.web3.eth.contract(
            address=htlc.contract_address(), abi=htlc.abi()
        )

        transaction_receipt: AttributeDict = self.web3.eth.get_transaction_receipt(transaction_hash)
        log_fund: AttributeDict = htlc_contract.events.log_fund().processLog(
            log=transaction_receipt["logs"][0]
        )

        locked_contract_id: str = log_fund["args"]["locked_contract_id"]
        htlc_fund_function = htlc_contract.functions.withdraw(
            locked_contract_id,  # Locked Contract ID
            secret_key  # Secret Key
        )

        self._fee = htlc_fund_function.estimateGas({
            "from": to_checksum_address(address=address, prefix="0x"),
            "value": Wei(0),
            "nonce": self.web3.eth.get_transaction_count(
                to_checksum_address(address=address, prefix="0x")
            ),
            "gasPrice": self.web3.eth.gasPrice
        })

        self._transaction = htlc_fund_function.buildTransaction({
            "from": to_checksum_address(address=address, prefix="0x"),
            "value": Wei(0),
            "nonce": self.web3.eth.get_transaction_count(
                to_checksum_address(address=address, prefix="0x")
            ),
            "gas": self._fee,
            "gasPrice": self.web3.eth.gasPrice
        })
        self._type = "xinfin_withdraw_unsigned"
        return self

    def sign(self, solver: WithdrawSolver) -> "WithdrawTransaction":
        """
        Sign XinFin withdraw transaction.

        :param solver: XinFin withdraw solver.
        :type solver: xinfin.solver.WithdrawSolver

        :returns: WithdrawTransaction -- XinFin withdraw transaction instance.

        >>> from swap.providers.xinfin.transaction import WithdrawTransaction
        >>> from swap.providers.xinfin.solver import WithdrawSolver
        >>> withdraw_transaction: WithdrawTransaction = WithdrawTransaction(network="mainnet")
        >>> withdraw_transaction.build_transaction(transaction_hash="0xe49ff507739f8d916ae2c9fd51dd63764658ffa42a5288a49d93bc70a933edc4", secret_key="Hello Meheret!", address="xdc69e04fe16c9A6A83076B3c2dc4b4Bc21b5d9A20C", htlc_transaction_hash="0x728c83cc83bb4b1a67fbfd480a9bdfdd55cb5fc6fd519f6a98fa35db3a2a9160")
        >>> withdraw_solver: WithdrawSolver = WithdrawSolver(xprivate_key="xprv9s21ZrQH143K3Y3pdbkbjreZQ9RVmqTLhRgf86uZyCJk2ou36YdUJt5frjwihGWmV1fQEDioiGZXWXUbHLy3kQf5xmhvhp8dZ2tfn6tgGUj", address=1)
        >>> withdraw_transaction.sign(solver=withdraw_solver)
        <swap.providers.xinfin.transaction.WithdrawTransaction object at 0x0409DAF0>
        """

        # Check parameter instances
        if not isinstance(solver, WithdrawSolver):
            raise TypeError(f"Solver must be XinFin WithdrawSolver, not {type(solver).__name__} type.")

        wallet: Wallet = solver.solve()
        signed_withdraw_transaction: SignedTransaction = self.web3.eth.account.sign_transaction(
            transaction_dict=self._transaction,
            private_key=wallet.private_key()
        )

        self._signature = dict(
            hash=signed_withdraw_transaction["hash"].hex(),
            rawTransaction=signed_withdraw_transaction["rawTransaction"].hex(),
            r=signed_withdraw_transaction["r"],
            s=signed_withdraw_transaction["s"],
            v=signed_withdraw_transaction["v"]
        )
        self._type = "xinfin_withdraw_signed"
        return self


class RefundTransaction(Transaction):
    """
    XinFin Refund transaction.

    :param network: XinFin network, defaults to ``mainnet``.
    :type network: str
    :param provider: XinFin network provider, defaults to ``http``.
    :type provider: str

    :returns: RefundTransaction -- XinFin refund transaction instance.

    .. warning::
        Do not forget to build transaction after initialize refund transaction.
    """

    def __init__(self, network: str = config["network"], provider: str = config["provider"]):
        super().__init__(
            network=network, provider=provider
        )

    def build_transaction(self, transaction_hash: str, address: str,
                          htlc_transaction_hash: Optional[str] = None) -> "RefundTransaction":
        """
        Build XinFin refund transaction.

        :param transaction_hash: XinFin HTLC funded transaction hash.
        :type transaction_hash: str
        :param address: XinFin sender address.
        :type address: str
        :param htlc_transaction_hash: XinFin HTLC transaction hash, defaults to ``None``.
        :type htlc_transaction_hash: str

        :returns: RefundTransaction -- XinFin refund transaction instance.

        >>> from swap.providers.xinfin.transaction import RefundTransaction
        >>> refund_transaction: RefundTransaction = RefundTransaction(network="mainnet")
        >>> refund_transaction.build_transaction(transaction_hash="0xe49ff507739f8d916ae2c9fd51dd63764658ffa42a5288a49d93bc70a933edc4", address="xdc69e04fe16c9A6A83076B3c2dc4b4Bc21b5d9A20C", htlc_transaction_hash="0x728c83cc83bb4b1a67fbfd480a9bdfdd55cb5fc6fd519f6a98fa35db3a2a9160")
        <swap.providers.xinfin.transaction.RefundTransaction object at 0x0409DAF0>
        """

        # Check parameter instances
        if not is_address(address=address):
            raise AddressError(f"Invalid XinFin recipient '{address}' address.")

        htlc: HTLC = HTLC(
            transaction_hash=htlc_transaction_hash, network=self._network
        )
        htlc_contract: Contract = self.web3.eth.contract(
            address=htlc.contract_address(), abi=htlc.abi()
        )

        transaction_receipt: AttributeDict = self.web3.eth.get_transaction_receipt(transaction_hash)
        log_fund: AttributeDict = htlc_contract.events.log_fund().processLog(
            log=transaction_receipt["logs"][0]
        )

        locked_contract_id: str = log_fund["args"]["locked_contract_id"]
        htlc_refund_function = htlc_contract.functions.refund(
            locked_contract_id,  # Locked Contract ID
        )

        self._fee = htlc_refund_function.estimateGas({
            "from": to_checksum_address(address=address, prefix="0x"),
            "value": Wei(0),
            "nonce": self.web3.eth.get_transaction_count(
                to_checksum_address(address=address, prefix="0x")
            ),
            "gasPrice": self.web3.eth.gasPrice
        })

        self._transaction = htlc_refund_function.buildTransaction({
            "from": to_checksum_address(address=address, prefix="0x"),
            "value": Wei(0),
            "nonce": self.web3.eth.get_transaction_count(
                to_checksum_address(address=address, prefix="0x")
            ),
            "gas": self._fee,
            "gasPrice": self.web3.eth.gasPrice
        })
        self._type = "xinfin_refund_unsigned"
        return self

    def sign(self, solver: RefundSolver) -> "RefundTransaction":
        """
        Sign XinFin refund transaction.

        :param solver: XinFin refund solver.
        :type solver: xinfin.solver.RefundSolver

        :returns: RefundTransaction -- XinFin refund transaction instance.

        >>> from swap.providers.xinfin.transaction import RefundTransaction
        >>> from swap.providers.xinfin.solver import RefundSolver
        >>> refund_transaction: RefundTransaction = RefundTransaction(network="mainnet")
        >>> refund_transaction.build_transaction(transaction_hash="0xe49ff507739f8d916ae2c9fd51dd63764658ffa42a5288a49d93bc70a933edc4", address="xdc69e04fe16c9A6A83076B3c2dc4b4Bc21b5d9A20C", htlc_transaction_hash="0x728c83cc83bb4b1a67fbfd480a9bdfdd55cb5fc6fd519f6a98fa35db3a2a9160")
        >>> refund_solver: RefundSolver = RefundSolver(xprivate_key="xprv9s21ZrQH143K3Y3pdbkbjreZQ9RVmqTLhRgf86uZyCJk2ou36YdUJt5frjwihGWmV1fQEDioiGZXWXUbHLy3kQf5xmhvhp8dZ2tfn6tgGUj", address=0)
        >>> refund_transaction.sign(solver=refund_solver)
        <swap.providers.xinfin.transaction.RefundTransaction object at 0x0409DAF0>
        """

        # Check parameter instances
        if not isinstance(solver, RefundSolver):
            raise TypeError(f"Solver must be XinFin RefundSolver, not {type(solver).__name__} type.")

        wallet: Wallet = solver.solve()
        signed_refund_transaction: SignedTransaction = self.web3.eth.account.sign_transaction(
            transaction_dict=self._transaction,
            private_key=wallet.private_key()
        )

        self._signature = dict(
            hash=signed_refund_transaction["hash"].hex(),
            rawTransaction=signed_refund_transaction["rawTransaction"].hex(),
            r=signed_refund_transaction["r"],
            s=signed_refund_transaction["s"],
            v=signed_refund_transaction["v"]
        )
        self._type = "xinfin_refund_signed"
        return self
