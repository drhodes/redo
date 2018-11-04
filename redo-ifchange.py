#!/usr/bin/env python
import sys, os

import vars_init
vars_init.init(sys.argv[1:])

import vars, state, builder, jwack, deps
from helpers import unlink
from log import debug, debug2, err

def should_build(t):
    f = state.File(name=t)
    if f.is_failed():
        raise builder.ImmediateReturn(32)
    dirty = deps.isdirty(f, depth = '', max_changed = vars.RUNID,
                         already_checked=[])
    return f.is_generated, dirty==[f] and deps.DIRTY or dirty


rv = 202
try:
    if vars_init.is_toplevel:
        builder.start_stdin_log_reader(status=True, details=True)
    if vars.TARGET and not vars.UNLOCKED:
        me = os.path.join(vars.STARTDIR, 
                          os.path.join(vars.PWD, vars.TARGET))
        f = state.File(name=me)
        debug2('TARGET: %r %r %r\n' % (vars.STARTDIR, vars.PWD, vars.TARGET))
    else:
        f = me = None
        debug2('redo-ifchange: not adding depends.\n')
    try:
        targets = sys.argv[1:]
        if f:
            for t in targets:
                f.add_dep('m', t)
            f.save()
            state.commit()
        rv = builder.main(targets, should_build)
    finally:
        try:
            state.rollback()
        finally:
            jwack.force_return_tokens()
except KeyboardInterrupt:
    if vars_init.is_toplevel:
        builder.await_log_reader()
    sys.exit(200)
state.commit()
if vars_init.is_toplevel:
    builder.await_log_reader()
sys.exit(rv)
