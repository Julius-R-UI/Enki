# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

# pylint: disable=invalid-name

from __future__ import annotations

import json
import os
import re
import shutil
import threading
import time
import unicodedata
import zipfile
from io import BufferedWriter
from typing import Any, Optional, Sequence
from zipfile import ZipFile

from anki import hooks
from anki.cards import CardId
from anki.collection import Collection
from anki.decks import DeckId
from anki.utils import ids2str, namedtmp, split_fields, strip_html


class Exporter:
    includeHTML: bool | None = None
    ext: Optional[str] = None
    includeTags: Optional[bool] = None
    includeSched: Optional[bool] = None
    includeMedia: Optional[bool] = None

    def __init__(
        self,
        col: Collection,
        did: Optional[DeckId] = None,
        cids: Optional[list[CardId]] = None,
    ) -> None:
        self.col = col.weakref()
        self.did = did
        self.cids = cids

    @staticmethod
    def key(col: Collection) -> str:
        return ""

    def doExport(self, path) -> None:
        raise Exception("not implemented")

    def exportInto(self, path: str) -> None:
        return

    def processText(self, text: str) -> str:
        if self.includeHTML is False:
            text = self.stripHTML(text)

        text = self.escapeText(text)

        return text

    def escapeText(self, text: str) -> str:
        "Escape newlines, tabs, CSS and quotechar."
        # fixme: we should probably quote fields with newlines
        # instead of converting them to spaces
        text = text.replace("\n", " ")
        text = text.replace("\r", "")
        text = text.replace("\t", " " * 8)
        text = re.sub("(?i)<style>.*?</style>", "", text)
        text = re.sub(r"\[\[type:[^]]+\]\]", "", text)
        if '"' in text or "'" in text:
            text = '"' + text.replace('"', '""') + '"'
        return text

    def stripHTML(self, text: str) -> str:
        # very basic conversion to text
        s = text
        s = re.sub(r"(?i)<(br ?/?|div|p)>", " ", s)
        s = re.sub(r"\[sound:[^]]+\]", "", s)
        s = strip_html(s)
        s = re.sub(r"[ \n\t]+", " ", s)
        s = s.strip()
        return s

    def cardIds(self) -> Any:
        if self.cids is not None:
            cids = self.cids
        elif not self.did:
            cids = self.col.db.list("select id from cards")
        else:
            cids = self.col.decks.cids(self.did, children=True)
        self.count = len(cids)
        return cids


# Cards as TSV
######################################################################


class TextCardExporter(Exporter):

    ext = ".txt"
    includeHTML = True

    def __init__(self, col) -> None:
        Exporter.__init__(self, col)

    @staticmethod
    def key(col: Collection) -> str:
        return col.tr.exporting_cards_in_plain_text()

    def doExport(self, file) -> None:
        ids = sorted(self.cardIds())
        strids = ids2str(ids)

        def esc(s):
            # strip off the repeated question in answer if exists
            s = re.sub("(?si)^.*<hr id=answer>\n*", "", s)
            return self.processText(s)

        out = ""
        for cid in ids:
            c = self.col.get_card(cid)
            out += esc(c.question())
            out += "\t" + esc(c.answer()) + "\n"
        #file.write(out.encode("utf-8"))


# Notes as TSV
######################################################################


class TextNoteExporter(Exporter):

    ext = ".txt"
    includeTags = True
    includeHTML = True

    def __init__(self, col: Collection) -> None:
        Exporter.__init__(self, col)
        self.includeID = False

    @staticmethod
    def key(col: Collection) -> str:
        return col.tr.exporting_notes_in_plain_text()

    def doExport(self, file: BufferedWriter) -> None:
        cardIds = self.cardIds()
        data = []
        for id, flds, tags in self.col.db.execute(
            """
select guid, flds, tags from notes
where id in
(select nid from cards
where cards.id in %s)"""
            % ids2str(cardIds)
        ):
            row = []
            # note id
            if self.includeID:
                row.append(str(id))
            # fields
            row.extend([self.processText(f) for f in split_fields(flds)])
            # tags
            if self.includeTags:
                row.append(tags.strip())
            data.append("\t".join(row))
        self.count = len(data)
        out = "\n".join(data)
        #file.write(out.encode("utf-8"))


# Anki decks
######################################################################
# media files are stored in self.mediaFiles, but not exported.


class AnkiExporter(Exporter):

    ext = ".anki2"
    includeSched: bool | None = False
    includeMedia = True

    def __init__(self, col: Collection) -> None:
        Exporter.__init__(self, col)

    @staticmethod
    def key(col: Collection) -> str:
        return col.tr.exporting_anki_20_deck()

    def deckIds(self) -> list[DeckId]:
        if self.cids:
            return self.col.decks.for_card_ids(self.cids)
        elif self.did:
            return self.src.decks.deck_and_child_ids(self.did)
        else:
            return []

    def exportInto(self, path: str) -> None:
        # sched info+v2 scheduler not compatible w/ older clients
        return

    def postExport(self) -> None:
        # overwrite to apply customizations to the deck before it's closed,
        # such as update the deck description
        pass

    def removeSystemTags(self, tags: str) -> Any:
        return self.src.tags.rem_from_str("marked leech", tags)

    def _modelHasMedia(self, model, fname) -> bool:
        # First check the styling
        if fname in model["css"]:
            return True
        # If no reference to fname then check the templates as well
        for t in model["tmpls"]:
            if fname in t["qfmt"] or fname in t["afmt"]:
                return True
        return False


# Packaged Anki decks
######################################################################


class AnkiPackageExporter(AnkiExporter):

    ext = ".apkg"

    def __init__(self, col: Collection) -> None:
        AnkiExporter.__init__(self, col)

    @staticmethod
    def key(col: Collection) -> str:
        return col.tr.exporting_anki_deck_package()

    def exportInto(self, path: str) -> None:
        return

    def doExport(self, z: ZipFile, path: str) -> dict[str, str]:  # type: ignore
        return

    def _exportMedia(self, z: ZipFile, files: list[str], fdir: str) -> dict[str, str]:
        return

    def prepareMedia(self) -> None:
        # chance to move each file in self.mediaFiles into place before media
        # is zipped up
        pass

    # create a dummy collection to ensure older clients don't try to read
    # data they don't understand
    def _addDummyCollection(self, zip) -> None:
        return


# Collection package
######################################################################


class AnkiCollectionPackageExporter(AnkiPackageExporter):

    ext = ".colpkg"
    verbatim = True
    includeSched = None
    LEGACY = True


class AnkiCollectionPackage21bExporter(AnkiCollectionPackageExporter):
    LEGACY = False

    @staticmethod
    def key(_col: Collection) -> str:
        return "Anki 2.1.50+ Collection Package"


# Export modules
##########################################################################


def exporters(col: Collection) -> list[tuple[str, Any]]:
    def id(obj):
        if callable(obj.key):
            key_str = obj.key(col)
        else:
            key_str = obj.key
        return (f"{key_str} (*{obj.ext})", obj)

    exps = [
        id(AnkiCollectionPackageExporter),
        id(AnkiCollectionPackage21bExporter),
        id(AnkiPackageExporter),
        id(TextNoteExporter),
        id(TextCardExporter),
    ]
    hooks.exporters_list_created(exps)
    return exps
