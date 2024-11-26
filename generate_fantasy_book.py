"""
Script to generate a high fantasy novel
"""

import asyncio
import json
import logging
import sys
import traceback
from pathlib import Path
from datetime import datetime

from novel_ai.models import Story, ChapterStatus
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
        "characters": chapter_outline['characters'],
        "plot_points": chapter_outline['plot_points'],
        "notes": chapter.notes
    }
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"Chapter saved to {content_file}")
    logger.info(f"Metadata saved to {metadata_file}")
    
    return content_file, metadata_file

async def load_story():
    """Load the story configuration"""
    with open('story_data/novels/high_fantasy.json', 'r') as f:
        story_data = json.load(f)
    return story_data

async def generate_chapter_with_retry(writer, story_data, chapter_outline, previous_chapter, max_retries=3, retry_delay=5):
    """Generate a chapter with retry logic"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1} to generate chapter {chapter_outline['sequence_number']}")
            
            chapter_brief = {
                "title": chapter_outline['title'],
                "chapter_number": chapter_outline['sequence_number'],
                "style_guide": story_data['style_guide']['content'],
                "characters": [story_data['characters'][char_id] for char_id in chapter_outline['characters']],
                "plot_points": [story_data['plot_points'][plot_id] for plot_id in chapter_outline.get('plot_points', [])],
                "notes": chapter_outline['notes'],
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
    """Generate the complete high fantasy novel"""
    logger.info("Starting high fantasy book generation")
    
    # Load configuration
    with open('config.json', 'r') as f:
        config_data = json.load(f)
    
    api_config = APIConfig.from_dict(config_data['api_config'])
    writer = ChapterWriter(api_config)
    
    # Load story structure
    story_data = await load_story()
    logger.info(f"Loaded story structure: {story_data['title']}")
    
    # Generate each chapter
    previous_chapter = None
    for chapter_data in story_data['chapters']:
        logger.info(f"\nGenerating chapter {chapter_data['sequence_number']}: {chapter_data['title']}")
        logger.info(f"Characters: {', '.join(chapter_data['characters'])}")
        
        try:
            # Generate chapter with retry logic
            chapter = await generate_chapter_with_retry(
                writer,
                story_data,
                chapter_data,
                previous_chapter
            )
            
            # Save chapter
            content_file, metadata_file = save_chapter(chapter, chapter_data, config_data['storage_path'])
            print(f"\nGenerated Chapter {chapter_data['sequence_number']}: {chapter_data['title']}")
            print(f"Saved to: {content_file}")
            
            previous_chapter = chapter
            
            # Wait between chapters to avoid rate limiting
            if chapter_data['sequence_number'] < len(story_data['chapters']):
                wait_time = 30
                logger.info(f"Waiting {wait_time} seconds before next chapter...")
                await asyncio.sleep(wait_time)
            
        except Exception as e:
            logger.error(f"Failed to generate chapter {chapter_data['sequence_number']}: {str(e)}")
            logger.error(traceback.format_exc())
            user_input = input(f"\nError generating chapter {chapter_data['sequence_number']}. Options:\n"
                             f"1. 'retry' to try this chapter again\n"
                             f"2. 'skip' to continue with next chapter\n"
                             f"3. Any other key to exit\n"
                             f"Enter choice: ")
            if user_input.lower() == 'retry':
                continue
            elif user_input.lower() != 'skip':
                break

if __name__ == "__main__":
    asyncio.run(generate_book())
