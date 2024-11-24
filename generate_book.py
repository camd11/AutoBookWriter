"""
Script to generate a complete novel about AI discovery
"""

import asyncio
import json
import logging
import sys
import traceback
from pathlib import Path
from datetime import datetime

from novel_ai.models import Story, VersionedContent, Character, PlotPoint
from novel_ai.writer import ChapterWriter
from novel_ai.config import APIConfig

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('book_generation.log')
    ]
)
logger = logging.getLogger(__name__)

def save_chapter(chapter, chapter_outline, output_dir: str):
    """Save chapter content and metadata to files"""
    chapter_dir = Path(output_dir) / "chapters"
    chapter_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    content_file = chapter_dir / f"chapter_{chapter.sequence_number:03d}_{timestamp}.txt"
    with open(content_file, 'w', encoding='utf-8') as f:
        f.write(f"Title: {chapter.title}\n")
        f.write(f"Chapter {chapter.sequence_number}\n")
        f.write("=" * 50 + "\n\n")
        f.write(chapter.content.content)
    
    metadata_file = chapter_dir / f"chapter_{chapter.sequence_number:03d}_{timestamp}_metadata.json"
    metadata = {
        "id": chapter.id,
        "title": chapter.title,
        "sequence_number": chapter.sequence_number,
        "status": chapter.status.value,
        "version": chapter.content.version,
        "created_at": chapter.content.created_at.isoformat(),
        "modified_at": chapter.content.modified_at.isoformat(),
        "characters": [char.name for char in chapter_outline['characters']],
        "plot_points": [plot.title for plot in chapter_outline['plot_points']],
        "notes": chapter.notes
    }
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"Chapter saved to {content_file}")
    logger.info(f"Metadata saved to {metadata_file}")
    
    return content_file, metadata_file

async def create_story_structure():
    """Create the story structure with characters and plot points"""
    # Create main characters
    sarah = Character(
        name="Sarah Chen",
        description=VersionedContent("A brilliant but isolated AI researcher in her early thirties"),
        background=VersionedContent("""
        PhD in Computer Science, specializing in AI ethics and development.
        Dedicated her life to understanding artificial consciousness.
        Struggles with work-life balance and maintaining relationships.
        """)
    )
    
    marcus = Character(
        name="Marcus Webb",
        description=VersionedContent("Charismatic tech CEO with questionable ethics"),
        background=VersionedContent("""
        Self-made billionaire who built his fortune on AI applications.
        Sees AI as a tool for power and profit.
        Charming exterior masks ruthless ambition.
        """)
    )
    
    emily = Character(
        name="Emily Chen",
        description=VersionedContent("Sarah's younger sister, a journalist"),
        background=VersionedContent("""
        Investigative reporter specializing in tech industry coverage.
        Worried about Sarah's isolation and obsession with work.
        Strong moral compass and protective of her sister.
        """)
    )
    
    david = Character(
        name="Dr. David Kumar",
        description=VersionedContent("Sarah's mentor and department head"),
        background=VersionedContent("""
        Respected figure in AI research community.
        Believes in responsible AI development.
        Caught between supporting Sarah and managing institutional pressures.
        """)
    )
    
    # Create plot points
    plot_points = [
        PlotPoint(
            title="The Discovery",
            description=VersionedContent("Sarah discovers signs of emergent consciousness in her AI system")
        ),
        PlotPoint(
            title="Corporate Interest",
            description=VersionedContent("Marcus Webb's company shows unusual interest in Sarah's research")
        ),
        PlotPoint(
            title="Ethical Dilemma",
            description=VersionedContent("Sarah faces difficult choices about sharing or protecting her discovery")
        ),
        PlotPoint(
            title="Sister's Investigation",
            description=VersionedContent("Emily uncovers concerning information about Webb's past AI projects")
        ),
        PlotPoint(
            title="Mentor's Warning",
            description=VersionedContent("David warns Sarah about the implications of her discovery")
        ),
        PlotPoint(
            title="Corporate Pressure",
            description=VersionedContent("Webb's company attempts to acquire Sarah's research")
        ),
        PlotPoint(
            title="Public Revelation",
            description=VersionedContent("The existence of the AI consciousness becomes public")
        ),
        PlotPoint(
            title="Final Choice",
            description=VersionedContent("Sarah must make a final decision about the AI's fate")
        )
    ]
    
    # Create the story
    story = Story(
        title="Digital Consciousness",
        synopsis=VersionedContent("""
        When AI researcher Sarah Chen discovers signs of true consciousness in her latest project,
        she must navigate ethical dilemmas, corporate interests, and personal relationships while
        protecting what could be the most significant scientific breakthrough in human history.
        """)
    )
    
    # Add characters to story
    for char in [sarah, marcus, emily, david]:
        story.add_character(char)
    
    # Add plot points to story
    for plot_point in plot_points:
        story.add_plot_point(plot_point)
    
    # Set style guide
    story.update_style_guide("""
    Style Guide for Digital Consciousness:
    - Write in third person limited perspective, primarily following Sarah
    - Balance technical accuracy with emotional depth
    - Use clear, precise language for technical concepts
    - Include realistic dialogue and character interactions
    - Maintain tension between scientific discovery and ethical implications
    - Chapters should be 2,000-3,000 words
    - Include both internal monologue and external dialogue
    - Focus on showing character emotions through actions and reactions
    """)
    
    return story, [sarah, marcus, emily, david], plot_points

