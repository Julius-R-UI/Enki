# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import anki.collection


class LocalizedError(Exception):
    "An error with a localized description"
    pass


class DocumentedError(LocalizedError):
    """A localized error described in the manual."""
    pass


class Interrupted(Exception):
    pass


class NetworkError(LocalizedError):
    pass


class SyncErrorKind(Enum):
    pass


class SyncError(LocalizedError):
    pass


class BackendIOError(LocalizedError):
    pass


class CustomStudyError(LocalizedError):
    pass


class DBError(LocalizedError):
    pass


class CardTypeError(DocumentedError):
    pass


class TemplateError(LocalizedError):
    pass


class NotFoundError(Exception):
    pass


class DeletedError(LocalizedError):
    pass


class ExistsError(Exception):
    pass


class UndoEmpty(Exception):
    pass


class FilteredDeckError(LocalizedError):
    pass


class InvalidInput(LocalizedError):
    pass


class SearchError(LocalizedError):
    pass


class AbortSchemaModification(Exception):
    pass


# legacy

