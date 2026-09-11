# CR080 checkpoint — 2026-09-11

## Valid screen: PASS to independent confirmation only

- Frozen corrected archive: cc9f30b833b292d3f735d6c821f3844e3fd3a0a3d840500616bb0369132a7a2d.
- Official runtime 1.32.7, isolated KaggleAgent loading, master 9112080.
- 8 paired seeds / 16 games: **10 wins, 6 losses**, 0 ties/errors/non-DONE.
- Each seat: 5 wins, 3 losses. Eight distinct seed worlds, not sixteen independent worlds.
- Score 0.625 meets the frozen discovery threshold. Paired bootstrap interval
  [0.25,0.875] remains wide; superiority is not established by this screen.
- Package reproduced byte-for-byte in GitHub run 34655053162, artifact 10284414571.
- Offline chronological composite 0.61030; descriptive only, no promotion claim.
- Contract tests caught injected exceptions/non-dict actions; actual entrypoint
  returned correct opening in both seats. Startup 2.3 sec uses official overage bank.

## Invalid initial screen

`invalid_loader_screen.json` is an engineering failure: NameError __file__ caused
719 non-dict actions each game, silently coerced to PASS by the old manual path.
Its zero-errors claim and 0-16 are invalid. It must never count as strategy evidence.
The raw result and original build provenance are preserved; the route bank and
selector remained unchanged by the mechanical path repair.

## Hosted checkpoint

API run 34655053172, artifact 10284539343: CR071M 56124705 rating 1728.2,
296 episodes listed. Latest 32 collected: 7 wins / 23 losses / 2 ties, score 0.25,
16 games per seat. CR070A 56091951 rating 1717.1 is the other active submission.
Current leader at snapshot: Majkel1337 3152.9; SpaTaro 3049.7. These are timed
snapshots, not final rank guarantees. Five submission allowances available.

## Next

Exactly one independent confirmation, run **34655496708**, master 9112081, 32 paired seeds per H2H.
Seven H2Hs / 448 games. CR080 vs incumbent + CR053/CR061/CR065; incumbent vs same
three guardrails. Gate and stop rule are in the protocol and executable aggregator.
PASS -> prepare one hosted probe that retires older CR070A; FAIL -> close CR080.
No automatic submission. Do not add extra validation after a clear gate result.