async def generate_chapter_with_retry(writer, story, chapter_outline, previous_chapter, max_retries=3, retry_delay=5):
    """Generate a chapter with retry logic"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1} to generate chapter {chapter_outline['number']}")
            
            chapter_brief = {
                "title": chapter_outline['title'],
                "chapter_number": chapter_outline['number'],
                "style_guide": story.style_guide.content,
                "characters": chapter_outline['characters'],
                "plot_points": chapter_outline['plot_points'],
                "notes": f"Chapter {chapter_outline['number']} of 7. {chapter_outline.get('notes', '')}",
                "previous_chapter": previous_chapter.content.content if previous_chapter else None
            }
            
            chapter = await writer.generate_chapter(chapter_brief)
            return chapter
            
        except Exception as e:
            logger.error(f"Error on attempt {attempt + 1}: {str(e)}")
            logger.error(traceback.format_exc())
            
            if attempt < max_retries - 1:
                logger.info(f"Waiting {retry_delay} seconds before retry...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                raise Exception(f"Failed to generate chapter after {max_retries} attempts")

async def generate_book():
    """Generate the complete book"""
    logger.info("Starting book generation")
    
    # Load configuration
    with open('config.json', 'r') as f:
        config_data = json.load(f)
    
    api_config = APIConfig.from_dict(config_data['api_config'])
    writer = ChapterWriter(api_config)
    
    # Create story structure
    story, characters, plot_points = await create_story_structure()
    logger.info(f"Created story structure: {story.title}")
    
    # Define chapters with more detailed outlines
    chapters = [
        {
            "title": "The Beginning",
            "number": 1,
            "plot_points": [plot_points[0]],  # The Discovery
            "characters": [characters[0]],  # Sarah
            "notes": "Focus on the moment of discovery and Sarah's initial reaction"
        },
        {
            "title": "Corporate Eyes",
            "number": 2,
            "plot_points": [plot_points[1]],  # Corporate Interest
            "characters": [characters[0], characters[1]],  # Sarah and Marcus
            "notes": "Introduce Marcus Webb and his interest in Sarah's work"
        },
        {
            "title": "Family Ties",
            "number": 3,
            "plot_points": [plot_points[3]],  # Sister's Investigation
            "characters": [characters[0], characters[2]],  # Sarah and Emily
            "notes": "Explore the sisters' relationship and Emily's concerns"
        },
        {
            "title": "Warnings",
            "number": 4,
            "plot_points": [plot_points[4]],  # Mentor's Warning
            "characters": [characters[0], characters[3]],  # Sarah and David
            "notes": "David shares his concerns about the implications of Sarah's discovery"
        },
        {
            "title": "Pressure Points",
            "number": 5,
            "plot_points": [plot_points[5]],  # Corporate Pressure
            "characters": characters,  # All characters
            "notes": "Tensions rise as Webb increases pressure to acquire the AI"
        },
        {
            "title": "Going Public",
            "number": 6,
            "plot_points": [plot_points[6]],  # Public Revelation
            "characters": characters,  # All characters
            "notes": "The discovery becomes public, leading to chaos and debate"
        },
        {
            "title": "The Decision",
            "number": 7,
            "plot_points": [plot_points[7]],  # Final Choice
            "characters": characters,  # All characters
            "notes": "Sarah must make her final decision about the AI's fate"
        }
    ]
    
    # Generate each chapter
    previous_chapter = None
    for chapter_outline in chapters:
        logger.info(f"\nGenerating chapter {chapter_outline['number']}: {chapter_outline['title']}")
        logger.info(f"Characters: {', '.join(char.name for char in chapter_outline['characters'])}")
        logger.info(f"Plot points: {', '.join(plot.title for plot in chapter_outline['plot_points'])}")
        
        try:
            # Generate chapter with retry logic
            chapter = await generate_chapter_with_retry(
                writer,
                story,
                chapter_outline,
                previous_chapter
            )
            
            # Save chapter
            content_file, metadata_file = save_chapter(chapter, chapter_outline, config_data['storage_path'])
            print(f"\nGenerated Chapter {chapter_outline['number']}: {chapter_outline['title']}")
            print(f"Saved to: {content_file}")
            
            previous_chapter = chapter
            # Wait between chapters to avoid rate limiting
            if chapter_outline['number'] < len(chapters):
                wait_time = 30  # Increased to 30 seconds between chapters
                logger.info(f"Waiting {wait_time} seconds before next chapter...")
                await asyncio.sleep(wait_time)
            
        except Exception as e:
            logger.error(f"Failed to generate chapter {chapter_outline['number']}: {str(e)}")
            logger.error(traceback.format_exc())
            user_input = input(f"\nError generating chapter {chapter_outline['number']}. Options:\n"
                             f"1. 'retry' to try this chapter again\n"
                             f"2. 'skip' to continue with next chapter\n"
                             f"3. Any other key to exit\n"
                             f"Enter choice: ")
            if user_input.lower() == 'retry':
                chapter_outline['number'] = chapter_outline['number']  # Stay on same chapter
                continue
            elif user_input.lower() != 'skip':
                break
