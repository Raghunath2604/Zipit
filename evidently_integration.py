#!/usr/bin/env python3
"""
Evidently AI Integration for MLOps Platform
Advanced drift detection, data quality monitoring, and model performance analysis
"""

from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset, TargetDriftPreset
from evidently.metrics import *
from evidently.test_suite import TestSuite
from evidently.tests import *
import pandas as pd
import numpy as np
import json
from datetime import datetime
import os

class EvidentlyManager:
    """Evidently AI integration for advanced monitoring"""
    
    def __init__(self, reports_path="/tmp/evidently_reports"):
        self.reports_path = reports_path
        os.makedirs(reports_path, exist_ok=True)
    
    def create_data_drift_report(self, reference_data, current_data, model_name, user_id):
        """Create comprehensive data drift report"""
        try:
            # Convert to DataFrames if needed
            if not isinstance(reference_data, pd.DataFrame):
                reference_data = pd.DataFrame(reference_data)
            if not isinstance(current_data, pd.DataFrame):
                current_data = pd.DataFrame(current_data)
            
            # Create drift report
            report = Report(metrics=[
                DataDriftPreset(),
                DataQualityPreset(),
                ColumnDriftMetric(column_name=reference_data.columns[0]),
                DatasetDriftMetric(),
                DatasetMissingValuesMetric()
            ])
            
            report.run(reference_data=reference_data, current_data=current_data)
            
            # Save report
            report_path = f"{self.reports_path}/drift_report_{user_id}_{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            report.save_html(report_path)
            
            # Extract key metrics
            report_dict = report.as_dict()
            drift_summary = self._extract_drift_summary(report_dict)
            
            return {
                "report_path": report_path,
                "drift_detected": drift_summary["dataset_drift"],
                "drift_score": drift_summary["drift_score"],
                "affected_features": drift_summary["drifted_features"],
                "data_quality_issues": drift_summary["quality_issues"],
                "summary": drift_summary
            }
            
        except Exception as e:
            return {"error": f"Drift report generation failed: {str(e)}"}
    
    def create_model_performance_report(self, reference_data, current_data, reference_target, current_target, model_name, user_id):
        """Create model performance comparison report"""
        try:
            # Prepare data
            ref_df = pd.DataFrame(reference_data)
            cur_df = pd.DataFrame(current_data)
            ref_df['target'] = reference_target
            cur_df['target'] = current_target
            
            # Column mapping
            column_mapping = ColumnMapping()
            column_mapping.target = 'target'
            
            # Create performance report
            report = Report(metrics=[
                TargetDriftPreset(),
                ClassificationPreset() if self._is_classification(reference_target) else RegressionPreset(),
                ColumnDriftMetric(column_name='target'),
                TargetByFeaturesTable()
            ])
            
            report.run(reference_data=ref_df, current_data=cur_df, column_mapping=column_mapping)
            
            # Save report
            report_path = f"{self.reports_path}/performance_report_{user_id}_{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            report.save_html(report_path)
            
            # Extract performance metrics
            report_dict = report.as_dict()
            performance_summary = self._extract_performance_summary(report_dict)
            
            return {
                "report_path": report_path,
                "target_drift": performance_summary["target_drift"],
                "performance_change": performance_summary["performance_change"],
                "summary": performance_summary
            }
            
        except Exception as e:
            return {"error": f"Performance report generation failed: {str(e)}"}
    
    def create_data_quality_report(self, data, model_name, user_id):
        """Create data quality assessment report"""
        try:
            if not isinstance(data, pd.DataFrame):
                data = pd.DataFrame(data)
            
            # Create data quality report
            report = Report(metrics=[
                DataQualityPreset(),
                DatasetMissingValuesMetric(),
                DatasetCorrelationsMetric(),
                ColumnSummaryMetric(column_name=data.columns[0]),
                ConflictTargetMetric() if 'target' in data.columns else None
            ])
            
            # Remove None metrics
            report.metrics = [m for m in report.metrics if m is not None]
            
            report.run(reference_data=data, current_data=None)
            
            # Save report
            report_path = f"{self.reports_path}/quality_report_{user_id}_{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            report.save_html(report_path)
            
            # Extract quality metrics
            report_dict = report.as_dict()
            quality_summary = self._extract_quality_summary(report_dict)
            
            return {
                "report_path": report_path,
                "quality_score": quality_summary["overall_score"],
                "issues": quality_summary["issues"],
                "recommendations": quality_summary["recommendations"],
                "summary": quality_summary
            }
            
        except Exception as e:
            return {"error": f"Data quality report generation failed: {str(e)}"}
    
    def run_test_suite(self, reference_data, current_data, model_name, user_id):
        """Run comprehensive test suite"""
        try:
            if not isinstance(reference_data, pd.DataFrame):
                reference_data = pd.DataFrame(reference_data)
            if not isinstance(current_data, pd.DataFrame):
                current_data = pd.DataFrame(current_data)
            
            # Create test suite
            tests = TestSuite(tests=[
                TestNumberOfColumnsWithMissingValues(),
                TestNumberOfRowsWithMissingValues(),
                TestNumberOfConstantColumns(),
                TestNumberOfDuplicatedRows(),
                TestNumberOfDuplicatedColumns(),
                TestColumnsType(),
                TestNumberOfDriftedColumns(),
                TestShareOfMissingValues(),
                TestMeanInNSigmas(column_name=reference_data.columns[0])
            ])
            
            tests.run(reference_data=reference_data, current_data=current_data)
            
            # Save test results
            test_path = f"{self.reports_path}/tests_{user_id}_{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            tests.save_html(test_path)
            
            # Extract test results
            test_results = tests.as_dict()
            test_summary = self._extract_test_summary(test_results)
            
            return {
                "test_path": test_path,
                "tests_passed": test_summary["passed"],
                "tests_failed": test_summary["failed"],
                "critical_issues": test_summary["critical"],
                "summary": test_summary
            }
            
        except Exception as e:
            return {"error": f"Test suite execution failed: {str(e)}"}
    
    def _extract_drift_summary(self, report_dict):
        """Extract key drift metrics from report"""
        try:
            metrics = report_dict.get("metrics", [])
            
            dataset_drift = False
            drift_score = 0.0
            drifted_features = []
            quality_issues = []
            
            for metric in metrics:
                if metric.get("metric") == "DatasetDriftMetric":
                    result = metric.get("result", {})
                    dataset_drift = result.get("dataset_drift", False)
                    drift_score = result.get("drift_score", 0.0)
                
                elif metric.get("metric") == "ColumnDriftMetric":
                    result = metric.get("result", {})
                    if result.get("drift_detected", False):
                        drifted_features.append(result.get("column_name"))
                
                elif metric.get("metric") == "DatasetMissingValuesMetric":
                    result = metric.get("result", {})
                    if result.get("number_of_missing_values", 0) > 0:
                        quality_issues.append("Missing values detected")
            
            return {
                "dataset_drift": dataset_drift,
                "drift_score": drift_score,
                "drifted_features": drifted_features,
                "quality_issues": quality_issues
            }
        except:
            return {"dataset_drift": False, "drift_score": 0.0, "drifted_features": [], "quality_issues": []}
    
    def _extract_performance_summary(self, report_dict):
        """Extract performance metrics from report"""
        try:
            metrics = report_dict.get("metrics", [])
            
            target_drift = False
            performance_change = {}
            
            for metric in metrics:
                if metric.get("metric") == "TargetDriftMetric":
                    result = metric.get("result", {})
                    target_drift = result.get("drift_detected", False)
            
            return {
                "target_drift": target_drift,
                "performance_change": performance_change
            }
        except:
            return {"target_drift": False, "performance_change": {}}
    
    def _extract_quality_summary(self, report_dict):
        """Extract data quality metrics from report"""
        try:
            metrics = report_dict.get("metrics", [])
            
            issues = []
            overall_score = 100
            recommendations = []
            
            for metric in metrics:
                if metric.get("metric") == "DatasetMissingValuesMetric":
                    result = metric.get("result", {})
                    missing_count = result.get("number_of_missing_values", 0)
                    if missing_count > 0:
                        issues.append(f"Missing values: {missing_count}")
                        overall_score -= 10
                        recommendations.append("Handle missing values before model training")
            
            return {
                "overall_score": max(0, overall_score),
                "issues": issues,
                "recommendations": recommendations
            }
        except:
            return {"overall_score": 100, "issues": [], "recommendations": []}
    
    def _extract_test_summary(self, test_results):
        """Extract test results summary"""
        try:
            tests = test_results.get("tests", [])
            
            passed = 0
            failed = 0
            critical = []
            
            for test in tests:
                status = test.get("status", "")
                if status == "SUCCESS":
                    passed += 1
                elif status == "FAIL":
                    failed += 1
                    test_name = test.get("name", "Unknown test")
                    if "missing" in test_name.lower() or "drift" in test_name.lower():
                        critical.append(test_name)
            
            return {
                "passed": passed,
                "failed": failed,
                "critical": critical
            }
        except:
            return {"passed": 0, "failed": 0, "critical": []}
    
    def _is_classification(self, target):
        """Check if target is classification or regression"""
        unique_values = len(set(target))
        return unique_values <= 10  # Assume classification if <= 10 unique values

# Integration with main platform
def integrate_evidently_with_platform():
    """Add Evidently endpoints to main platform"""
    from fastapi import APIRouter
    
    router = APIRouter(prefix="/api/evidently", tags=["Evidently"])
    evidently_manager = EvidentlyManager()
    
    @router.post("/drift/report")
    async def create_drift_report(user_id: int, model_name: str, reference_data: list, current_data: list):
        result = evidently_manager.create_data_drift_report(reference_data, current_data, model_name, user_id)
        return result
    
    @router.post("/performance/report")
    async def create_performance_report(user_id: int, model_name: str, reference_data: list, current_data: list, reference_target: list, current_target: list):
        result = evidently_manager.create_model_performance_report(reference_data, current_data, reference_target, current_target, model_name, user_id)
        return result
    
    @router.post("/quality/report")
    async def create_quality_report(user_id: int, model_name: str, data: list):
        result = evidently_manager.create_data_quality_report(data, model_name, user_id)
        return result
    
    @router.post("/tests/run")
    async def run_test_suite(user_id: int, model_name: str, reference_data: list, current_data: list):
        result = evidently_manager.run_test_suite(reference_data, current_data, model_name, user_id)
        return result
    
    return router