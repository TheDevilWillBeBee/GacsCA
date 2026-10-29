"""GE1: explicit native-only fifth writes over the frozen GE0 component.

This is a changed integration component, not an own programme or whole CA.
It retains GE0's native frame, early programme, schedule and finite ports.
Only the five final-store ports at the 37 normal native primaries cease to
be free: they read the actual old EarlyOut holder bits. Other final-store
ports and the two late Workspace ports remain explicit finite inputs.
"""
import gray_early_native_flags as ge0
import literal_maintenance as literal

Q=ge0.Q
U=ge0.U
SLOTS=ge0.SLOTS
WRITE_BEGIN=112*Q
WRITE_END=120*Q
NATIVE_PRIMARY_BEGIN=ge0.PRIMARY_START
NATIVE_PRIMARY_END=ge0.PRIMARY_START+37


def native_fifth_stores(cells,other_stores=None):
    """Total raw radius-five store equations; no simulated-state oracle.

    For a holder x and copy offset s, its service coordinate is
    (computed_native_GF(x)+s) modQ. The old EarlyOut bit for logical x+s
    is the 3/5 vote of physical holders x+s-t, t in SLOTS. These coordinates
    lie in[-4,4]. A native match overrides any incoming final-store port.
    The frozen GT0 Nextbit equation supplies reset and clock gating.
    """
    computed=literal.scalar({j:ge0.native_word(c) for j,c in cells.items()})
    stores={} if other_stores is None else dict(other_stores)
    for s in SLOTS:
        address=(computed['addr']+s)%Q
        if NATIVE_PRIMARY_BEGIN<=address<NATIVE_PRIMARY_END:
            bit=ge0.head.vote([cells[s-t].early_out[i]&1
                for i,t in enumerate(SLOTS)])
            stores[s]=(1,bit)
    return stores


def local_transition(cells,beta,workspace_ports=(0,0),other_fifth_stores=None):
    return ge0.local_transition(cells,beta,workspace_ports,
        native_fifth_stores(cells,other_fifth_stores))


def transition_manifest():
    return dict(component='GE1 native-only fifth writeback',Q=Q,U=U,
        lambda_original=24,c_original=104,radius=5,frame_bits=ge0.FRAME_BITS,
        frame_schema=ge0.FRAME_SCHEMA,normal_native_primary_interval=[
            NATIVE_PRIMARY_BEGIN,NATIVE_PRIMARY_END],
        copy_offsets=SLOTS,raw_EarlyOut_holder_offsets={str(s):[s-t for t in SLOTS]
            for s in SLOTS},service_address='(computed native GF(x)+s) mod Q',
        enable='native-primary service match; frozen GT0 clock gate',
        value='3/5 majority of old raw EarlyOut(x+s-t)[copy t]',
        write_window=[WRITE_BEGIN,WRITE_END],
        write_begin_reset_has_priority=True,actual_first_write=WRITE_BEGIN+1,
        commit='at computed Age0: SimBit := old 3/5 Nextbit; Nextbit := 0',
        unchanged_early_native_code_bits=2346,
        remaining_ports=['two late Workspace bits','five non-native final stores'],
        full_own_beta_or_programme_fit_proved=False,
        new_whole_rule_or_shorter_U=False)
