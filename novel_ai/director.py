"""
Director module for managing story development and coordination.
"""

import logging
from typing import List, Optional
from .models import Story, Chapter, Character, PlotPoint, ChapterStatus
from .config import APIConfig

logger = logging.getLogger(__name__)

class Director:
    """Manages overall story development and coordination"""
    
    def __init__(self, api_config: APIConfig, story: Story):
        self.api_config = api_config
        self.story = story
        self.current_chapter_id: Optional[str] = None
    
    async def create_chapter_brief(self, chapter: Chapter) -> str:
        """Generate a chapter brief for the writer module"""
        # Get previous chapter for context if it exists
        prev_chapter = None
        if chapter.sequence_number > 1:
            prev_chapters = [c for c in self.story.chapters if c.sequence_number == chapter.sequence_number - 1]
            if prev_chapters:
                prev_chapter = prev_chapters[0]
        
        # Compile relevant plot points
        relevant_plot_points = [
            self.story.plot_points[pp_id] 
            for pp_id in chapter.plot_points
        ]
        
        # Compile character information
        characters = [
            self.story.characters[char_id]
            for char_id in chapter.characters
        ]
        
        # Create the brief template
        brief = {
            "chapter_number": chapter.sequence_number,
            "title": chapter.title,
            "plot_points": relevant_plot_points,
            "characters": characters,
            "style_guide": self.story.style_guide.content,
            "previous_chapter": prev_chapter.content.content if prev_chapter else None,
            "notes": chapter.notes
        }
        
        # TODO: Use Claude API to generate detailed chapter brief
        return str(brief)
    
    async def review_chapter(self, chapter: Chapter) -> List[str]:
        """Review a completed chapter and generate feedback"""
        # TODO: Implement chapter review logic using Reader and Editor modules
        return []
    
    async def approve_chapter(self, chapter: Chapter) -> bool:
        """Approve a chapter for inclusion in the final story"""
        feedback = await self.review_chapter(chapter)
        if not feedback:
            chapter.status = ChapterStatus.COMPLETE
            return True
        chapter.status = ChapterStatus.REVISION
        return False
    
    async def generate_plot_outline(self) -> List[PlotPoint]:
        """Generate a plot outline for the story"""
        # TODO: Implement plot outline generation using Claude API
        return []
    
    async def update_story_bible(self) -> None:
        """Update the story bible with current story state"""
        # TODO: Implement story bible update logic
        pass
    
    def get_chapter_status(self) -> dict:
        """Get the current status of all chapters"""
        return {
            chapter.id: {
                "title": chapter.title,
                "status": chapter.status,
                "sequence": chapter.sequence_number
            }
            for chapter in self.story.chapters
        }
