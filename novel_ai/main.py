"""
Main module demonstrating the Novel AI system usage.
"""

import asyncio
import logging
from pathlib import Path
from typing import List

from .config import APIConfig, SystemConfig, initialize_config
from .models import Story, Chapter, Character, PlotPoint, VersionedContent
from .director import Director
from .writer import ChapterWriter
from .reader import StoryAnalyzer
from .editor import ContentEditor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def create_example_story() -> Story:
    """Create an example story with initial content"""
    # Create a new story
    story = Story(
        title="The Digital Revolution",
        synopsis=VersionedContent("A tale of AI and human collaboration in the modern age.")
    )
    
    # Add characters
    protagonist = Character(
        name="Dr. Sarah Chen",
        description=VersionedContent("Brilliant AI researcher with a complex past"),
        background=VersionedContent("Leading expert in AI ethics and development"),
        traits=["brilliant", "determined", "ethical"]
    )
    
    antagonist = Character(
        name="Marcus Webb",
        description=VersionedContent("Tech mogul with questionable motives"),
        background=VersionedContent("Self-made billionaire, pushing AI boundaries"),
        traits=["ambitious", "ruthless", "charismatic"]
    )
    
    story.add_character(protagonist)
    story.add_character(antagonist)
    
    # Add plot points
    plot_points = [
        PlotPoint(
            title="AI Breakthrough",
            description=VersionedContent("Sarah makes a groundbreaking AI discovery")
        ),
        PlotPoint(
            title="Ethical Dilemma",
            description=VersionedContent("The implications of the AI breakthrough become clear")
        ),
        PlotPoint(
            title="Corporate Interference",
            description=VersionedContent("Marcus attempts to acquire Sarah's research")
        )
    ]
    
    for plot_point in plot_points:
        story.add_plot_point(plot_point)
    
    # Set style guide
    story.update_style_guide("""
    Style Guide for The Digital Revolution:
    - Write in third person limited perspective, focusing on Sarah's viewpoint
    - Maintain a balance between technical accuracy and accessibility
    - Use clear, concise language with occasional poetic flourishes
    - Emphasize the human elements of the story
    - Keep chapters between 2,000 and 3,000 words
    """)
    
    return story

async def main():
    """Main function demonstrating system usage"""
    # Initialize configuration
    config = initialize_config()
    api_config = APIConfig(api_key="your-api-key-here")  # Replace with actual API key
    
    # Create example story
    story = await create_example_story()
    
    # Initialize system components
    director = Director(api_config, story)
    writer = ChapterWriter(api_config)
    analyzer = StoryAnalyzer(api_config, story)
    editor = ContentEditor(api_config, story, analyzer)
    
    # Generate first chapter
    chapter_brief = await director.create_chapter_brief(Chapter(
        title="The Discovery",
        content=VersionedContent(""),
        sequence_number=1,
        plot_points=[story.plot_points[list(story.plot_points.keys())[0]]],
        characters=[list(story.characters.keys())[0]]  # Add protagonist
    ))
    
    # Generate chapter content
    chapter = await writer.generate_chapter(chapter_brief)
    
    # Analyze and review chapter
    analysis = await analyzer.analyze_chapter(chapter)
    review = await editor.review_chapter(chapter)
    
    # Generate revision request if needed
    if review.get("style_issues") or review.get("content_issues"):
        revision_request = await editor.generate_revision_request(chapter, review)
        # Revise chapter
        revised_chapter = await writer.revise_chapter(chapter, revision_request["revision_points"])
        # Update chapter in story
        story.add_chapter(revised_chapter)
    else:
        # Add chapter to story
        story.add_chapter(chapter)
    
    # Generate summary report
    logger.info("Story Progress Report:")
    logger.info("Title: %s", story.title)
    logger.info("Chapters: %d", len(story.chapters))
    logger.info("Characters: %d", len(story.characters))
    logger.info("Plot Points: %d", len(story.plot_points))
    
    # Get plot coverage report
    plot_coverage = analyzer.get_plot_coverage_report()
    logger.info("Plot Coverage: %.2f%%", plot_coverage["coverage_rate"] * 100)
    
    # Get style violation report
    style_violations = editor.get_style_violation_report()
    if style_violations:
        logger.info("Style Violations Found:")
        for chapter_title, violations in style_violations.items():
            logger.info("%s: %d violations", chapter_title, violations["violations_count"])

def run_example():
    """Run the example usage"""
    asyncio.run(main())

if __name__ == "__main__":
    run_example()
