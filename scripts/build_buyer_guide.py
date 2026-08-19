#!/usr/bin/env python3
"""Build, finalize, and audit the monthly subscription × model buying guide."""
from buyer_guide.build import main as build_base
from buyer_guide.finalize import main as finalize
from buyer_guide.postprocess import main as postprocess

if __name__ == "__main__":
    build_base()
    finalize()
    postprocess()
