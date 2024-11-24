"""
Core data models for the Novel AI system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import uuid


class ChapterStatus(Enum):
    """Status states for chapter development"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    REVISION = "revision"
    COMPLETE = "complete"


@dataclass
class VersionedContent:
    """Base class for content that needs version control"""
    content: str
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    
    def update(self, new_content: str) -> None:
        """Update content and increment version"""
        self.content = new_content
        self.version += 1
        self.modified_at = datetime.now()


@dataclass
class Character:
    """Represents a story character with version control"""
    name: str
    description: VersionedContent
    background: VersionedContent
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    traits: List[str] = field(default_factory=list)
    relationships: Dict[str, str] = field(default_factory=dict)
    
    def update_description(self, new_description: str) -> None:
        """Update character description"""
        self.description.update(new_description)
    
    def update_background(self, new_background: str) -> None:
        """Update character background"""
        self.background.update(new_background)


@dataclass
class PlotPoint:
    """Represents a significant plot event"""
    title: str
    description: VersionedContent
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    chapter_id: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    
    def update_description(self, new_description: str) -> None:
        """Update plot point description"""
        self.description.update(new_description)


@dataclass
class Chapter:
    """Represents a story chapter"""
    title: str
    content: VersionedContent
    sequence_number: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: ChapterStatus = ChapterStatus.PLANNED
    plot_points: List[PlotPoint] = field(default_factory=list)
    characters: List[str] = field(default_factory=list)  # Character IDs
    notes: str = ""
    
    def update_content(self, new_content: str) -> None:
        """Update chapter content"""
        self.content.update(new_content)


@dataclass
class Story:
    """Main story container class"""
    title: str
    synopsis: VersionedContent
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    chapters: List[Chapter] = field(default_factory=list)
    characters: Dict[str, Character] = field(default_factory=dict)
    plot_points: Dict[str, PlotPoint] = field(default_factory=dict)
    style_guide: VersionedContent = field(default_factory=lambda: VersionedContent(""))
    
    def add_chapter(self, chapter: Chapter) -> None:
        """Add a new chapter to the story"""
        self.chapters.append(chapter)
        self.chapters.sort(key=lambda x: x.sequence_number)
    
    def add_character(self, character: Character) -> None:
        """Add a new character to the story"""
        self.characters[character.id] = character
    
    def add_plot_point(self, plot_point: PlotPoint) -> None:
        """Add a new plot point to the story"""
        self.plot_points[plot_point.id] = plot_point
    
    def update_synopsis(self, new_synopsis: str) -> None:
        """Update story synopsis"""
        self.synopsis.update(new_synopsis)
    
    def update_style_guide(self, new_style_guide: str) -> None:
        """Update style guide"""
        self.style_guide.update(new_style_guide)
