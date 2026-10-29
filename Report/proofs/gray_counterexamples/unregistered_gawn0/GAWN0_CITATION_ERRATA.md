# GAWN0 wording and citation errata

This note corrects wording in the frozen
[GAWN0 proof](GAWN0_NORMALIZED_NATIVE_EXECUTION_AND_PERIOD.md), SHA256
`e17af96ce9a1a3757cd5d6e8ee6947099a447ba1c4ef1570b98506f0e8fd30a7`.
The proof, ROM, source and 464-asset certificate are preserved unchanged.

1. In §3, the previous compositional compiler argument is
   [GAW2_THREE_GATHER_PERIOD.md §2](../unregistered_gaw2/GAW2_THREE_GATHER_PERIOD.md),
   rather than the printed §§2–3. Section 3 records deadline and storage
   failures of earlier versions; it is not the compiler correctness proof.
2. In §5, the infinite-line physical period induction is
   [GAW2_THREE_GATHER_PERIOD.md §6](../unregistered_gaw2/GAW2_THREE_GATHER_PERIOD.md),
   rather than the printed §7. Section 7 concerns reproducibility.
3. In §2, replace “set the signed step” by “set a step congruent to
   +1 or -1 modulo8192”. Literal MOVI(-1) yields the unsigned 20-bit
   value1048575. Conversion to a signed Word100 value does not make
   this -1. Its residue modulo8192 is8191, so VADDINDEX still computes
   exactly the stated native GF adjustment. The projection and
   relational algebra require that residue, not a signed Word100 -1.

These are citation and wording corrections, not changes to the rule,
ROM, deadlines, statements N1/N2 or their lower preparation premises.
The independent review found no counterexample to those scoped claims;
it supplies no noisy recovery, smaller-constant or iid reliability theorem.
