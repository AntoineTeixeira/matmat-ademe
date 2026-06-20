"""
Presentation
************
Defines bridge pool shared data.

Content
*******
- Data:
    - pool: Pool[CombinedBridge]
"""

from matmat.core.base import pool
from matmat.core.bridge import core as bridge

pool = pool.Pool[bridge.CombinedBridge]()
"""The shared pool of combined bridges"""
