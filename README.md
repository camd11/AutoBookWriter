# AI Novel Generation System

A modular Python system for managing multiple instances of Claude 3.5 Sonnet for collaborative novel writing.

## System Architecture

The system consists of several key modules working together to manage the novel writing process:

### 1. Director Module
- Manages overall story structure and coordination
- Maintains master documents (plot outline, character sheets, style guides)
- Assigns and tracks chapter development
- Reviews editor reports and approves final content
- Implements version control for story elements

### 2. Writer Module
- Receives chapter briefs with context from director
- Handles chapter generation using Claude API
- Includes previous chapter context for continuity
- Implements style and tone templates

### 3. Reader Module
- Analyzes chapters for plot consistency
- Verifies character consistency
- Generates chapter summaries
- Flags potential issues
- Passes analysis to editor module

### 4. Editor Module
- Reviews style and tone consistency
- Checks pacing
- Maintains consistent voice
- Generates revision requests
- Creates reports for director module

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AutoBookWriter.git
cd AutoBookWriter
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
   - Copy the example environment file: 
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your OpenRouter API key:
     ```
     OPENROUTER_API_KEY=your_openrouter_api_key_here
     ```
   - Alternatively, you can set the environment variable directly:
     ```bash
     export OPENROUTER_API_KEY=your_api_key_here
     ```

4. Create necessary directories:
```bash
mkdir -p data/chapters data/analysis data/reviews data/story_states data/database_backups logs/conversations
```

## API Key Security

This project uses the OpenRouter API which requires an API key. To obtain an API key:

1. Sign up at [OpenRouter](https://openrouter.ai/)
2. Navigate to your account settings
3. Generate a new API key
4. Add this key to your `.env` file as described in the Setup section

**Important Security Notes:**
- Never commit your `.env` file to git (it's already in `.gitignore`)
- If you accidentally expose your API key, rotate it immediately
- See `API_KEY_SECURITY.md` for more detailed security best practices

## Usage

```python
from novel_ai.config import initialize_config
from novel_ai.models import Story, Chapter, Character, PlotPoint
from novel_ai.director import Director
from novel_ai.writer import ChapterWriter
from novel_ai.reader import StoryAnalyzer
from novel_ai.editor import ContentEditor

async def main():
    # Initialize configuration
    config = initialize_config("config.json")
    
    # Create a new story
    story = Story(
        title="Your Novel Title",
        synopsis=VersionedContent("Your novel synopsis")
    )
    
    # Initialize system components
    director = Director(config.api_config, story)
    writer = ChapterWriter(config.api_config)
    analyzer = StoryAnalyzer(config.api_config, story)
    editor = ContentEditor(config.api_config, story, analyzer)
    
    # Generate a chapter
    chapter_brief = await director.create_chapter_brief(...)
    chapter = await writer.generate_chapter(chapter_brief)
    
    # Analyze and review
    analysis = await analyzer.analyze_chapter(chapter)
    review = await editor.review_chapter(chapter)
    
    # Handle revisions if needed
    if review.get("style_issues") or review.get("content_issues"):
        revision_request = await editor.generate_revision_request(chapter, review)
        chapter = await writer.revise_chapter(chapter, revision_request["revision_points"])
    
    # Add to story
    story.add_chapter(chapter)

if __name__ == "__main__":
    asyncio.run(main())
```

See `main.py` for a complete example implementation.

## Key Features

1. Version Control
- Tracks all changes to story elements
- Maintains chapter versions
- Logs decision history

2. Consistency Checking
- Character behavior verification
- Plot continuity checking
- Style and tone consistency

3. Progress Tracking
- Chapter completion status
- Plot point coverage
- Character arc progression

4. Error Handling
- API failure recovery
- Inconsistency detection
- Context overflow management

## Best Practices

1. Story Structure
- Begin with a clear outline
- Define characters thoroughly
- Establish style guide early

2. Chapter Generation
- Provide detailed chapter briefs
- Include relevant character and plot information
- Reference style guide consistently

3. Review Process
- Review for plot consistency
- Check character continuity
- Verify style adherence

4. Version Control
- Track all significant changes
- Maintain clear revision history
- Document decision rationale

## Future Improvements

1. Enhanced Analysis
- Sentiment analysis for scenes
- Character relationship tracking
- Theme consistency checking

2. Advanced Generation
- Multi-perspective chapter generation
- Dynamic character development
- Adaptive style matching

3. Workflow Optimization
- Parallel chapter generation
- Automated consistency checking
- Real-time collaboration features

## Technical Notes

- The system uses asyncio for concurrent operations
- Claude API integration requires valid API credentials
- Story data is persisted using JSON format
- Logging is configured for debugging and monitoring

## Error Handling

The system implements comprehensive error handling:

1. API Errors
- Automatic retries for transient failures
- Rate limiting compliance
- Graceful degradation

2. Consistency Errors
- Detection of plot holes
- Character inconsistencies
- Style violations

3. System Errors
- File I/O error handling
- Memory management
- Resource cleanup

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - See LICENSE file for details
