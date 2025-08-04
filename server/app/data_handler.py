import json
import os
from typing import Optional, Dict, List
from .config import Config

class DataHandler:
    """Handles data operations for countries and states."""
    
    def __init__(self):
        self.countries = self._load_countries()
        self.states = self._load_states()
    
    def _load_countries(self) -> List[Dict[str, str]]:
        """Load countries data from JSON file."""
        try:
            file_path = os.path.join(os.path.dirname(__file__), "..", Config.COUNTRIES_DATA_PATH)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("countries", [])
        except FileNotFoundError:
            print(f"Warning: Countries data file not found at {Config.COUNTRIES_DATA_PATH}")
            return []
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in countries data file")
            return []
    
    def _load_states(self) -> List[Dict[str, str]]:
        """Load US states data from JSON file."""
        try:
            file_path = os.path.join(os.path.dirname(__file__), "..", Config.STATES_DATA_PATH)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("states", [])
        except FileNotFoundError:
            print(f"Warning: States data file not found at {Config.STATES_DATA_PATH}")
            return []
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in states data file")
            return []
    
    def find_country_capital(self, country_name: str) -> Optional[str]:
        """Find the capital of a country by name."""
        country_name_lower = country_name.lower().strip()
        
        for country in self.countries:
            if country["name"].lower() == country_name_lower:
                return country["capital"]
        
        return None
    
    def find_state_capital(self, state_name: str) -> Optional[str]:
        """Find the capital of a US state by name."""
        state_name_lower = state_name.lower().strip()
        
        for state in self.states:
            if state["name"].lower() == state_name_lower:
                return state["capital"]
        
        return None
    
    def find_capital(self, query: str) -> Optional[str]:
        """Find capital for either a country or state."""
        # First try to find as a country
        capital = self.find_country_capital(query)
        if capital:
            return capital
        
        # If not found as country, try as state
        capital = self.find_state_capital(query)
        if capital:
            return capital
        
        return None
    
    def get_all_countries(self) -> List[str]:
        """Get list of all country names."""
        return [country["name"] for country in self.countries]
    
    def get_all_states(self) -> List[str]:
        """Get list of all US state names."""
        return [state["name"] for state in self.states]
    
    def get_data_summary(self) -> Dict[str, int]:
        """Get summary of loaded data."""
        return {
            "countries_count": len(self.countries),
            "states_count": len(self.states)
        } 