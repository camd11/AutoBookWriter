from openai import OpenAI
import os
from datetime import datetime
import logging
import json
from config.env_loader import ensure_env_loaded

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
ensure_env_loaded()

def setup_logging(module_name):
    """Setup logging for each module with timestamps"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_dir = os.path.join('logs', module_name)
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f'{timestamp}.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    logger = logging.getLogger(module_name)
    logger.addHandler(file_handler)
    
    return logger

class AIClient:
    def __init__(self, module_name):
        # Get API key from environment variable
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY environment variable is not set. "
                "Please set it before running the application. "
                "Example: export OPENROUTER_API_KEY='your-api-key'"
            )
            
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.logger = setup_logging(module_name)
        self.extra_headers = {
            "HTTP-Referer": "http://localhost",
            "X-Title": "NovelAI-Generator",
        }
        self.conversation_history = {}  # Store conversation history by conversation_id
        self.module_name = module_name
        
        # Setup conversation logging
        self.conversation_log_dir = os.path.join('logs', 'conversations')
        os.makedirs(self.conversation_log_dir, exist_ok=True)
        self.master_log_path = os.path.join('logs', 'master_conversation_log.json')
        self.master_log = self._load_or_create_master_log()

    def _load_or_create_master_log(self):
        """Load existing master log or create new one"""
        if os.path.exists(self.master_log_path):
            with open(self.master_log_path, 'r') as f:
                return json.load(f)
        return {
            "project_start_time": datetime.now().strftime('%Y%m%d_%H%M%S'),
            "conversations": {}
        }

    def _save_master_log(self):
        """Save master log to disk"""
        with open(self.master_log_path, 'w') as f:
            json.dump(self.master_log, f, indent=4)

    def _log_conversation(self, conversation_id, messages, response):
        """Log conversation to both individual file and master log"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create conversation entry
        conversation_entry = {
            "module": self.module_name,
            "timestamp": timestamp,
            "messages": messages,
            "response": response
        }
        
        # Save to individual conversation log
        conv_log_path = os.path.join(
            self.conversation_log_dir, 
            f'conversation_{conversation_id}_{timestamp}.json'
        )
        with open(conv_log_path, 'w') as f:
            json.dump(conversation_entry, f, indent=4)
        
        # Update master log
        if conversation_id not in self.master_log["conversations"]:
            self.master_log["conversations"][conversation_id] = []
        self.master_log["conversations"][conversation_id].append(conversation_entry)
        self._save_master_log()

    async def get_completion(self, messages, conversation_id=None, temperature=0.7):
        """Get completion from Claude API with conversation history"""
        try:
            # If conversation_id provided, append to existing history
            if conversation_id:
                if conversation_id not in self.conversation_history:
                    self.conversation_history[conversation_id] = []
                conversation_messages = self.conversation_history[conversation_id] + messages
            else:
                conversation_messages = messages

            completion = self.client.chat.completions.create(
                extra_headers=self.extra_headers,
                model="anthropic/claude-3.5-sonnet:beta",
                messages=conversation_messages,
                temperature=temperature
            )
            
            response = completion.choices[0].message.content
            
            # Update conversation history if conversation_id provided
            if conversation_id:
                self.conversation_history[conversation_id].extend([
                    messages[-1],  # Add user's message
                    {"role": "assistant", "content": response}  # Add AI's response
                ])
                # Log conversation update
                self.logger.info(f"Updated conversation {conversation_id} history. Current length: {len(self.conversation_history[conversation_id])}")
            
            # Log the interaction
            self._log_conversation(
                conversation_id or "single_interaction",
                messages,
                response
            )
            
            self.logger.info(f"Generated response for prompt: {messages[-1]['content'][:100]}...")
            return response
            
        except Exception as e:
            self.logger.error(f"Error getting completion: {str(e)}")
            raise

    def start_conversation(self):
        """Start a new conversation and return its ID"""
        conversation_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.conversation_history[conversation_id] = []
        self.logger.info(f"Started new conversation: {conversation_id}")
        return conversation_id

    def end_conversation(self, conversation_id):
        """End a conversation and clean up its history"""
        if conversation_id in self.conversation_history:
            # Log final conversation state before ending
            self._log_conversation(
                conversation_id,
                self.conversation_history[conversation_id],
                "CONVERSATION_ENDED"
            )
            del self.conversation_history[conversation_id]
            self.logger.info(f"Ended conversation: {conversation_id}")

    def get_conversation_history(self, conversation_id):
        """Get the history of a specific conversation"""
        return self.conversation_history.get(conversation_id, [])

    def clear_conversation_history(self, conversation_id=None):
        """Clear conversation history for one or all conversations"""
        if conversation_id:
            if conversation_id in self.conversation_history:
                self.conversation_history[conversation_id] = []
                self.logger.info(f"Cleared history for conversation: {conversation_id}")
        else:
            self.conversation_history = {}
            self.logger.info("Cleared all conversation histories")
