from abc import ABC, abstractmethod
from typing import List
from ..core.domain import RawTable

class BaseExtractor(ABC):
    """
    Abstract Base Class for all Extractors.
    所有提取器都必須繼承此類別，確保介面統一。
    """
    
    @abstractmethod
    def extract(self, source_path: str) -> List[RawTable]:
        """
        Extracts schema information from the given source path.
        
        Args:
            source_path: Path to the local directory (after cloning) or file.
            
        Returns:
            List[RawTable]: A list of raw table definitions.
        """
        pass
