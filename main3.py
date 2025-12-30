import time

def decrate(func):
    def wrapper(*args, **kwargs):
        print('--------func start--------')
        t1 = time.time()
        res = func(*args, **kwargs)
        process_time = time.time() - t1
        print(f'------------func end ,time is {process_time}-----------')
        return res
    return wrapper

@decrate
def main():
    x = 6
    print(x**4)

if __name__ == '__main__':
    main()