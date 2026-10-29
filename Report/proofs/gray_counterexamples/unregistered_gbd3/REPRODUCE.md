# GBD3 reproduction and exact scope

Run from the repository root, using Python3:

```sh
python3 Report/proofs/gray_counterexamples/unregistered_gbd3/validate_gbd3.py --output /tmp/GBD3_readonly_validation.json
```

The validator checks the entire inherited195-asset GBD2 provenance chain,
both accepted child/parent GBD2 receipts and terminal logs, all new source
versions and retained failed checks, then recomputes the new controller,
fresh K3387 packing and literal reset/birth/software binding. It writes
only the requested validation receipt and temporary replay results; it
does not change accepted sources or receipts.

Accepted new mathematical receipts are
[controller](../../../../figs/gray_counterexamples/unregistered_gbd3/GBD3_certificate_attempt06.json),
[fresh packing](../../../../figs/gray_counterexamples/unregistered_gbd3/GBD3_packing_certificate_attempt01.json),
and [binding](../../../../figs/gray_counterexamples/unregistered_gbd3/GBD3_binding_certificate_attempt01.json).
The corresponding logs end without an exception and their processes
returned0. The separately retained attempt03 code-count error and attempt04
checker-name-shadowing error returned1; neither issued a passing receipt.

The [written proof](GBD3_FINITE_HEAD_AND_LITERAL_WRITE.md) states each
scope. Q8192/U1048576/lambda24/c104 remain numerical baseline parameters.
The counted layout is K3387/2K6774 with Head204/eight carried Word20 registers.
FGET140/FPUT137/caller396 bits are actual issued software. Literal packing
has170 chunks/3217 transport rows, followed by computed-port Head birth;
the register0 and register7 callers take155 and190 updates, respectively.

Computed native ports and the coherent History-bank origin remain premises.
The current components do not emit a full own beta or autonomous native/
gather/flag/whole-period rule. There is no error-map/noise/shorter-U or Gray
refutation conclusion. The immutable counted binary code, Word20 vector
operations, altered Head/controller and computed-port reset/birth are
explicit departures from Gray's full protocol.

The manifest freezes these sources and receipts. Historical successful
attempts01/02/05 are matched to their exact source snapshots; the current
extended sources are not falsely substituted for those old hashes.
