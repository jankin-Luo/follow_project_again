import time
import requests
import json
import jsonpath
from common.recordlog import logs
from common.readyaml import ReadYamlData
from common.debugtalk import DebugTalk
from conf.OperationConfig import OperationConfig
from common.sendrequests import SendRequests
import allure
from common.assertions import Assertions

#封装了异步接口的测试类
#这个类里面编写了多个方法：执行异步接口任务的方法、查询结果接口的轮询方法、替换yaml函数方法（用了正则表达式）、提取方法、提取task_id方法

class AsyncInterfaceTester:
    """
    异步接口测试器 - 使用轮询机制实现异步接口测试
    不需要使用asyncio和aiohttp，通过简单的轮询等待实现异步接口测试
    """

    def __init__(self):
        self.send = SendRequests()
        self.debug_talk = DebugTalk()

    def poll_async_task(self, task_check_url, task_id, check_method='GET',
                        check_headers=None, check_params=None,
                        max_attempts=30, interval=2, success_status=['SUCCESS', 'COMPLETED']):
        """
        轮询异步任务状态

        Args:
            task_check_url: 检查任务状态的API URL
            task_id: 任务ID
            check_method: 检查任务状态的HTTP方法，默认GET
            check_headers: 检查任务状态的请求头
            check_params: 检查任务状态的请求参数
            max_attempts: 最大轮询次数
            interval: 轮询间隔（秒）
            success_status: 成功状态列表

        Returns:
            dict: 任务最终状态和结果
        """
        attempts = 0
        task_params = {'task_id': task_id} if check_params is None else check_params
        if 'task_id' not in task_params:
            task_params['task_id'] = task_id

        logs.info(f"开始轮询异步任务，任务ID: {task_id}")
        allure.attach(f"任务ID: {task_id}", "异步任务ID", allure.attachment_type.TEXT)

        while attempts < max_attempts:
            try:
                # 发送状态检查请求
                response = self.send.send_request(
                    method=check_method,
                    url=task_check_url,
                    headers=check_headers,
                    params=task_params
                )

                if response.status_code == 200:
                    result = response.json()
                    current_status = self._extract_task_status(result)

                    logs.info(f"轮询第 {attempts + 1} 次，当前任务状态: {current_status}")
                    allure.attach(f"轮询第 {attempts + 1} 次，状态: {current_status}",
                                  f"异步任务状态检查", allure.attachment_type.TEXT)

                    # 检查任务是否完成
                    if current_status in success_status:
                        logs.info(f"异步任务已完成，状态: {current_status}")
                        allure.attach(f"任务完成，状态: {current_status}",
                                      "异步任务完成", allure.attachment_type.TEXT)
                        return {
                            'status': 'completed',
                            'result': result,
                            'task_id': task_id,
                            'final_status': current_status
                        }
                    elif current_status in ['FAILED', 'ERROR', 'FAILURE']:
                        logs.warning(f"异步任务失败，状态: {current_status}")
                        return {
                            'status': 'failed',
                            'result': result,
                            'task_id': task_id,
                            'final_status': current_status
                        }
                    else:
                        # 任务仍在进行中，继续轮询
                        logs.info(f"任务仍在进行中，等待 {interval} 秒后继续轮询...")
                        time.sleep(interval)
                        attempts += 1
                else:
                    logs.warning(f"检查任务状态失败，状态码: {response.status_code}")
                    attempts += 1
                    time.sleep(interval)

            except Exception as e:
                logs.error(f"轮询过程中发生异常: {str(e)}")
                attempts += 1
                time.sleep(interval)

        # 达到最大尝试次数仍未完成
        logs.warning(f"达到最大轮询次数({max_attempts})，任务可能仍在执行中")
        return {
            'status': 'timeout',
            'result': None,
            'task_id': task_id,
            'final_status': 'TIMEOUT'
        }

    def _extract_task_status(self, response_data):
        """
        从响应数据中提取任务状态
        默认查找常见的状态字段
        """
        # 常见的状态字段名
        status_fields = ['status', 'state', 'task_status', 'process_status', 'job_status']

        for field in status_fields:
            try:
                status = jsonpath.jsonpath(response_data, f'$.{field}')
                if status:
                    return status[0]
            except:
                continue

        # 如果没找到标准字段，尝试查找所有包含status的字段
        if isinstance(response_data, dict):
            for key, value in response_data.items():
                if 'status' in key.lower():
                    return value

        # 默认返回UNKNOWN
        return 'UNKNOWN'

    def execute_async_interface_test(self, baseinfo, testcase, async_config):
        """
        执行异步接口测试

        Args:
            baseinfo: 基础接口信息
            testcase: 测试用例信息
            async_config: 异步配置信息
                - trigger_url: 触发异步任务的URL（可选，如果与baseinfo.url不同）
                - check_url: 检查任务状态的URL
                - task_id_path: 从触发响应中提取任务ID的JSONPath
                - max_attempts: 最大轮询次数
                - interval: 轮询间隔
                - success_status: 成功状态列表
        """
        try:
            # 1. 触发异步任务
            logs.info("开始执行异步接口测试 - 触发异步任务")

            # 准备请求参数
            cookies = None
            params_type = ['params', 'data', 'json']

            base_url = OperationConfig().get_env('host')
            trigger_url = base_url + async_config.get('trigger_url', baseinfo['url'])

            # 处理动态参数
            header = baseinfo['header'].copy()
            if 'cookies' in baseinfo:
                cookies = self._replace_dynamic_vars(baseinfo['cookies'])

            tc = testcase.copy()
            case_name = tc.pop('case_name')
            validation = tc.pop('validation', [])
            extract = tc.pop('extract', None)
            extract_list = tc.pop('extract_list', None)

            for k, v in tc.items():
                if k in params_type:
                    tc[k] = self._replace_dynamic_vars(v)

            # 发送异步任务触发请求
            trigger_response = self.send.run_main(
                name=baseinfo['api_name'],
                case_name=case_name + "_async_trigger",
                url=trigger_url,
                headers=header,
                method=baseinfo['method'],
                cookies=cookies,
                **tc
            )

            allure.attach(trigger_response.text, "异步任务触发响应", allure.attachment_type.TEXT)

            # 2. 提取任务ID
            task_id = self._extract_task_id(trigger_response.json(), async_config['task_id_path'])
            if not task_id:
                raise ValueError(f"无法从响应中提取任务ID，JSONPath: {async_config['task_id_path']}")

            logs.info(f"成功提取任务ID: {task_id}")
            allure.attach(f"任务ID: {task_id}", "提取的任务ID", allure.attachment_type.TEXT)

            # 3. 轮询等待任务完成
            check_url = base_url + async_config['check_url']
            check_headers = header  # 可以使用不同的请求头

            poll_result = self.poll_async_task(
                task_check_url=check_url,
                task_id=task_id,
                check_method=async_config.get('check_method', 'GET'),
                check_headers=check_headers,
                max_attempts=async_config.get('max_attempts', 30),
                interval=async_config.get('interval', 2),
                success_status=async_config.get('success_status', ['SUCCESS', 'COMPLETED'])
            )

            # 4. 处理轮询结果
            if poll_result['status'] == 'completed':
                final_result = poll_result['result']
                allure.attach(json.dumps(final_result, ensure_ascii=False, indent=2),
                              "异步任务最终结果", allure.attachment_type.JSON)

                # 执行验证
                self._perform_validation(validation, final_result, 200)

                # 执行数据提取，**************好像没用****************
                if extract:
                    self._extract_data(extract, json.dumps(final_result, ensure_ascii=False))
                if extract_list:
                    self._extract_data_list(extract_list, json.dumps(final_result, ensure_ascii=False))

                return poll_result

            elif poll_result['status'] == 'failed':
                logs.error(f"异步任务执行失败: {poll_result['result']}")
                allure.attach(f"任务失败: {poll_result['result']}", "异步任务失败", allure.attachment_type.TEXT)
                raise Exception(f"异步任务执行失败: {poll_result['result']}")

            else:  # timeout
                logs.warning(f"异步任务超时，可能仍在执行中")
                allure.attach("任务超时，可能仍在执行中", "异步任务超时", allure.attachment_type.TEXT)
                raise Exception(f"异步任务超时，任务ID: {task_id}")

        except Exception as e:
            logs.error(f"异步接口测试执行失败: {str(e)}")
            raise e

    def _replace_dynamic_vars(self, data):
        """替换动态变量（简化版）"""
        # 这里使用您现有的BaseRequest类中的逻辑
        str_data = data
        if not isinstance(data, str):
            str_data = json.dumps(data, ensure_ascii=False)

        # 查找${}格式的动态变量并替换
        import re
        pattern = r'\$\{([^}]+)\}'
        matches = re.findall(pattern, str_data)

        for match in matches:
            try:
                # 分离函数名和参数
                if '(' in match and ')' in match:
                    func_part = match.split('(')[0]
                    args_part = match.split('(')[1].rstrip(')')
                    args = [arg.strip() for arg in args_part.split(',')] if args_part else []

                    # 调用DebugTalk中的方法
                    func = getattr(self.debug_talk, func_part)
                    result = func(*args) if args else func()

                    # 替换原始字符串
                    original = f"${{{match}}}"
                    str_data = str_data.replace(original, str(result))
            except Exception as e:
                logs.warning(f"替换动态变量失败: {match}, 错误: {e}")

        # 根据原数据类型返回
        if isinstance(data, dict):
            try:
                return json.loads(str_data)
            except:
                return eval(str_data)
        else:
            return str_data

    def _extract_task_id(self, response_data, task_id_path):
        """从响应中提取任务ID"""
        try:
            task_ids = jsonpath.jsonpath(response_data, task_id_path)
            if task_ids:
                return task_ids[0]
            else:
                logs.error(f"无法通过JSONPath '{task_id_path}' 提取任务ID")
                return None
        except Exception as e:
            logs.error(f"提取任务ID时发生错误: {e}")
            return None

    def _perform_validation(self, validation_rules, response_data, status_code):
        """执行验证规则"""
        assert_res = Assertions()
        assert_res.assert_result(validation_rules, response_data, status_code)

    def _extract_data(self, extract_rules, response_text):
        """提取数据到YAML文件"""
        read_yaml = ReadYamlData()
        for k, v in extract_rules.items():
            if '$' in v:
                try:
                    extracted_value = jsonpath.jsonpath(json.loads(response_text), v)[0]
                    extract_data = {k: extracted_value}
                    read_yaml.write_yaml_data(extract_data)
                    logs.info(f'json提取到的{extract_data}')
                except Exception as e:
                    logs.error(f'提取数据失败: {e}')

    def _extract_data_list(self, extract_rules, response_text):
        """提取数据列表到YAML文件"""
        read_yaml = ReadYamlData()
        for k, v in extract_rules.items():
            if '$' in v:
                try:
                    extracted_values = jsonpath.jsonpath(json.loads(response_text), v)
                    extract_data = {k: extracted_values}
                    read_yaml.write_yaml_data(extract_data)
                    logs.info(f'json列表提取到的{extract_data}')
                except Exception as e:
                    logs.error(f'提取数据列表失败: {e}')


