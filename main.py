# class MyClass:
#     def __init__(self, name):
#         self.name = name
#         print(f"创建对象: {self.name}")
#
#     def __del__(self):
#         print(f"销毁对象: {self.name}")
#
# if __name__=='__main__':
#     myclass = MyClass('你好')

def except_behavior():
    try:
        print("1. try 块开始")
        print("这行不会执行")
        # raise ValueError('这里错误')
        result = 10 / 0  # 这里会抛出 ZeroDivisionError

    except ZeroDivisionError as e:
        print(f"2. 捕获到异常: {e}")
        # 程序会继续执行，不会中断
        raise e

    print("3. except 块之后，程序继续执行")


except_behavior()
print("4. 函数调用后，程序继续执行")