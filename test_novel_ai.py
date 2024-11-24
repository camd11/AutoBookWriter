"""
Test script for the Novel AI Generation System
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

from novel_ai.models import Story, VersionedContent, Character, PlotPoint
from novel_ai.writer import ChapterWriter
from novel_ai.config import APIConfig

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_novel_ai.log')
    ]
)
logger = logging.getLogger(__name__)

def save_chapter(chapter, output_dir: str):
    """Save chapter content and metadata to files"""
    # Create output directory if it doesn't exist
    chapter_dir = Path(output_dir) / "chapters"
    chapter_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save chapter content
    content_file = chapter_dir / f"chapter_{chapter.sequence_number:03d}_{timestamp}.txt"
    with open(content_file, 'w', encoding='utf-8') as f:
        f.write(f"Title: {chapter.title}\n")
        f.write(f"Chapter {chapter.sequence_number}\n")
        f.write("=" * 50 + "\n\n")
        f.write(chapter.content.content)
    
    # Save chapter metadata
    metadata_file = chapter_dir / f"chapter_{chapter.sequence_number:03d}_{timestamp}_metadata.json"
    metadata = {
        "id": chapter.id,
        "title": chapter.title,
        "sequence_number": chapter.sequence_number,
        "status": chapter.status.value,
        "version": chapter.content.version,
        "created_at": chapter.content.created_at.isoformat(),
        "modified_at": chapter.content.modified_at.isoformat(),
        "characters": chapter.characters,
        "notes": chapter.notes
    }
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"Chapter saved to {content_file}")
    logger.info(f"Metadata saved to {metadata_file}")
    
    return content_file, metadata_file

async def test_chapter_generation():
    logger.info("Starting test chapter generation")
    
    # Load configuration
    logger.info("Loading configuration from config.json")
    try:
        with open('config.json', 'r') as f:
            config_data = json.load(f)
            logger.debug(f"Loaded config data: {json.dumps(config_data, indent=2)}")
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        return
    
    # Create API config
    logger.info("Initializing API configuration")
    try:
        api_config = APIConfig.from_dict(config_data['api_config'])
        logger.info("API configuration initialized successfully")
        logger.debug(f"API Config details:")
        logger.debug(f"- Model: {api_config.model}")
        logger.debug(f"- Base URL: {api_config.base_url}")
        logger.debug(f"- Headers: {api_config.headers}")
        logger.debug(f"- Generation Params: {api_config.generation_params}")
    except Exception as e:
        logger.error(f"Error initializing API config: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return
    
    # Initialize writer
    logger.info("Initializing ChapterWriter")
    writer = ChapterWriter(api_config)
    
    # Create a test chapter brief
    logger.info("Creating test chapter brief")
    chapter_brief = {
        "title": "The Beginning",
        "chapter_number": 1,
        "style_guide": """
        Write in a clear, engaging style.
        Use descriptive language but avoid purple prose.
        Focus on character development and natural dialogue.
        """,
        "characters": [
            Character(
                name="Sarah Chen",
                description=VersionedContent("A brilliant AI researcher"),
                background=VersionedContent("PhD in Computer Science, specializing in AI ethics")
            )
        ],
        "plot_points": [
            PlotPoint(
                title="First Discovery",
                description=VersionedContent("Sarah makes an unexpected breakthrough in AI consciousness")
            )
        ],
        "notes": "This is the opening chapter that introduces Sarah and her work in AI research.",
        "previous_chapter": None
    }
    
    logger.info("Attempting to generate chapter...")
    try:
        # Generate chapter
        chapter = await writer.generate_chapter(chapter_brief)
        
        logger.info("Chapter generated successfully!")
        print("\nGenerated Chapter:")
        print("-" * 50)
        print(f"Title: {chapter.title}")
        print(f"Sequence Number: {chapter.sequence_number}")
        print("-" * 50)
        print("Content:")
        print(chapter.content.content)
        print("-" * 50)
        
        # Save the chapter
        content_file, metadata_file = save_chapter(chapter, config_data['storage_path'])
        print(f"\nChapter saved to: {content_file}")
        print(f"Metadata saved to: {metadata_file}")
        
    except Exception as e:
        logger.error(f"Error generating chapter: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    print("Starting test script...")
    asyncio.run(test_chapter_generation())
    print("Test script completed")
