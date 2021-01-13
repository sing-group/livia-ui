from argparse import FileType, Namespace
from functools import reduce
from typing import Optional, List, Tuple

from livia.input.FileFrameInput import FileFrameInput
from livia.output.FileFrameOutput import FileFrameOutput
from livia.process.analyzer.AnalyzerFrameProcessor import AnalyzerFrameProcessor
from livia.process.analyzer.FrameAnalyzerManager import FrameAnalyzerManager
from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerMetadata
from livia.process.analyzer.NoChangeFrameAnalyzer import NoChangeFrameAnalyzer
from livia.process.listener.ProcessChangeEvent import ProcessChangeEvent
from livia.process.listener.ProcessChangeListener import ProcessChangeListener
from livia_ui.cli import LIVIA_CLI_LOGGER
from livia_ui.cli.command.ArgumentsCommand import ArgumentsCommand


class ProcessorListener(ProcessChangeListener):
    def started(self, event: ProcessChangeEvent):
        LIVIA_CLI_LOGGER.info(f"Video analysis started")

    def stopped(self, event: ProcessChangeEvent):
        event.processor.close()

    def finished(self, event: ProcessChangeEvent):
        LIVIA_CLI_LOGGER.info(f"Video analysis finished")


class ProcessArgumentsCommand(ArgumentsCommand):
    def __init__(self):
        super().__init__("process", "Video processing")

    def _build_subparser(self, subparser):
        subparser.add_argument("-in", "--input", dest="input", type=FileType("r"), required=True,
                               help="Video input file")
        subparser.add_argument("-out", "--output", dest="output", type=FileType("w"), required=True,
                               help="Video output file")

        for analyzer in FrameAnalyzerManager.list_analyzers():
            group = subparser.add_argument_group("Analyzer " + analyzer.name)

            short_prefix = f"-an-{analyzer.id}-"
            long_prefix = f"--analyzer-{analyzer.id}-"

            group.add_argument(short_prefix + "order", long_prefix + "order", type=int, required=False,
                               help="Priority order of the analyzer")

            for prop in analyzer.properties:
                group.add_argument(short_prefix + prop.id, long_prefix + prop.id, help=prop.prop.__doc__,
                                   required=False)

    def execute_command(self, args: Namespace):
        analyzer = self._build_analyzer(args)

        LIVIA_CLI_LOGGER.info(f"Processing {args.input.name} to {args.output.name}")
        input = FileFrameInput(args.input.name, delay=0)
        output = FileFrameOutput(args.output.name, input.get_fps(), *input.get_frame_size())

        processor = AnalyzerFrameProcessor(input, output, analyzer, daemon=False)
        processor.add_process_change_listener(ProcessorListener())

        processor.start()

    def _build_analyzer(self, args):
        analyzers: List[(int, FrameAnalyzerMetadata)] = []

        for analyzer_metadata in FrameAnalyzerManager.list_analyzers():
            analyzer_args, order = ProcessArgumentsCommand._extract_args_for_analyzer(args, analyzer_metadata)

            if analyzer_args is not None:
                analyzer = analyzer_metadata.analyzer_class()
                for prop_id, value in analyzer_args.__dict__.items():
                    prop = analyzer_metadata.get_property_by_id(prop_id)
                    if prop is not None:
                        setattr(analyzer, prop.name, value)
                analyzers.append((order, analyzer))

        if analyzers:
            analyzers.sort(key=lambda item: item[0], reverse=True)

            def add_child(a1, a2):
                a1.child = a2
                return a1

            analyzer = reduce(add_child, [analyzer_order[1] for analyzer_order in analyzers])
        else:
            analyzer = NoChangeFrameAnalyzer()

        return analyzer

    @staticmethod
    def _extract_args_for_analyzer(args: Namespace, analyzer: FrameAnalyzerMetadata) ->\
            Tuple[Optional[Namespace], Optional[int]]:
        def arg(arg_id):
            return f"analyzer_{analyzer.id}_{arg_id}".replace("-", "_")

        order = getattr(args, arg("order"))
        if order is None:
            return None, None
        else:
            analyzer_args = Namespace()

            for prop in analyzer.properties:
                arg_value = getattr(args, arg(prop.id))
                if arg_value is not None:
                    setattr(analyzer_args, prop.id, arg_value)

            return analyzer_args, order
