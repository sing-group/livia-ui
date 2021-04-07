from typing import List, Any, Tuple

from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerPropertyMetadata


class LiveAnalyzerConfiguration:
    def __init__(self, config_name: str, analyzer_id: str,
                 analyzer_params: List[Tuple[FrameAnalyzerPropertyMetadata, Any]]):
        self._configuration_name: str = config_name
        self._analyzer_id: str = analyzer_id
        self._analyzer_params: List[Tuple[FrameAnalyzerPropertyMetadata, Any]] = analyzer_params

    @property
    def configuration_name(self):
        return self._configuration_name

    @configuration_name.setter
    def configuration_name(self, new_name: str):
        self._configuration_name = new_name

    @property
    def analyzer_id(self) -> str:
        return self._analyzer_id

    @property
    def parameters(self) -> List[Tuple[FrameAnalyzerPropertyMetadata, Any]]:
        return self._analyzer_params
