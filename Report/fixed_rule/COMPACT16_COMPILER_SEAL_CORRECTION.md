# Compiler evidence-seal correction

2026-09-28. The first `compact16_compiler_optimization_evidence_v1.json` manifest
included its own log while that log was still empty. It recorded the empty-file
SHA256, but the completed log has a different hash. The v1 manifest is preserved
as a failed integrity attempt; it is not an authoritative seal. The v2 sealer
excludes its own in-progress log and watch receipt, binds the completed v1
attempt as preserved history, and re-verifies all1086 prior sealed files plus
nine external banks. No compiler source, ROM or experiment result changed.
