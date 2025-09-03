"""In-Memory Storage Implementation

This module provides an in-memory storage implementation for company configurations
with thread-safe operations and comprehensive error handling.
"""

import threading
from typing import Dict, List, Optional
from datetime import datetime

from ..models.company import CompanyConfiguration


class CompanyNotFoundError(Exception):
    """Raised when a company configuration is not found."""
    
    def __init__(self, company_name: str):
        self.company_name = company_name
        super().__init__(f"Company configuration not found: {company_name}")


class CompanyAlreadyExistsError(Exception):
    """Raised when trying to create a company that already exists."""
    
    def __init__(self, company_name: str):
        self.company_name = company_name
        super().__init__(f"Company configuration already exists: {company_name}")


class CompanyConfigStorage:
    """In-memory storage for company configurations.
    
    Provides thread-safe CRUD operations for managing company configurations
    in memory. Suitable for development and testing environments.
    """
    
    def __init__(self):
        """Initialize the storage with an empty configuration store."""
        self._configurations: Dict[str, CompanyConfiguration] = {}
        self._lock = threading.RLock()  # Reentrant lock for thread safety
    
    def create(self, configuration: CompanyConfiguration) -> CompanyConfiguration:
        """Create a new company configuration.
        
        Args:
            configuration: The company configuration to store
            
        Returns:
            The stored configuration with updated timestamps
            
        Raises:
            CompanyAlreadyExistsError: If a company with this name already exists
        """
        company_name = configuration.company_name.lower().strip()
        
        with self._lock:
            if company_name in self._configurations:
                raise CompanyAlreadyExistsError(configuration.company_name)
            
            # Update timestamps
            now = datetime.utcnow()
            configuration.created_at = now
            configuration.updated_at = now
            
            # Store configuration
            self._configurations[company_name] = configuration
            
            return configuration
    
    def get(self, company_name: str) -> CompanyConfiguration:
        """Retrieve a company configuration by name.
        
        Args:
            company_name: Name of the company to retrieve
            
        Returns:
            The company configuration
            
        Raises:
            CompanyNotFoundError: If the company is not found
        """
        normalized_name = company_name.lower().strip()
        
        with self._lock:
            if normalized_name not in self._configurations:
                raise CompanyNotFoundError(company_name)
            
            return self._configurations[normalized_name]
    
    def get_all(self) -> List[CompanyConfiguration]:
        """Retrieve all company configurations.
        
        Returns:
            List of all stored company configurations, sorted by name
        """
        with self._lock:
            configurations = list(self._configurations.values())
            # Sort by company name for consistent ordering
            configurations.sort(key=lambda x: x.company_name.lower())
            return configurations
    
    def update(self, company_name: str, configuration: CompanyConfiguration) -> CompanyConfiguration:
        """Update an existing company configuration.
        
        Args:
            company_name: Name of the company to update
            configuration: Updated configuration data
            
        Returns:
            The updated configuration
            
        Raises:
            CompanyNotFoundError: If the company is not found
        """
        normalized_name = company_name.lower().strip()
        
        with self._lock:
            if normalized_name not in self._configurations:
                raise CompanyNotFoundError(company_name)
            
            # Preserve creation timestamp, update modification timestamp
            original_config = self._configurations[normalized_name]
            configuration.created_at = original_config.created_at
            configuration.updated_at = datetime.utcnow()
            
            # Update storage
            # If the company name changed, we need to handle the key change
            new_normalized_name = configuration.company_name.lower().strip()
            
            if normalized_name != new_normalized_name:
                # Check if new name conflicts with existing company
                if new_normalized_name in self._configurations:
                    raise CompanyAlreadyExistsError(configuration.company_name)
                
                # Remove old entry and add new one
                del self._configurations[normalized_name]
                self._configurations[new_normalized_name] = configuration
            else:
                # Same name, just update in place
                self._configurations[normalized_name] = configuration
            
            return configuration
    
    def delete(self, company_name: str) -> CompanyConfiguration:
        """Delete a company configuration.
        
        Args:
            company_name: Name of the company to delete
            
        Returns:
            The deleted configuration
            
        Raises:
            CompanyNotFoundError: If the company is not found
        """
        normalized_name = company_name.lower().strip()
        
        with self._lock:
            if normalized_name not in self._configurations:
                raise CompanyNotFoundError(company_name)
            
            # Remove and return the configuration
            return self._configurations.pop(normalized_name)
    
    def exists(self, company_name: str) -> bool:
        """Check if a company configuration exists.
        
        Args:
            company_name: Name of the company to check
            
        Returns:
            True if the company exists, False otherwise
        """
        normalized_name = company_name.lower().strip()
        
        with self._lock:
            return normalized_name in self._configurations
    
    def count(self) -> int:
        """Get the total number of stored configurations.
        
        Returns:
            Number of company configurations in storage
        """
        with self._lock:
            return len(self._configurations)
    
    def clear(self) -> None:
        """Clear all stored configurations.
        
        This method is primarily intended for testing purposes.
        """
        with self._lock:
            self._configurations.clear()
    
    def search(self, query: str) -> List[CompanyConfiguration]:
        """Search for companies by name, aliases, or email domain.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching company configurations
        """
        if not query or not query.strip():
            return self.get_all()
        
        query_lower = query.lower().strip()
        
        with self._lock:
            matches = []
            
            for config in self._configurations.values():
                # Check company name
                if query_lower in config.company_name.lower():
                    matches.append(config)
                    continue
                
                # Check aliases
                if any(query_lower in alias.lower() for alias in config.profile.aliases):
                    matches.append(config)
                    continue
                
                # Check email domain
                if query_lower in config.profile.email_domain.lower():
                    matches.append(config)
                    continue
                
                # Check industry
                if config.profile.industry and query_lower in config.profile.industry.lower():
                    matches.append(config)
                    continue
            
            # Sort matches by relevance (exact name matches first, then partial)
            def sort_key(config):
                name_lower = config.company_name.lower()
                if name_lower == query_lower:
                    return 0  # Exact match
                elif name_lower.startswith(query_lower):
                    return 1  # Starts with query
                else:
                    return 2  # Contains query
            
            matches.sort(key=sort_key)
            return matches


# Create a global instance for the application
storage = CompanyConfigStorage()


__all__ = [
    'CompanyConfigStorage',
    'CompanyNotFoundError',
    'CompanyAlreadyExistsError',
    'storage'
]