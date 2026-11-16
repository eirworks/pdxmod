# Checkbox group for selecting project tags

from collections.abc import Iterable
from enum import Enum

from textual.containers import ItemGrid
from textual.widgets import Checkbox

from pdxmod.project.project import project_tags

CHECKBOX_CHROME_WIDTH = 9
"""Columns a checkbox uses besides its label: border (2), padding (2), toggle button (3), label padding (2)."""


def tag_column_width(tags: Iterable[Enum]) -> int:
    """Return the width one tag checkbox needs so its longest label stays readable."""
    labels = [tag.value for tag in tags]
    return max((len(label) for label in labels), default=0) + CHECKBOX_CHROME_WIDTH


class TagCheckboxGroup(ItemGrid):
    """Checkbox grid listing project tags, wrapping into as many columns as fit."""

    DEFAULT_CSS = """
    TagCheckboxGroup {
        height: auto;
        grid-gutter: 0 2;
        margin-bottom: 1;
    }
    """

    def __init__(
        self,
        tags: Iterable[Enum] | None = None,
        selected: Iterable[Enum] = (),
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Build one checkbox per project tag.

        Args:
            tags: Tags to offer; defaults to every tag of the default game.
            selected: Tags whose checkbox starts checked.
            name: Optional widget name.
            id: Optional widget ID.
            classes: Optional CSS classes.
        """
        self.tags = list(tags) if tags is not None else project_tags()
        selected_tags = set(selected)
        self._tag_checkboxes = {
            tag: Checkbox(tag.value, value=tag in selected_tags, id=f"tag-{tag.name}")
            for tag in self.tags
        }

        super().__init__(
            *self._tag_checkboxes.values(),
            name=name,
            id=id,
            classes=classes,
            min_column_width=tag_column_width(self.tags),
            stretch_height=False,
        )

    def selected_tags(self) -> list[Enum]:
        """Return the tags whose checkbox is currently checked."""
        return [tag for tag, checkbox in self._tag_checkboxes.items() if checkbox.value]

    def selected_tag_values(self) -> list[str]:
        """Return the display values of the checked tags, ready for storing."""
        return [tag.value for tag in self.selected_tags()]

    def set_selected(self, tags: Iterable[Enum]) -> None:
        """Check the given tags and uncheck the others."""
        selected_tags = set(tags)
        for tag, checkbox in self._tag_checkboxes.items():
            checkbox.value = tag in selected_tags
