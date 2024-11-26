from typing import List, Dict, Optional, Any
from datetime import datetime
import json
import os
import logging
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import asyncio

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

class Message:
    def __init__(self, role: str, content: str, timestamp: Optional[datetime] = None, metadata: Dict[str, Any] = None):
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
        self.analyzed = False
        self.sentiment = None
        self.entities = []
        self.keywords = []
        
    def to_dict(self) -> Dict:
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'analyzed': self.analyzed,
            'sentiment': self.sentiment,
            'entities': self.entities,
            'keywords': self.keywords
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        msg = cls(
            role=data['role'],
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata', {})
        )
        msg.analyzed = data.get('analyzed', False)
        msg.sentiment = data.get('sentiment')
        msg.entities = data.get('entities', [])
        msg.keywords = data.get('keywords', [])
        return msg

class Conversation:
    def __init__(self, id: str, title: str):
        self.id = id
        self.title = title
        self.messages: List[Message] = []
        self.summary: str = ""
        self.topics: List[str] = []
        self.context_embeddings = None
        self.metadata: Dict[str, Any] = {}
        
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to the conversation"""
        self.messages.append(Message(role, content, metadata=metadata))
        
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'title': self.title,
            'messages': [m.to_dict() for m in self.messages],
            'summary': self.summary,
            'topics': self.topics,
            'metadata': self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'Conversation':
        conv = cls(data['id'], data['title'])
        conv.messages = [Message.from_dict(m) for m in data['messages']]
        conv.summary = data.get('summary', '')
        conv.topics = data.get('topics', [])
        conv.metadata = data.get('metadata', {})
        return conv
        
    def get_recent_context(self, max_messages: int = 10, include_metadata: bool = False) -> List[Dict]:
        """Get recent messages for context"""
        messages = self.messages[-max_messages:]
        if include_metadata:
            return [m.to_dict() for m in messages]
        return [{'role': m.role, 'content': m.content} for m in messages]
        
    def analyze_content(self):
        """Analyze conversation content"""
        # Initialize NLTK components
        lemmatizer = WordNetLemmatizer()
        stop_words = set(stopwords.words('english'))
        
        # Analyze all unanalyzed messages
        for message in self.messages:
            if not message.analyzed:
                # Tokenize and process text
                tokens = word_tokenize(message.content.lower())
                tokens = [lemmatizer.lemmatize(token) for token in tokens 
                         if token.isalnum() and token not in stop_words]
                
                # Extract keywords
                word_freq = Counter(tokens)
                message.keywords = [word for word, count in word_freq.most_common(5)]
                
                # Mark as analyzed
                message.analyzed = True
                
        # Update conversation topics
        all_keywords = []
        for message in self.messages:
            all_keywords.extend(message.keywords)
        
        # Update topics based on most common keywords
        word_freq = Counter(all_keywords)
        self.topics = [word for word, count in word_freq.most_common(10)]
        
    def generate_summary(self) -> str:
        """Generate a summary of the conversation"""
        # Combine recent messages
        recent_content = "\n".join([
            f"{m.role}: {m.content}" 
            for m in self.messages[-10:]  # Consider last 10 messages
        ])
        
        # Extract key sentences
        sentences = sent_tokenize(recent_content)
        
        # Simple extractive summarization
        if len(sentences) <= 3:
            self.summary = recent_content
        else:
            self.summary = " ".join(sentences[:3])  # Take first 3 sentences
            
        return self.summary

class ContextManager:
    def __init__(self, storage_dir: str = "conversations"):
        self.storage_dir = storage_dir
        self.current_conversation: Optional[Conversation] = None
        self.conversations: Dict[str, Conversation] = {}
        self.logger = logging.getLogger(__name__)
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        
        # Load existing conversations
        self.load_conversations()
        
    async def analyze_conversations(self):
        """Analyze all conversations"""
        for conv in self.conversations.values():
            conv.analyze_content()
            conv.generate_summary()
            await self.save_conversation(conv)
            
    async def save_conversation(self, conversation: Conversation):
        """Save a conversation to storage asynchronously"""
        try:
            filename = os.path.join(self.storage_dir, f"{conversation.id}.json")
            async with asyncio.Lock():
                with open(filename, 'w') as f:
                    json.dump(conversation.to_dict(), f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving conversation: {e}")
            
    def load_conversations(self):
        """Load conversations from storage"""
        try:
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json'):
                    with open(os.path.join(self.storage_dir, filename), 'r') as f:
                        data = json.load(f)
                        conv = Conversation.from_dict(data)
                        self.conversations[conv.id] = conv
        except Exception as e:
            self.logger.error(f"Error loading conversations: {e}")
            
    def new_conversation(self, title: str = "New Conversation", metadata: Dict[str, Any] = None) -> Conversation:
        """Create a new conversation"""
        conv_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        conversation = Conversation(conv_id, title)
        if metadata:
            conversation.metadata = metadata
        self.conversations[conv_id] = conversation
        self.current_conversation = conversation
        return conversation
        
    async def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to current conversation"""
        if not self.current_conversation:
            self.new_conversation()
        
        self.current_conversation.add_message(role, content, metadata)
        await self.save_conversation(self.current_conversation)
        
        # Analyze after adding message
        self.current_conversation.analyze_content()
        self.current_conversation.generate_summary()
        
    def get_context(self, max_messages: int = 10, include_metadata: bool = False) -> List[Dict]:
        """Get context from current conversation"""
        if not self.current_conversation:
            return []
            
        return self.current_conversation.get_recent_context(max_messages, include_metadata)
        
    def get_conversation_analysis(self, conv_id: str = None) -> Dict[str, Any]:
        """Get detailed analysis of a conversation"""
        conv = self.conversations.get(conv_id, self.current_conversation)
        if not conv:
            return {}
            
        # Ensure conversation is analyzed
        conv.analyze_content()
        
        return {
            'id': conv.id,
            'title': conv.title,
            'summary': conv.summary,
            'topics': conv.topics,
            'message_count': len(conv.messages),
            'participants': list(set(m.role for m in conv.messages)),
            'duration': (conv.messages[-1].timestamp - conv.messages[0].timestamp).total_seconds() if conv.messages else 0,
            'metadata': conv.metadata
        }
        
    def search_conversations(self, query: str, include_metadata: bool = False) -> List[Dict]:
        """Search conversations by content with advanced filtering"""
        results = []
        query_tokens = set(word_tokenize(query.lower()))
        
        for conv in self.conversations.values():
            matches = []
            relevance_score = 0
            
            for msg in conv.messages:
                msg_tokens = set(word_tokenize(msg.content.lower()))
                # Calculate token overlap
                overlap = len(query_tokens.intersection(msg_tokens))
                
                if overlap > 0:
                    match_data = {
                        'content': msg.content,
                        'timestamp': msg.timestamp.isoformat(),
                        'relevance': overlap / len(query_tokens)
                    }
                    if include_metadata:
                        match_data['metadata'] = msg.metadata
                        
                    matches.append(match_data)
                    relevance_score += match_data['relevance']
            
            if matches:
                results.append({
                    'id': conv.id,
                    'title': conv.title,
                    'matches': sorted(matches, key=lambda x: x['relevance'], reverse=True),
                    'relevance': relevance_score / len(matches),
                    'summary': conv.summary,
                    'topics': conv.topics
                })
                
        return sorted(results, key=lambda x: x['relevance'], reverse=True)
        
    async def cleanup(self):
        """Cleanup and save all conversations"""
        try:
            for conv in self.conversations.values():
                await self.save_conversation(conv)
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            
    def __del__(self):
        """Ensure cleanup on destruction"""
        asyncio.run(self.cleanup())
