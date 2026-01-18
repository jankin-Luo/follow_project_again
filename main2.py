#大概过一下怎么写的
import time

import requests


class AsyncInterfaceTester:
    def __init__(self):
        pass

    def lunxun(self,lx_url,task_id,interval,max_attempts,success_status):
        attemp = 0
        while attemp < max_attempts:
            try:
                res = post(lx_url,task_id)
                if res.status_code == 200:
                    js = res.json()
                    status = self.extract_status(js)
                    if status in success_status:
                        return True
                    elif status in fail_status:
                        return False
                    else:
                        #任务未完成
                        attemp += 1
                        time.sleep(interval)
                        logs.info('任务还在进行,稍后继续查询')
                else:
                    #接口返回信息非200
                    attemp += 1
                    time.sleep(interval)
                    logs.info('连接不畅')
            #连接报错
            except Exception as e:
                logs.error('轮询异常了')
                attemp += 1
                time.sleep(interval)

        logs.info('轮询超时了')
        return {'超时信息'}