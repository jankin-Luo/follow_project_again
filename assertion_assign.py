import enum
from enum import Enum, auto
import logging
import allure
from typing import Dict, Any, List, Tuple

# 日志配置
logs = logging.getLogger(__name__)


class IssueSeverity(Enum):
    """问题严重性级别"""
    CRITICAL = "致命级"
    HIGH = "重要级"
    MEDIUM = "警告级"
    LOW = "信息级"


class IssueCategory(Enum):
    """问题分类枚举"""

    # 技术问题
    TECHNICAL_ENV = "技术问题-环境配置"
    TECHNICAL_DEPENDENCY = "技术问题-依赖服务"
    TECHNICAL_LOGIC = "技术问题-代码逻辑"
    TECHNICAL_DATA = "技术问题-测试数据"

    # 业务问题
    BUSINESS_RULE = "业务问题-业务规则"
    BUSINESS_DATA = "业务问题-数据逻辑"
    BUSINESS_BOUNDARY = "业务问题-边界条件"
    BUSINESS_UI = "业务问题-用户交互"

    # 其他
    SYSTEMIC = "系统性问题"
    INTERMITTENT = "间歇性问题"


class AssertionResult:
    """断言结果类，包含细粒度问题分类信息"""

    def __init__(self,
                 success: bool = True,
                 issue_type: IssueCategory = None,
                 severity: IssueSeverity = IssueSeverity.MEDIUM,
                 message: str = "",
                 details: Dict = None):
        self.success = success
        self.issue_type = issue_type
        self.severity = severity
        self.message = message
        self.details = details or {}

    def __bool__(self):
        return self.success


class TestAssert:
    """断言封装类，实现细粒度问题分类"""

    def __init__(self, test_name: str, business_requirement: str = None):
        self.test_name = test_name
        self.business_requirement = business_requirement
        self.failures = []

    def contains_assert(self, value: str, response: Dict, status_code: int) -> AssertionResult:
        """字符串包含断言，添加细粒度分类"""
        # 检查状态码
        if 'status_code' in value:
            expected_status = value['status_code']
            if expected_status != status_code:
                error_type = IssueCategory.TECHNICAL_ENV
                severity = IssueSeverity.CRITICAL
                error_msg = f"状态码不匹配，预期: {expected_status}, 实际: {status_code}"
                self._record_failure(error_type, severity, error_msg,
                                     f"状态码断言失败: 预期{expected_status}≠实际{status_code}")
                return AssertionResult(success=False,
                                       issue_type=error_type,
                                       severity=severity,
                                       message=error_msg,
                                       details={"expected": expected_status, "actual": status_code})

        # 检查内容
        if 'content' in value:
            expected_content = value['content']
            if expected_content not in str(response):
                error_type = IssueCategory.BUSINESS_RULE
                severity = IssueSeverity.HIGH
                error_msg = f"内容包含断言失败，预期包含: '{expected_content}', 实际: '{response}'"
                self._record_failure(error_type, severity, error_msg,
                                     f"内容断言失败: 预期包含'{expected_content}'但实际为'{response}'")
                return AssertionResult(success=False,
                                       issue_type=error_type,
                                       severity=severity,
                                       message=error_msg,
                                       details={"expected": expected_content, "actual": response})

        return AssertionResult(success=True)

    def equal_assert(self, expected: Dict, response: Dict) -> AssertionResult:
        """相等断言，添加细粒度分类"""
        if expected != response:
            # 检查是否是业务数据问题
            if self._is_business_data_mismatch(expected, response):
                error_type = IssueCategory.BUSINESS_DATA
                severity = IssueSeverity.HIGH
            else:
                error_type = IssueCategory.TECHNICAL_LOGIC
                severity = IssueSeverity.MEDIUM

            error_msg = f"数据匹配断言失败，实际: {response}, 预期: {expected}"
            self._record_failure(error_type, severity, error_msg,
                                 f"数据匹配断言失败: 实际{response} ≠ 预期{expected}")
            return AssertionResult(success=False,
                                   issue_type=error_type,
                                   severity=severity,
                                   message=error_msg,
                                   details={"expected": expected, "actual": response})

        return AssertionResult(success=True)

    def _is_business_data_mismatch(self, expected: Dict, response: Dict) -> bool:
        """判断数据不匹配是否是业务问题"""
        # 业务问题特征：预期和实际数据都是合法业务数据，但逻辑不匹配
        # 技术问题特征：数据格式错误、类型不匹配等
        # 这里简单判断：如果预期和实际都是字典且有相同键，可能是业务问题
        if isinstance(expected, dict) and isinstance(response, dict):
            common_keys = set(expected.keys()) & set(response.keys())
            if common_keys:
                # 检查常见业务字段（如价格、状态等）
                business_fields = ['price', 'status', 'amount', 'quantity', 'user_id']
                return bool(common_keys & set(business_fields))
        return False

    def assert_mysql(self, expected_sql: str) -> AssertionResult:
        """数据库断言，添加细粒度分类"""
        try:
            conn = ConnectMysql()
            db_value = conn.query(expected_sql)
            if db_value is None:
                error_type = IssueCategory.TECHNICAL_DATA
                severity = IssueSeverity.HIGH
                error_msg = f"数据库查询返回空值，SQL: {expected_sql}"
                self._record_failure(error_type, severity, error_msg,
                                     f"数据库查询失败: SQL '{expected_sql}' 未返回预期结果")
                return AssertionResult(success=False,
                                       issue_type=error_type,
                                       severity=severity,
                                       message=error_msg,
                                       details={"sql": expected_sql})
            return AssertionResult(success=True)
        except Exception as e:
            error_type = IssueCategory.TECHNICAL_DEPENDENCY
            severity = IssueSeverity.CRITICAL
            error_msg = f"数据库连接异常: {str(e)}"
            self._record_failure(error_type, severity, error_msg,
                                 f"数据库异常: {str(e)}")
            return AssertionResult(success=False,
                                   issue_type=error_type,
                                   severity=severity,
                                   message=error_msg,
                                   details={"error": str(e), "sql": expected_sql})

    def _record_failure(self, issue_type: IssueCategory, severity: IssueSeverity,
                        message: str, attachment_title: str):
        """记录失败信息，添加到测试结果中"""
        self.failures.append({
            "issue_type": issue_type.value,
            "severity": severity.value,
            "message": message,
            "attachment_title": attachment_title
        })
        logs.error(f"[{issue_type.value} - {severity.value}] {message}")
        allure.attach(
            f"错误类型: {issue_type.value}\n"
            f"严重性: {severity.value}\n"
            f"错误信息: {message}\n"
            f"相关业务需求: {self.business_requirement or 'N/A'}\n"
            f"测试用例: {self.test_name}",
            attachment_title,
            allure.attachment_type.TEXT
        )

    def assert_result(self, expected: Dict, response: Dict, status_code: int):
        """执行断言并收集结果"""
        all_pass = True
        for assert_type, value in expected.items():
            if assert_type == 'contains':
                result = self.contains_assert(value, response, status_code)
            elif assert_type == 'eq':
                result = self.equal_assert(value, response)
            elif assert_type == 'db':
                result = self.assert_mysql(value)
            else:
                continue

            if not result.success:
                all_pass = False

        if all_pass:
            logs.info(f"测试用例 {self.test_name} 通过")
        else:
            logs.error(f"测试用例 {self.test_name} 失败")
            assert False, "测试失败"