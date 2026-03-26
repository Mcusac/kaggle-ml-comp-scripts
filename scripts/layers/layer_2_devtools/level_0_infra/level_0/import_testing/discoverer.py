"""Module discovery for import testing."""

import sys
from pathlib import Path
from dataclasses import dataclass


@dataclass
class DiscoveryConfig:
    """Configuration for module discovery."""
    scripts_dir: Path
    exclude_packages: set[str] = None
    
    def __post_init__(self):
        if self.exclude_packages is None:
            self.exclude_packages = {'dev', '__pycache__', '.git'}


class ModuleDiscoverer:
    """
    Discover Python modules and packages in codebase.
    
    Automatically detects packages and resolves module paths.
    """
    
    def __init__(self, config: DiscoveryConfig):
        """
        Initialize discoverer.
        
        Args:
            config: Discovery configuration
        """
        self.config = config
        self.codebase_packages = self._discover_packages()
        
        # Ensure scripts directory is in path
        if str(self.config.scripts_dir) not in sys.path:
            sys.path.insert(0, str(self.config.scripts_dir))
    
    def _discover_packages(self) -> set[str]:
        """Discover all packages in codebase."""
        packages = set()
        
        for item in self.config.scripts_dir.iterdir():
            if not item.is_dir():
                continue
            
            if (item.name.startswith('_') or 
                item.name.startswith('.') or
                item.name in self.config.exclude_packages):
                continue
            
            # Check if it's a Python package
            init_file = item / '__init__.py'
            has_py_files = any(f.is_file() and f.suffix == '.py' for f in item.iterdir() if not f.name.startswith('.'))
            
            if init_file.exists() or has_py_files:
                packages.add(item.name)
        
        return packages
    
    def discover_modules_in_package(self, package_name: str) -> list[str]:
        """
        Recursively discover all modules in a package.
        
        Args:
            package_name: Base package name (e.g., 'config')
            
        Returns:
            List of full module paths
        """
        package_root = self.config.scripts_dir / package_name
        if not package_root.exists():
            return []
        
        modules = []
        
        def walk_package(path: Path, current_module: str):
            """Recursively walk package directory."""
            for item in sorted(path.iterdir()):
                # Skip test files, pycache, hidden files
                if (item.name.startswith('test_') or 
                    item.name == '__pycache__' or 
                    item.name.startswith('.')):
                    continue
                
                if item.is_file() and item.suffix == '.py':
                    # Skip __init__.py (handled as package)
                    if item.stem != '__init__':
                        module_name = f"{current_module}.{item.stem}"
                        modules.append(module_name)
                
                elif item.is_dir() and not item.name.startswith('_') and not item.name.startswith('.'):
                    # Package directory
                    init_file = item / '__init__.py'
                    if init_file.exists():
                        new_module = f"{current_module}.{item.name}"
                        modules.append(new_module)
                        walk_package(item, new_module)
        
        walk_package(package_root, package_name)
        return sorted(modules)
    
    def get_all_modules(self) -> dict[str, list[str]]:
        """
        Get all modules grouped by package.
        
        Returns:
            Dictionary mapping package names to module lists
        """
        all_modules = {}
        for package in sorted(self.codebase_packages):
            modules = self.discover_modules_in_package(package)
            all_modules[package] = modules
        
        return all_modules
