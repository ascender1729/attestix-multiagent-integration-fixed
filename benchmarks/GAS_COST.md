# Gas Cost Analysis (V-7)

Source data: `export-0xf3Fda3af995B4409029C56900fC5E78E34554797.csv` (repo root)
Network: Base Sepolia testnet (Chain ID 84532)
Wallet: 0xf3Fda3af995B4409029C56900fC5E78E34554797
Period: 2026-05-11 11:14 - 11:30 UTC

## Per-transaction breakdown

| Block    | TX (truncated)  | Method   | Status                                  | Fee (ETH)  |
|----------|-----------------|----------|-----------------------------------------|------------|
| 41364881 | 0xdc81e16c...   | Register | Success                                 | 0.000001   |
| 41364883 | 0x219a833a...   | Attest   | Error in Main Txn : execution reverted  | 0.00000177 |
| 41365207 | 0xf3702424...   | Attest   | Error in Main Txn : execution reverted  | 0.00000177 |
| 41365382 | 0x107aa293...   | Attest   | Success                                 | 0.00000265 |

## Totals

- Total fees: **0.00000719 ETH** (sum of all four)
- Successful work: 0.000001 (schema register) + 0.00000265 (final attest) = **0.00000365 ETH**
- Wasted on reverts: 0.00000177 + 0.00000177 = **0.00000354 ETH** (**49.2% of total spend was on reverts before the gas-limit fix landed**)

## Interpretation

The two reverted attestation attempts (blocks 41364883 and 41365207) are the empirical evidence behind the 300k -> 600k gas-limit fix described in the report (Methodology section "Blockchain Anchoring"). Without the upstream library change, every attestation would have continued to revert and consume gas for nothing. The successful TX at block 41365382 confirms the fix works.

Operational implication for production:
- One successful EAS attestation on Base Sepolia testnet costs ~0.00000265 ETH (zero USD value on testnet, ~$0.008 at $3K ETH on mainnet at comparable gas conditions).
- One-time schema registration cost: ~0.000001 ETH.
- Reverted transactions still consume gas. The upstream library now uses the 600k limit by default to prevent this.

## Method

Computed by:
1. Reading `export-0xf3Fda3af995B4409029C56900fC5E78E34554797.csv` (committed at repo root, sourced from BaseScan export of the wallet's transaction history on 2026-05-11).
2. Summing the `Txn Fee` column.
3. Cross-referencing the `Status` column to separate successful spend from wasted-revert spend.

Reproducible: open the CSV in any spreadsheet and SUM the Txn Fee column.

## Reference

EAS Attestation UID for the final successful TX: 0xb2cdbd8583f4d2afc57d4a4859a89f3e...
Explorer: https://sepolia.basescan.org/tx/0x107aa293eea834a69d3fc7ff8bc3202e2608704184a9e9d9fd7fa3df5df7963f
