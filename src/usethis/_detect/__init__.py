"""The detections module.

The purpose of this module is provide functions which use heuristics to detect whether
different tools are being used or not (and in some cases; to infer which one is the one
to prefer when there are multiple choices; e.g. choosing to use 'uv' as the backend
instead of 'poetry', etc.)

These detections might make use of lower-level integrations.
"""
