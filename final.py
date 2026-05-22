#!/usr/bin/env python3
"""
Pokemon API Viewer
A program to view Pokemon information from the PokéAPI including:
- Generation when each Pokémon was introduced
- Types of each Pokémon
- First letter of each Pokémon's name
"""

import requests
import json
from typing import List, Dict, Optional
from collections import defaultdict


class PokemonViewer:
    """Class to interact with the PokéAPI and display Pokémon information."""
    
    BASE_URL = "https://pokeapi.co/api/v2/"
    
    def __init__(self):
        """Initialize the PokemonViewer."""
        self.session = requests.Session()
        self.pokemon_cache = {}
        self.generation_cache = {}
    
    def fetch_pokemon(self, pokemon_id: int) -> Optional[Dict]:
        """
        Fetch a single Pokémon by ID.
        
        Args:
            pokemon_id: The ID of the Pokémon to fetch
            
        Returns:
            Dictionary containing Pokémon data or None if not found
        """
        if pokemon_id in self.pokemon_cache:
            return self.pokemon_cache[pokemon_id]
        
        try:
            response = self.session.get(f"{self.BASE_URL}pokemon/{pokemon_id}/")
            response.raise_for_status()
            data = response.json()
            self.pokemon_cache[pokemon_id] = data
            return data
        except requests.RequestException as e:
            print(f"Error fetching Pokémon {pokemon_id}: {e}")
            return None
    
    def fetch_pokemon_list(self, limit: int = 151, offset: int = 0) -> Optional[List[Dict]]:
        """
        Fetch a list of Pokémon.
        
        Args:
            limit: Maximum number of Pokémon to fetch (default: 151 for Gen 1)
            offset: Number of Pokémon to skip (default: 0)
            
        Returns:
            List of Pokémon data or None if request fails
        """
        try:
            response = self.session.get(f"{self.BASE_URL}pokemon/", 
                                       params={"limit": limit, "offset": offset})
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except requests.RequestException as e:
            print(f"Error fetching Pokémon list: {e}")
            return None
    
    def get_pokemon_generation(self, pokemon_name: str) -> Optional[str]:
        """
        Get the generation in which a Pokémon was introduced.
        
        Args:
            pokemon_name: Name of the Pokémon
            
        Returns:
            Generation name (e.g., "Generation I") or None if not found
        """
        try:
            response = self.session.get(f"{self.BASE_URL}pokemon-species/{pokemon_name.lower()}/")
            response.raise_for_status()
            data = response.json()
            generation_url = data.get("generation", {}).get("url")
            
            if generation_url:
                gen_response = self.session.get(generation_url)
                gen_response.raise_for_status()
                gen_data = gen_response.json()
                return gen_data.get("name", "Unknown")
            return None
        except requests.RequestException as e:
            print(f"Error fetching generation for {pokemon_name}: {e}")
            return None
    
    def get_pokemon_types(self, pokemon_data: Dict) -> List[str]:
        """
        Extract types from Pokémon data.
        
        Args:
            pokemon_data: Dictionary containing Pokémon data
            
        Returns:
            List of type names
        """
        types = []
        for type_info in pokemon_data.get("types", []):
            type_name = type_info.get("type", {}).get("name", "Unknown")
            types.append(type_name.capitalize())
        return types
    
    def display_pokemon_info(self, pokemon_data: Dict, generation: Optional[str] = None):
        """
        Display formatted information about a Pokémon.
        
        Args:
            pokemon_data: Dictionary containing Pokémon data
            generation: Generation name (if already fetched)
        """
        name = pokemon_data.get("name", "Unknown").capitalize()
        pokemon_id = pokemon_data.get("id", "?")
        types = self.get_pokemon_types(pokemon_data)
        first_letter = name[0].upper() if name else "?"
        
        # Fetch generation if not provided
        if generation is None:
            generation = self.get_pokemon_generation(name)
        
        generation_display = generation if generation else "Unknown"
        types_display = ", ".join(types) if types else "Unknown"
        
        print(f"\n{'='*60}")
        print(f"ID: {pokemon_id:3d} | Name: {name:15s} | First Letter: {first_letter}")
        print(f"{'='*60}")
        print(f"Generation: {generation_display}")
        print(f"Types: {types_display}")
        print(f"{'='*60}")
    
    def display_multiple_pokemon(self, pokemon_list: List[Dict]):
        """
        Display information for multiple Pokémon in a table format.
        
        Args:
            pokemon_list: List of Pokémon data
        """
        print("\n" + "="*100)
        print(f"{'ID':<5} {'Name':<20} {'First Letter':<15} {'Types':<40}")
        print("="*100)
        
        for pokemon_data in pokemon_list:
            name = pokemon_data.get("name", "Unknown").capitalize()
            pokemon_id = pokemon_data.get("id", "?")
            first_letter = name[0].upper() if name else "?"
            types = self.get_pokemon_types(pokemon_data)
            types_display = ", ".join(types) if types else "Unknown"
            
            print(f"{pokemon_id:<5} {name:<20} {first_letter:<15} {types_display:<40}")
        
        print("="*100 + "\n")
    
    def filter_by_first_letter(self, pokemon_list: List[Dict], letter: str) -> List[Dict]:
        """
        Filter Pokémon by the first letter of their name.
        
        Args:
            pokemon_list: List of Pokémon data
            letter: The letter to filter by
            
        Returns:
            Filtered list of Pokémon
        """
        letter = letter.upper()
        return [p for p in pokemon_list if p.get("name", "").upper().startswith(letter)]
    
    def filter_by_type(self, pokemon_list: List[Dict], pokemon_type: str) -> List[Dict]:
        """
        Filter Pokémon by type.
        
        Args:
            pokemon_list: List of Pokémon data
            pokemon_type: The type to filter by
            
        Returns:
            Filtered list of Pokémon with that type
        """
        filtered = []
        for pokemon in pokemon_list:
            types = self.get_pokemon_types(pokemon)
            if pokemon_type.capitalize() in types:
                filtered.append(pokemon)
        return filtered
    
    def interactive_menu(self):
        """Run an interactive menu for exploring Pokémon."""
        print("\n" + "="*60)
        print("Welcome to the Pokémon API Viewer!")
        print("="*60)
        
        while True:
            print("\n--- Main Menu ---")
            print("1. View Pokémon by Generation")
            print("2. Search for a specific Pokémon")
            print("3. Filter Pokémon by First Letter")
            print("4. Filter Pokémon by Type")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                self.show_generation_menu()
            elif choice == "2":
                self.search_pokemon()
            elif choice == "3":
                self.filter_by_letter_menu()
            elif choice == "4":
                self.filter_by_type_menu()
            elif choice == "5":
                print("\nThank you for using Pokémon API Viewer!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def show_generation_menu(self):
        """Show menu for viewing Pokémon by generation."""
        generations = {
            "1": (1, 151, "Generation I"),
            "2": (152, 251, "Generation II"),
            "3": (252, 386, "Generation III"),
            "4": (387, 493, "Generation IV"),
            "5": (494, 649, "Generation V"),
            "6": (650, 721, "Generation VI"),
            "7": (722, 809, "Generation VII"),
            "8": (810, 905, "Generation VIII"),
        }
        
        print("\nSelect a Generation:")
        for key, (_, _, name) in generations.items():
            print(f"{key}. {name}")
        
        gen_choice = input("Enter generation (1-8): ").strip()
        
        if gen_choice in generations:
            start_id, end_id, gen_name = generations[gen_choice]
            offset = start_id - 1
            limit = end_id - start_id + 1
            
            print(f"\nLoading {gen_name}...")
            pokemon_list = self.fetch_pokemon_list(limit=limit, offset=offset)
            
            if pokemon_list:
                # Fetch full data for each Pokémon
                full_pokemon_list = []
                for pokemon in pokemon_list:
                    pokemon_id = pokemon["url"].split("/")[-2]
                    full_data = self.fetch_pokemon(int(pokemon_id))
                    if full_data:
                        full_pokemon_list.append(full_data)
                
                self.display_multiple_pokemon(full_pokemon_list)
    
    def search_pokemon(self):
        """Search for a specific Pokémon."""
        name = input("\nEnter Pokémon name or ID: ").strip()
        
        try:
            # Try as ID first
            if name.isdigit():
                pokemon = self.fetch_pokemon(int(name))
            else:
                # Try as name
                response = self.session.get(f"{self.BASE_URL}pokemon/{name.lower()}/")
                response.raise_for_status()
                pokemon = response.json()
            
            if pokemon:
                generation = self.get_pokemon_generation(pokemon.get("name", name))
                self.display_pokemon_info(pokemon, generation)
        except requests.RequestException:
            print(f"Pokémon '{name}' not found.")
    
    def filter_by_letter_menu(self):
        """Filter and display Pokémon by first letter."""
        letter = input("\nEnter a letter (A-Z): ").strip().upper()
        
        if len(letter) != 1 or not letter.isalpha():
            print("Please enter a single letter.")
            return
        
        print(f"\nLoading all Pokémon starting with '{letter}'...")
        pokemon_list = self.fetch_pokemon_list(limit=1000, offset=0)
        
        if pokemon_list:
            # Fetch full data
            full_pokemon_list = []
            for pokemon in pokemon_list:
                pokemon_id = pokemon["url"].split("/")[-2]
                full_data = self.fetch_pokemon(int(pokemon_id))
                if full_data:
                    full_pokemon_list.append(full_data)
            
            filtered = self.filter_by_first_letter(full_pokemon_list, letter)
            
            if filtered:
                print(f"\nFound {len(filtered)} Pokémon starting with '{letter}':")
                self.display_multiple_pokemon(filtered)
            else:
                print(f"No Pokémon found starting with '{letter}'.")
    
    def filter_by_type_menu(self):
        """Filter and display Pokémon by type."""
        pokemon_type = input("\nEnter Pokémon type (Fire, Water, Grass, etc.): ").strip()
        
        print(f"\nLoading all Pokémon of type '{pokemon_type}'...")
        pokemon_list = self.fetch_pokemon_list(limit=1000, offset=0)
        
        if pokemon_list:
            # Fetch full data
            full_pokemon_list = []
            for pokemon in pokemon_list:
                pokemon_id = pokemon["url"].split("/")[-2]
                full_data = self.fetch_pokemon(int(pokemon_id))
                if full_data:
                    full_pokemon_list.append(full_data)
            
            filtered = self.filter_by_type(full_pokemon_list, pokemon_type)
            
            if filtered:
                print(f"\nFound {len(filtered)} Pokémon of type '{pokemon_type.capitalize()}':")
                self.display_multiple_pokemon(filtered)
            else:
                print(f"No Pokémon found of type '{pokemon_type}'.")


def main():
    """Main entry point."""
    viewer = PokemonViewer()
    viewer.interactive_menu()


if __name__ == "__main__":
    main()
