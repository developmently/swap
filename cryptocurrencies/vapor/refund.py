#!/usr/bin/env python3

from swap.providers.vapor.wallet import Wallet
from swap.providers.vapor.transaction import RefundTransaction
from swap.providers.vapor.assets import BTM as ASSET
from swap.providers.vapor.solver import RefundSolver
from swap.providers.vapor.signature import RefundSignature
from swap.providers.vapor.utils import submit_transaction_raw

import json

# Choose network mainnet, solonet or testnet
NETWORK: str = "mainnet"
# Vapor funded transaction hash/id
TRANSACTION_HASH: str = "37b36d7be5dfda0cc5dc3c918705464ff901dc5eadb6f4f049db03a679e02bfe"
# Vapor sender wallet mnemonic
SENDER_MNEMONIC: str = "unfair divorce remind addict add roof park clown build renew illness fault"
# Vapor sender derivation path
SENDER_PATH: str = "m/44/153/1/0/1"
# Witness Hash Time Lock Contract (HTLC) bytecode
BYTECODE: str = "042ccf300720fe6b3fd4458291b19605d92837ae1060cc0237e68022b2eb9faf01a118226212203e0" \
                "a377ae4afa031d4551599d9bb7d5b27f4736d77f78cac4d476f0ffba5ae3e203a26da82ead15a8053" \
                "3a02696656b14b5dbfd84eb14790f2e1be5e9e45820eeb741f547a6416000000557aa888537a7cae7" \
                "cac631f000000537acd9f6972ae7cac00c0"

print("=" * 10, "Sender Vapor Account")

# Initialize Vapor sender wallet
sender_wallet: Wallet = Wallet(network=NETWORK)
# Get Vapor sender wallet from mnemonic
sender_wallet.from_mnemonic(mnemonic=SENDER_MNEMONIC)
# Drive Vapor sender wallet from path
sender_wallet.from_path(path=SENDER_PATH)

# Print some Vapor sender wallet info's
print("XPrivate Key:", sender_wallet.xprivate_key())
print("XPublic Key:", sender_wallet.xpublic_key())
print("Private Key:", sender_wallet.private_key())
print("Public Key:", sender_wallet.public_key())
print("Path:", sender_wallet.path())
print("Address:", sender_wallet.address())
print("Balance:", sender_wallet.balance(asset=ASSET, unit="BTM"), "BTM")

print("=" * 10, "Unsigned Refund Transaction")

# Initialize refund transaction
unsigned_refund_transaction: RefundTransaction = RefundTransaction(network=NETWORK)
# Build refund transaction
unsigned_refund_transaction.build_transaction(
    address=sender_wallet.address(),
    transaction_hash=TRANSACTION_HASH,
    asset=ASSET
)

print("Unsigned Refund Transaction Fee:", unsigned_refund_transaction.fee(unit="NEU"), "NEU")
print("Unsigned Refund Transaction Hash:", unsigned_refund_transaction.hash())
print("Unsigned Refund Transaction Main Raw:", unsigned_refund_transaction.raw())
# print("Unsigned Refund Transaction Json:", json.dumps(unsigned_refund_transaction.json(), indent=4))
print("Unsigned Refund Transaction Unsigned:", json.dumps(unsigned_refund_transaction.unsigned_datas(), indent=4))
print("Unsigned Refund Transaction Signatures:", json.dumps(unsigned_refund_transaction.signatures(), indent=4))
print("Unsigned Refund Transaction Type:", unsigned_refund_transaction.type())

unsigned_refund_transaction_raw: str = unsigned_refund_transaction.transaction_raw()
print("Unsigned Refund Transaction Raw:", unsigned_refund_transaction_raw)

print("=" * 10, "Signed Refund Transaction")

# Initialize refund solver
refund_solver: RefundSolver = RefundSolver(
    xprivate_key=sender_wallet.xprivate_key(),
    path=sender_wallet.path(),
    bytecode=BYTECODE
)

# Sign unsigned refund transaction
signed_refund_transaction: RefundTransaction = unsigned_refund_transaction.sign(refund_solver)

print("Signed Refund Transaction Fee:", signed_refund_transaction.fee(unit="NEU"), "NEU")
print("Signed Refund Transaction Hash:", signed_refund_transaction.hash())
print("Signed Refund Transaction Main Raw:", signed_refund_transaction.raw())
# print("Signed Refund Transaction Json:", json.dumps(signed_refund_transaction.json(), indent=4))
print("Signed Refund Transaction Unsigned Datas:", json.dumps(signed_refund_transaction.unsigned_datas(), indent=4))
print("Signed Refund Transaction Signatures:", json.dumps(signed_refund_transaction.signatures(), indent=4))
print("Signed Refund Transaction Type:", signed_refund_transaction.type())

signed_refund_transaction_raw: str = signed_refund_transaction.transaction_raw()
print("Signed Refund Transaction Raw:", signed_refund_transaction_raw)

print("=" * 10, "Refund Signature")

# Initialize refund signature
refund_signature: RefundSignature = RefundSignature(network=NETWORK)
# Sign unsigned refund transaction raw
refund_signature.sign(
    transaction_raw=unsigned_refund_transaction_raw,
    solver=refund_solver
)

print("Refund Signature Fee:", refund_signature.fee(unit="NEU"), "NEU")
print("Refund Signature Hash:", refund_signature.hash())
print("Refund Signature Main Raw:", refund_signature.raw())
# print("Refund Signature Json:", json.dumps(refund_signature.json(), indent=4))
print("Refund Signature Unsigned Datas:", json.dumps(refund_signature.unsigned_datas(), indent=4))
print("Refund Signature Signatures:", json.dumps(refund_signature.signatures(), indent=4))
print("Refund Signature Type:", refund_signature.type())

signed_refund_signature_transaction_raw: str = refund_signature.transaction_raw()
print("Refund Signature Transaction Raw:", signed_refund_signature_transaction_raw)

# Check both signed refund transaction raws are equal
assert signed_refund_transaction_raw == signed_refund_signature_transaction_raw

# Submit refund transaction raw
# print("\nSubmitted Refund Transaction:", json.dumps(submit_transaction_raw(
#     transaction_raw=signed_refund_transaction_raw  # Or signed_refund_signature_transaction_raw
# ), indent=4))