# 扩展BaseRequest类以支持异步接口测试
class ExtendedBaseRequest(BaseRequest):
    def __init__(self):
        super().__init__()
        self.async_tester = AsyncInterfaceTester()

    def specification_yaml_async(self, baseinfo, testcase, async_config):
        """
        规范化异步接口测试
        """
        return self.async_tester.execute_async_interface_test(baseinfo, testcase, async_config)


# 示例：如何在测试中使用
def example_usage():
    """
    示例：如何在测试用例中使用异步接口测试
    """
    # 模拟测试数据
    baseinfo = {
        'api_name': '异步下单接口',
        'url': '/api/order/async/create',
        'method': 'post',
        'header': {'Content-Type': 'application/json'},
        'cookies': '${get_extract_data(Cookie)}'
    }

    testcase = {
        'case_name': '异步下单测试',
        'json': {
            'orderInfo': {'name': 'test_order'},
            'async': True
        },
        'validation': [
            {'contains': {'status': 'SUCCESS'}}
        ]
    }

    async_config = {
        'trigger_url': '/api/order/async/create',  # 触发异步任务的URL
        'check_url': '/api/order/async/status',  # 查询状态的URL
        'task_id_path': '$.taskId',  # 从触发响应中提取任务ID的路径
        'max_attempts': 30,  # 最大轮询次数
        'interval': 2,  # 轮询间隔(秒)
        'success_status': ['SUCCESS', 'COMPLETED', 'FINISHED']  # 成功状态列表
    }

    # 创建扩展的请求处理器
    extended_req = ExtendedBaseRequest()

    # 执行异步接口测试
    try:
        result = extended_req.specification_yaml_async(baseinfo, testcase, async_config)
        print(f"异步测试完成: {result}")
    except Exception as e:
        print(f"异步测试失败: {e}")


if __name__ == "__main__":
    example_usage()



