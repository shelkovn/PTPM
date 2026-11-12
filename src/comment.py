from dataclasses import dataclass

@dataclass
class Comment:
    #username
    name: str
    
    message: str

    id: int