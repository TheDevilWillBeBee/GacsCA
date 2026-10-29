# GBC5 receipt-link errata

The frozen GBC5 proof, SHA256
`bc64df9caf7d5e45da1341511256912159a874c73f49ecff2873d4143e37f41a`,
uses `../../../figs/...` for three receipt links. Their correct relative
root from that proof directory is `../../../../figs/...`. This is a
hyperlink correction only; the mathematical sources, exact asset hashes,
manifest and terminal replay remain unchanged.

The intended links are:

- [810 issued reader/ABI checks](../../../../figs/gray_counterexamples/unregistered_gbc5/GBC5_scratch_free_reader_attempt03.json).
- [104 complete diagnostics](../../../../figs/gray_counterexamples/unregistered_gbc5/GBC5_complete_diagnostic_attempt01.json).
- [Retained initial ownership-checker failure](../../../../figs/gray_counterexamples/unregistered_gbc5/GBC5_scratch_free_reader_attempt01.log).

The original proof is preserved without replacement. No new claim or
rule change is made by this note.
