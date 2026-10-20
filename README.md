# Stockroom Ledger

A transactional multi-location stock ledger with receive, issue and transfer operations, shortage protection, audit history and CSV export.

## Quick start

```sh
python stockroom.py --db demo.db receive NOTEBOOK MAIN 25 --ref SYN-RECEIPT-1
python stockroom.py --db demo.db transfer NOTEBOOK MAIN COUNTER 8 --ref SYN-TRANSFER-1
python stockroom.py --db demo.db stock
python stockroom.py --db demo.db history
python stockroom.py --db demo.db export stock.csv
```

## Tests

`python -m unittest discover -s tests -v`

## Scope and limitations

Local single-operator tool, not a network warehouse system. No accounts/authentication. Ledger is unencrypted; only invented inventory examples ship. Duplicate reference IDs are refused, preventing accidental replay; negative stock is prohibited. Timestamps use UTC. Quantities are whole units.

## Attribution and sample data

Built for Raj's portfolio with Wabi AI assistance. Sample data is invented and labelled synthetic; no real customer, employer or private account records are included. This is a learning/portfolio implementation, not a claim of commercial work or production deployment.

See source and tests for implementation decisions. Use invented data when exploring.

## How it works

CLI → validated movement → BEGIN IMMEDIATE → balance + movement insert → commit. Transfer updates both locations in one transaction; rejected operations roll back.

## Verified example

Receipt25 and transfer8 leave MAIN17/COUNTER8; a shortage99 is refused; CSV contains both positions. Unique movement reference prevents replay.

See [VALIDATION.md](VALIDATION.md) for tested environments and scope.
