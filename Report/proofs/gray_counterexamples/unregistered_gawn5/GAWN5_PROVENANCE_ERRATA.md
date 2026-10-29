# GAWN5 manifest-issuer correction

The first manifest issuer was redirected to a log inside its own asset
directory. The issuer included that still-empty log, then its final stdout
changed the log's hash. The first read-only validation consequently failed
on the issuer-log hash before any new mathematical replay.

The original manifest and validator are retained in figs alongside the
terminal issuer log; the failed validator log is in figs/robustness.
The final issue command writes to an external log outside the enumerated
directory. It pins the now-terminal original log and retained original
manifest/validator. No projection equation, native trajectory, checker
result, written reduction, CA rule or inherited asset changed.
