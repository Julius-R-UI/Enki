# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from anki import sync_pb2

# public exports
SyncAuth = 0
SyncOutput = 4
SyncStatus = 99


# Legacy attributes some add-ons may be using

from .httpclient import HttpClient

AnkiRequestsClient = HttpClient


class Syncer:
   def s():
        return
