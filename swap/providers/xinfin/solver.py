#!/usr/bin/env python3

from typing import Optional

from ..config import xinfin as config
from .wallet import Wallet


class FundSolver:
    """
    XinFin Fund solver.

    :param xprivate_key: XinFin sender xprivate key.
    :type xprivate_key: str
    :param account: XinFin derivation account, defaults to 0.
    :type account: int
    :param change: XinFin derivation change, defaults to False.
    :type change: bool
    :param address: XinFin derivation address, defaults to 0.
    :type address: int
    :param path: XinFin derivation path, defaults to None.
    :type path: str

    :returns: FundSolver -- XinFin fund solver instance.

    >>> from swap.providers.xinfin.solver import FundSolver
    >>> sender_root_xprivate_key: str = "xprv9s21ZrQH143K3XihXQBN8Uar2WBtrjSzK2oRDEGQ25pA2kKAADoQXaiiVXht163ZTrdtTXfM4GqNRE9gWQHky25BpvBQuuhNCM3SKwWTPNJ"
    >>> fund_solver: FundSolver = FundSolver(xprivate_key=sender_root_xprivate_key)
    <swap.providers.xinfin.solver.FundSolver object at 0x03FCCA60>
    """

    def __init__(self, xprivate_key: str, account: int = 0,
                 change: bool = False, address: int = 0, path: Optional[str] = None):
        if path is None:
            path = config["BIP44"].format(
                account=account, change=(1 if change else 0), address=address
            )

        self._xprivate_key: str = xprivate_key
        self._path: Optional[str] = path

    def solve(self, network: str = config["network"]) -> Wallet:
        return Wallet(network=network).from_root_xprivate_key(
            xprivate_key=self._xprivate_key
        ).from_path(path=self._path)


class WithdrawSolver:
    """
    XinFin Withdraw solver.

    :param xprivate_key: XinFin sender xprivate key.
    :type xprivate_key: str
    :param account: XinFin derivation account, defaults to 0.
    :type account: int
    :param change: XinFin derivation change, defaults to False.
    :type change: bool
    :param address: XinFin derivation address, defaults to 0.
    :type address: int
    :param path: XinFin derivation path, defaults to None.
    :type path: str

    :returns: WithdrawSolver -- XinFin withdraw solver instance.

    >>> from swap.providers.xinfin.solver import WithdrawSolver
    >>> recipient_root_xprivate_key: str = "xprv9s21ZrQH143K3XihXQBN8Uar2WBtrjSzK2oRDEGQ25pA2kKAADoQXaiiVXht163ZTrdtTXfM4GqNRE9gWQHky25BpvBQuuhNCM3SKwWTPNJ"
    >>> withdraw_solver: WithdrawSolver = WithdrawSolver(xprivate_key=recipient_root_xprivate_key)
    <swap.providers.xinfin.solver.WithdrawSolver object at 0x03FCCA60>
    """

    def __init__(self, xprivate_key: str, account: int = 0,
                 change: bool = False, address: int = 0, path: Optional[str] = None):
        if path is None:
            path = config["BIP44"].format(
                account=account, change=(1 if change else 0), address=address
            )

        self._xprivate_key: str = xprivate_key
        self._path: Optional[str] = path

    def solve(self, network: str = config["network"]) -> Wallet:
        return Wallet(network=network).from_root_xprivate_key(
            xprivate_key=self._xprivate_key
        ).from_path(path=self._path)


class RefundSolver:
    """
    XinFin Refund solver.

    :param xprivate_key: XinFin sender xprivate key.
    :type xprivate_key: str
    :param account: XinFin derivation account, defaults to 0.
    :type account: int
    :param change: XinFin derivation change, defaults to False.
    :type change: bool
    :param address: XinFin derivation address, defaults to 0.
    :type address: int
    :param path: XinFin derivation path, defaults to None.
    :type path: str

    :returns: RefundSolver -- XinFin refund solver instance.

    >>> from swap.providers.xinfin.solver import RefundSolver
    >>> sender_root_xprivate_key: str = "xprv9s21ZrQH143K3XihXQBN8Uar2WBtrjSzK2oRDEGQ25pA2kKAADoQXaiiVXht163ZTrdtTXfM4GqNRE9gWQHky25BpvBQuuhNCM3SKwWTPNJ"
    >>> refund_solver: RefundSolver = RefundSolver(xprivate_key=sender_root_xprivate_key)
    <swap.providers.xinfin.solver.RefundSolver object at 0x03FCCA60>
    """

    def __init__(self, xprivate_key: str, account: int = 0,
                 change: bool = False, address: int = 0, path: Optional[str] = None):
        if path is None:
            path = config["BIP44"].format(
                account=account, change=(1 if change else 0), address=address
            )

        self._xprivate_key: str = xprivate_key
        self._path: Optional[str] = path

    def solve(self, network: str = config["network"]) -> Wallet:
        return Wallet(network=network).from_root_xprivate_key(
            xprivate_key=self._xprivate_key
        ).from_path(path=self._path)
