"""
Writer module for chapter generation using Claude API through OpenRouter.
"""

import logging
import json
import aiohttp
from typing import Dict, Optional
import asyncio
from .models import Chapter, VersionedContent

logger = logging.getLogger(__name__)

class ChapterWriter:
    """Handles chapter generation using Claude API through OpenRouter"""
    
    def __init__(self, api_config):
        self.api_config = api_config
        self.current_chapter: Optional[Chapter] = None
        self.context_window: Dict = {}
    
    async def _generate_content(self, prompt: str) -> str:
        """Generate content using Claude API through OpenRouter"""
        headers = {
            "Authorization": f"Bearer {self.api_config.api_key}",
            "Content-Type": "application/json"
        }
        # Add OpenRouter specific headers
        headers.update(self.api_config.headers)
        
        data = {
            "model": self.api_config.model,
            "messages": [
                {"role": "system", "content": "You are an expert novelist focusing on creating engaging and consistent narrative content."},
                {"role": "user", "content": prompt}
            ]
        }
        # Add generation parameters
        data.update(self.api_config.generation_params)
        
        timeout = aiohttp.ClientTimeout(total=60)  # Increased timeout to 60 seconds
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                for attempt in range(self.api_config.max_retries):
                    try:
                        async with session.post(
                            self.api_config.base_url,
                            headers=headers,
                            json=data
                        ) as response:
                            if response.status == 200:
                                result = await response.json()
                                return result['choices'][0]['message']['content']
                            elif response.status == 408:  # Timeout
                                error_text = await response.text()
                                logger.error(f"API timeout on attempt {attempt + 1}: {error_text}")
                                if attempt < self.api_config.max_retries - 1:
                                    wait_time = (attempt + 1) * 10  # Progressive delay
                                    logger.info(f"Waiting {wait_time} seconds before retry...")
                                    await asyncio.sleep(wait_time)
                                continue
                            else:
                                error_text = await response.text()
                                logger.error(f"API request failed with status {response.status}: {error_text}")
                                if attempt < self.api_config.max_retries - 1:
                                    wait_time = (attempt + 1) * 5
                                    logger.info(f"Waiting {wait_time} seconds before retry...")
                                    await asyncio.sleep(wait_time)
                                continue
                    except asyncio.TimeoutError:
                        logger.error(f"Request timeout on attempt {attempt + 1}")
                        if attempt < self.api_config.max_retries - 1:
                            wait_time = (attempt + 1) * 10
                            logger.info(f"Waiting {wait_time} seconds before retry...")
                            await asyncio.sleep(wait_time)
                        continue
                    except aiohttp.ClientError as e:
                        logger.error(f"Request error on attempt {attempt + 1}: {str(e)}")
                        if attempt < self.api_config.max_retries - 1:
                            wait_time = (attempt + 1) * 5
                            logger.info(f"Waiting {wait_time} seconds before retry...")
                            await asyncio.sleep(wait_time)
                        continue
                
                raise Exception(f"Failed after {self.api_config.max_retries} attempts")
                
        except Exception as e:
            logger.error(f"Failed to generate content: {str(e)}")
            raise

    def _create_chapter_prompt(self, chapter_brief: dict) -> str:
        """Create a detailed prompt for chapter generation"""
        prompt_template = {
            "role": "system",
            "content": f"""You are writing chapter {chapter_brief['chapter_number']} of a novel.
            Title: {chapter_brief['title']}
            
            Style Guide:
            {chapter_brief['style_guide']}
            
            Previous Chapter Context:
            {chapter_brief.get('previous_chapter', 'This is the first chapter.')}
            
            Characters in this chapter:
            {json.dumps([char.name for char in chapter_brief['characters']], indent=2)}
            
            Plot points to cover:
            {json.dumps([plot.title for plot in chapter_brief['plot_points']], indent=2)}
            
            Additional Notes:
            {chapter_brief['notes']}
            
            Please write this chapter maintaining consistency with the style guide and previous context.
            Focus on natural character interactions and smooth plot progression.
            Write a complete chapter of approximately 2,500 words."""
        }
        
        return json.dumps(prompt_template, indent=2)

    async def generate_chapter(self, chapter_brief: dict) -> Chapter:
        """Generate a complete chapter based on the provided brief"""
        logger.info("Starting chapter generation for: %s", chapter_brief['title'])
        
        prompt = self._create_chapter_prompt(chapter_brief)
        content = await self._generate_content(prompt)
        
        chapter = Chapter(
            title=chapter_brief['title'],
            content=VersionedContent(content),
            sequence_number=chapter_brief['chapter_number']
        )
        
        return chapter

    async def revise_chapter(self, chapter: Chapter, feedback: list) -> Chapter:
        """Revise a chapter based on provided feedback"""
        logger.info("Revising chapter: %s", chapter.title)
        
        revision_prompt = {
            "role": "user",
            "content": f"""Please revise the following chapter based on this feedback:
            
            Original Chapter:
            {chapter.content.content}
            
            Feedback Points:
            {json.dumps(feedback, indent=2)}
            
            Please maintain the original style and tone while addressing these points."""
        }
        
        revised_content = await self._generate_content(json.dumps(revision_prompt))
        chapter.update_content(revised_content)
        
        return chapter

    def _manage_context_window(self, chapter: Chapter) -> None:
        """Manage the context window for consistent writing"""
        self.context_window = {
            'current_chapter': chapter.id,
            'content_length': len(chapter.content.content),
            'version': chapter.content.version
        }
