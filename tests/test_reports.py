import unittest
from reports.report_core import ReportGenerator, ReportType, ReportFilter
from datetime import datetime

class TestReports(unittest.TestCase):
    def setUp(self):
        self.generator = ReportGenerator("test_db.sqlite")

    def test_machine_project_report(self):
        filters = ReportFilter(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31)
        )
        df = self.generator.generate_report(ReportType.MACHINE_PROJECT, filters)
        self.assertIsNotNone(df)
        self.assertTrue('profit' in df.columns)
        self.assertTrue('shareholder_profit' in df.columns)

    # Add more tests... 