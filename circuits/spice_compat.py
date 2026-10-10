"""Narrow PySpice 1.5 compatibility fix for ngspice 42 informational stderr.
Actual errors are still handled by PySpice. No simulated data is changed.
"""
from PySpice.Spice.NgSpice.Shared import NgSpiceShared, ffi
_original = NgSpiceShared._send_char

def _send_char(message_c, ngspice_id, user_data):
    message = ffi.string(message_c).decode('utf-8', errors='replace').strip()
    if message == 'stderr Using SPARSE 1.3 as Direct Linear Solver':
        instance = ffi.from_handle(user_data)
        instance._stdout.append(message)
        return instance.send_char(message, ngspice_id)
    return _original(message_c, ngspice_id, user_data)
NgSpiceShared._send_char = staticmethod(_send_char)
