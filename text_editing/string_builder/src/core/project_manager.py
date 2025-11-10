"""
Project Manager for String Builder Application
Handles project creation, loading, saving, and chunk management.
"""

import json
import os
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

@dataclass
class StringChunk:
    """Represents a text chunk in the string builder."""
    id: str
    content: str
    position: int
    created_at: str
    modified_at: str
    tags: List[str] = None
    formatting: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.formatting is None:
            self.formatting = {}

@dataclass
class Project:
    """Represents a string builder project."""
    id: str
    name: str
    description: str
    created_at: str
    modified_at: str
    chunks: List[StringChunk]
    output_format: str = "plain"
    separator: str = ""
    prefix: str = ""
    suffix: str = ""
    
    def __post_init__(self):
        if not self.chunks:
            self.chunks = []

class ProjectManager:
    """Manages string builder projects and chunks."""
    
    def __init__(self, settings_manager):
        """Initialize project manager."""
        self.settings_manager = settings_manager
        self.current_project: Optional[Project] = None
        self.projects: Dict[str, Project] = {}
        self.projects_directory = settings_manager.projects_directory
        
        self.load_projects()
        self.load_last_project()
    
    def create_project(self, name: str, description: str = "") -> Project:
        """Create a new project."""
        project_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        project = Project(
            id=project_id,
            name=name,
            description=description,
            created_at=timestamp,
            modified_at=timestamp,
            chunks=[]
        )
        
        self.projects[project_id] = project
        self.current_project = project
        self.settings_manager.last_project = project_id
        self.save_project(project)
        
        return project
    
    def load_projects(self):
        """Load all projects from disk."""
        if not os.path.exists(self.projects_directory):
            os.makedirs(self.projects_directory, exist_ok=True)
            return
        
        for filename in os.listdir(self.projects_directory):
            if filename.endswith('.json'):
                try:
                    project_path = os.path.join(self.projects_directory, filename)
                    with open(project_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Convert chunk data to StringChunk objects
                    chunks = []
                    for chunk_data in data.get('chunks', []):
                        chunk = StringChunk(**chunk_data)
                        chunks.append(chunk)
                    
                    # Create project object
                    project_data = data.copy()
                    project_data['chunks'] = chunks
                    project = Project(**project_data)
                    
                    self.projects[project.id] = project
                    
                except Exception as e:
                    print(f"Error loading project {filename}: {e}")
    
    def load_last_project(self):
        """Load the last opened project."""
        if self.settings_manager.last_project and self.settings_manager.last_project in self.projects:
            self.current_project = self.projects[self.settings_manager.last_project]
        elif self.projects:
            # Load the most recently modified project
            latest_project = max(self.projects.values(), key=lambda p: p.modified_at)
            self.current_project = latest_project
            self.settings_manager.last_project = latest_project.id
    
    def save_project(self, project: Project):
        """Save a project to disk."""
        try:
            project.modified_at = datetime.now().isoformat()
            
            # Convert to dictionary for JSON serialization
            project_data = asdict(project)
            
            project_file = os.path.join(self.projects_directory, f"{project.id}.json")
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving project: {e}")
    
    def save_current_project(self):
        """Save the current project."""
        if self.current_project:
            self.save_project(self.current_project)
    
    def switch_project(self, project_id: str) -> bool:
        """Switch to a different project."""
        if project_id in self.projects:
            # Save current project before switching
            self.save_current_project()
            
            self.current_project = self.projects[project_id]
            self.settings_manager.last_project = project_id
            return True
        return False
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        if project_id in self.projects:
            try:
                # Delete file
                project_file = os.path.join(self.projects_directory, f"{project_id}.json")
                if os.path.exists(project_file):
                    os.remove(project_file)
                
                # Remove from memory
                del self.projects[project_id]
                
                # Switch to another project if this was current
                if self.current_project and self.current_project.id == project_id:
                    if self.projects:
                        new_project = next(iter(self.projects.values()))
                        self.switch_project(new_project.id)
                    else:
                        self.current_project = None
                        self.settings_manager.last_project = None
                
                return True
            except Exception as e:
                print(f"Error deleting project: {e}")
                return False
        return False
    
    def add_chunk(self, content: str, position: Optional[int] = None) -> StringChunk:
        """Add a new chunk to the current project."""
        if not self.current_project:
            # Create a default project if none exists
            self.create_project("Default Project")
        
        chunk_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        if position is None:
            position = len(self.current_project.chunks)
        
        chunk = StringChunk(
            id=chunk_id,
            content=content,
            position=position,
            created_at=timestamp,
            modified_at=timestamp
        )
        
        # Insert chunk at specified position
        self.current_project.chunks.insert(position, chunk)
        
        # Update positions of subsequent chunks
        for i, chunk in enumerate(self.current_project.chunks):
            chunk.position = i
        
        self.save_current_project()
        return chunk
    
    def remove_chunk(self, chunk_id: str) -> bool:
        """Remove a chunk from the current project."""
        if not self.current_project:
            return False
        
        for i, chunk in enumerate(self.current_project.chunks):
            if chunk.id == chunk_id:
                self.current_project.chunks.pop(i)
                
                # Update positions of subsequent chunks
                for j, remaining_chunk in enumerate(self.current_project.chunks):
                    remaining_chunk.position = j
                
                self.save_current_project()
                return True
        return False
    
    def move_chunk(self, chunk_id: str, new_position: int) -> bool:
        """Move a chunk to a new position."""
        if not self.current_project:
            return False
        
        chunk = None
        old_position = None
        
        # Find the chunk
        for i, c in enumerate(self.current_project.chunks):
            if c.id == chunk_id:
                chunk = c
                old_position = i
                break
        
        if chunk is None or old_position is None:
            return False
        
        # Remove chunk from old position
        self.current_project.chunks.pop(old_position)
        
        # Insert at new position
        new_position = max(0, min(new_position, len(self.current_project.chunks)))
        self.current_project.chunks.insert(new_position, chunk)
        
        # Update all positions
        for i, c in enumerate(self.current_project.chunks):
            c.position = i
        
        chunk.modified_at = datetime.now().isoformat()
        self.save_current_project()
        return True
    
    def update_chunk(self, chunk_id: str, content: str) -> bool:
        """Update chunk content."""
        if not self.current_project:
            return False
        
        for chunk in self.current_project.chunks:
            if chunk.id == chunk_id:
                chunk.content = content
                chunk.modified_at = datetime.now().isoformat()
                self.save_current_project()
                return True
        return False
    
    def get_built_string(self) -> str:
        """Build the final string from all chunks."""
        if not self.current_project or not self.current_project.chunks:
            return ""
        
        # Sort chunks by position
        sorted_chunks = sorted(self.current_project.chunks, key=lambda c: c.position)
        
        # Join chunks with separator
        content_list = [chunk.content for chunk in sorted_chunks]
        result = self.current_project.separator.join(content_list)
        
        # Add prefix and suffix
        result = self.current_project.prefix + result + self.current_project.suffix
        
        return result
    
    def get_project_list(self) -> List[Dict[str, Any]]:
        """Get list of all projects with basic info."""
        return [
            {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'modified_at': project.modified_at,
                'chunk_count': len(project.chunks)
            }
            for project in self.projects.values()
        ]
