from conf.setting import FILE_PATH
import configparser


class OperationConfig():

    def __init__(self, file_path=None):
        if file_path is None:
            self.__file_path = FILE_PATH['conf']
        else:
            self.__file_path = file_path

        self.conf = configparser.ConfigParser()
        try:
            self.conf.read(self.__file_path, encoding='utf-8')
        except Exception as e:
            print(e)

    def get_section_for_data(self, section, option):
        '''
        读取ini文件
        :param section:
        :param option:
        :return:
        '''
        try:
            data = self.conf.get(section, option)
            return data
        except Exception as e:
            print(e)

    def get_env(self, option):
        '''获取环境地址函数 '''
        return self.get_section_for_data('api_env', option)

    def get_mysql(self, option):
        '''获取环境地址函数 '''
        return self.get_section_for_data('MYSQL', option)


if __name__ == '__main__':
    oper = OperationConfig()
    print(oper.get_mysql( 'host'))
