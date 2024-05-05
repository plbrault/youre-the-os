from dataclasses import dataclass

@dataclass
class WindowConfig:
    size: tuple[int,int]
    title: str
    icon_path: str
