# -*- coding: utf-8 -*-
"""testrail_api_reporter package"""

__version__ = "1.7.1"

# Engines
from .engines.at_coverage_reporter import ATCoverageReporter
from .engines.content_generator import TestCaseContentGenerator
from .engines.plotly_reporter import PlotlyReporter
from .engines.results_reporter import TestRailResultsReporter

# Publishers
from .publishers.confluence_sender import ConfluenceSender
from .publishers.email_sender import EmailSender
from .publishers.slack_sender import SlackSender
from .publishers.gdrive_uploader import GoogleDriveUploader

# Utils
from .utils.ai_providers import AIContentProvider, OpenAIProvider, CohereProvider, AnthropicProvider, CustomProvider
from .utils.reporter_utils import upload_image, delete_file, zip_file
from .utils.logger_config import setup_logger
