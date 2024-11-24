"""
Script to resume book generation from a specific chapter
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
from generate_book import create_story_structure, generate_chapter_with_retry, save_chapter

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

def load_previous_chapter(chapter_num: int, story_dir: str) -> str:
    """Load the content of the previous chapter"""
    chapter_dir = Path(story_dir) / "chapters"
    if not chapter_dir.exists():
        return None
    
    # Find the latest version of the previous chapter
    previous_files = list(chapter_dir.glob(f"chapter_{chapter_num:03d}_*.txt"))
    if not previous_files:
        return None
    
    # Sort by timestamp (newest first)
    latest_file = sorted(previous_files, key=lambda x: x.stem.split('_')[2], reverse=True)[0]
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        return f.read()

async def resume_book_generation(start_chapter: int = 3):
    """Resume book generation from a specific chapter"""
    logger.info(f"Resuming book generation from chapter {start_chapter}")
    
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
    
    # Load the previous chapter's content
    previous_content = load_previous_chapter(start_chapter - 1, config_data['storage_path'])
    if previous_content:
        previous_chapter = type('Chapter', (), {
            'content': type('VersionedContent', (), {'content': previous_content})()
        })()
    else:
        previous_chapter = None
    
    # Generate remaining chapters
    for chapter_outline in chapters:
        if chapter_outline['number'] < start_chapter:
            continue
            
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
            if chapter_outline['number'] < max(ch['number'] for ch in chapters):
                wait_time = 30  # 30 seconds between chapters
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

if __name__ == "__main__":
    print("Resuming book generation from chapter 3...")
    asyncio.run(resume_book_generation(3))
    print("Book generation completed")
