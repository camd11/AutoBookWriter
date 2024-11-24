"""
Editor module for reviewing and revising chapter content.
"""

import logging
from typing import Dict, List, Optional
from .models import Chapter, Story
from .config import APIConfig
from .reader import StoryAnalyzer

logger = logging.getLogger(__name__)

class ContentEditor:
    """Handles content review and revision"""
    
    def __init__(self, api_config: APIConfig, story: Story, analyzer: StoryAnalyzer):
        self.api_config = api_config
        self.story = story
        self.analyzer = analyzer
        self.style_violations: Dict[str, List[str]] = {}
        self.revision_history: Dict[str, List[Dict]] = {}
    
    async def review_chapter(self, chapter: Chapter) -> Dict[str, List[str]]:
        """Perform a comprehensive review of a chapter"""
        logger.info("Starting review for chapter: %s", chapter.title)
        
        # Get analysis from the reader module
        analysis = await self.analyzer.analyze_chapter(chapter)
        
        # Perform additional editorial checks
        editorial_review = await self._perform_editorial_review(chapter)
        
        # Combine all feedback
        review_results = {
            "style_issues": await self._check_style(chapter),
            "voice_consistency": await self._check_voice(chapter),
            "pacing_feedback": analysis.get("pacing", []),
            "content_issues": editorial_review.get("content_issues", []),
            "suggested_improvements": editorial_review.get("suggestions", [])
        }
        
        # Track style violations
        if review_results["style_issues"]:
            self.style_violations[chapter.id] = review_results["style_issues"]
        
        return review_results
    
    async def _perform_editorial_review(self, chapter: Chapter) -> Dict[str, List[str]]:
        """Perform detailed editorial review"""
        # TODO: Implement Claude API call for editorial review
        review = {
            "content_issues": [],
            "suggestions": []
        }
        
        # Check for common issues
        await self._check_grammar_and_spelling(chapter, review)
        await self._check_dialogue(chapter, review)
        await self._check_scene_structure(chapter, review)
        
        return review
    
    async def _check_style(self, chapter: Chapter) -> List[str]:
        """Check adherence to style guide"""
        issues = []
        
        # TODO: Implement style checking using Claude API
        # Compare against style guide rules
        style_guide = self.story.style_guide.content
        
        return issues
    
    async def _check_voice(self, chapter: Chapter) -> List[str]:
        """Check consistency of narrative voice"""
        issues = []
        
        # TODO: Implement voice consistency checking using Claude API
        # Analyze narrative perspective, tone, and voice
        
        return issues
    
    async def _check_grammar_and_spelling(self, chapter: Chapter, review: Dict) -> None:
        """Check grammar and spelling"""
        # TODO: Implement grammar and spelling check using Claude API
        pass
    
    async def _check_dialogue(self, chapter: Chapter, review: Dict) -> None:
        """Check dialogue formatting and authenticity"""
        # TODO: Implement dialogue checking using Claude API
        pass
    
    async def _check_scene_structure(self, chapter: Chapter, review: Dict) -> None:
        """Check scene structure and transitions"""
        # TODO: Implement scene structure analysis using Claude API
        pass
    
    async def generate_revision_request(self, chapter: Chapter, review_results: Dict) -> Dict:
        """Generate a structured revision request"""
        revision_request = {
            "chapter_id": chapter.id,
            "chapter_title": chapter.title,
            "revision_points": [],
            "priority_issues": [],
            "style_guide_references": []
        }
        
        # Compile revision points
        for category, issues in review_results.items():
            if issues:
                revision_request["revision_points"].extend(
                    [{"category": category, "issue": issue} for issue in issues]
                )
        
        # Identify priority issues
        revision_request["priority_issues"] = [
            point for point in revision_request["revision_points"]
            if self._is_priority_issue(point)
        ]
        
        # Add relevant style guide references
        revision_request["style_guide_references"] = self._get_relevant_style_rules(
            review_results["style_issues"]
        )
        
        # Track revision history
        if chapter.id not in self.revision_history:
            self.revision_history[chapter.id] = []
        self.revision_history[chapter.id].append(revision_request)
        
        return revision_request
    
    def _is_priority_issue(self, issue: Dict) -> bool:
        """Determine if an issue is high priority"""
        priority_categories = {"style_issues", "voice_consistency"}
        return issue["category"] in priority_categories
    
    def _get_relevant_style_rules(self, style_issues: List[str]) -> List[str]:
        """Get relevant rules from style guide"""
        # TODO: Implement style guide rule matching
        return []
    
    def get_revision_history(self, chapter_id: str) -> Optional[List[Dict]]:
        """Get the revision history for a chapter"""
        return self.revision_history.get(chapter_id)
    
    def get_style_violation_report(self) -> Dict[str, Dict]:
        """Generate a report of style violations across chapters"""
        report = {}
        for chapter_id, violations in self.style_violations.items():
            chapter = next(
                (ch for ch in self.story.chapters if ch.id == chapter_id),
                None
            )
            if chapter:
                report[chapter.title] = {
                    "violations_count": len(violations),
                    "violations": violations
                }
        return report
