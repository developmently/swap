#!/usr/bin/env python3

import pytest
import json
import os

from swap.utils.exceptions import APIError
from swap.providers.bitcoin.utils import (
    is_network, is_address, is_transaction_raw,
    decode_transaction_raw, submit_transaction_raw
)

# Test Values
base_path = os.path.dirname(__file__)
file_path = os.path.abspath(os.path.join(base_path, "..", "..", "values.json"))
values = open(file_path, "r")
_ = json.loads(values.read())
values.close()


def test_bitcoin_utils():

    assert is_network(network=_["bitcoin"]["network"])
    assert not is_network(network="unknown")

    assert is_address(address=_["bitcoin"]["wallet"]["sender"]["address"])
    assert not is_address(address=_["bitcoin"]["wallet"]["sender"]["address"], network="mainnet")
    assert is_address(address=_["bitcoin"]["wallet"]["sender"]["address"], network=_["bitcoin"]["network"])

    assert is_address(address=_["bitcoin"]["wallet"]["recipient"]["address"])
    assert not is_address(address=_["bitcoin"]["wallet"]["recipient"]["address"], network="mainnet")
    assert is_address(address=_["bitcoin"]["wallet"]["recipient"]["address"], network=_["bitcoin"]["network"])

    assert is_transaction_raw(transaction_raw=_["bitcoin"]["fund"]["unsigned"]["transaction_raw"])
    assert not is_transaction_raw(transaction_raw="unknown")

    assert decode_transaction_raw(transaction_raw=_["bitcoin"]["fund"]["unsigned"]["transaction_raw"]) == \
        {
            "fee": 678,
            "network": _["bitcoin"]["network"],
            "tx": _["bitcoin"]["fund"]["unsigned"]["json"],
            "type": "bitcoin_fund_unsigned"
        }

    # (REQ_ERROR) 16: mandatory-script-verify-flag-failed (Operation not valid with the current stack size)
    with pytest.raises(APIError):
        submit_transaction_raw(transaction_raw=_["bitcoin"]["fund"]["unsigned"]["transaction_raw"])
