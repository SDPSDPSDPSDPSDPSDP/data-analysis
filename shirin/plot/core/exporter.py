import os
from typing import Optional

import matplotlib.pyplot as plt


class PlotExporter:
    SUPPORTED_FORMATS = ['png', 'svg']
    
    def __init__(
        self,
        enabled: bool = True,
        output_dir: str = "./plot_output/",
        prefix: Optional[str] = None,
        format: str = 'png',
        auto_show: bool = True
    ):
        self.enabled = enabled
        self.output_dir = os.path.expanduser(output_dir)
        self.prefix = prefix
        self.format = format.lower()
        self.auto_show = auto_show
        
        self._validate_format()
        if self.enabled:
            os.makedirs(self.output_dir, exist_ok=True)
    
    def _validate_format(self) -> None:
        if self.format not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format '{self.format}'. "
                f"Supported formats are {self.SUPPORTED_FORMATS}."
            )
    
    def _create_filepath(self, output_name: str) -> str:
        if self.prefix:
            filename = f"{self.prefix}_{output_name}.{self.format}"
        else:
            filename = f"{output_name}.{self.format}"
        return os.path.join(self.output_dir, filename)
    
    def export_and_show(self, output_name: str) -> None:
        if self.enabled:
            filepath = self._create_filepath(output_name)
            plt.savefig(filepath, bbox_inches="tight", dpi=300, format=self.format)
        
        if self.auto_show:
            plt.show()
    
    def export_only(self, output_name: str) -> None:
        if self.enabled:
            filepath = self._create_filepath(output_name)
            plt.savefig(filepath, bbox_inches="tight", dpi=300, format=self.format)
    
    def show_only(self) -> None:
        if self.auto_show:
            plt.show()
