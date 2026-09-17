import os
import xlrd
from conf import setting
from xlutils.copy import copy
from common.recordlog import logs
import xlwt


# Excel 数据所在 sheet 的索引（0 表示第 1 个 sheet）。
# 读取和写回共用这一个索引，避免两边指向不同的 sheet。
# 原代码读取时用的是 obj.sheets()[1]，这里保持为 1 不变。
XLS_SHEET_INDEX = 1


class HandleExcel:
    """读取excel测试数据文件"""
    def __init__(self,file_path=None):
        if file_path is not None:
            self.file_path = file_path
        else:
            self.file_path = setting.FILE_PATH['EXCEL']
        self.__global_table=self.xls_obj()

    def xls_obj(self):
        """获取Excel文件的对象,后续都通过这个对象去操作Excel中的数据"""
        if os.path.splitext(self.file_path)[-1] != '.xlsx':  # 获取文件后缀名
            obj = xlrd.open_workbook(self.file_path, formatting_info=True)
            xls_obj = obj.sheets()[XLS_SHEET_INDEX]
            return xls_obj
        else:
            logs.error('Excel文件格式必须是.xls格式')
            return None

    def get_rows(self):
        """
        获取xls文件总行数
        @return:
        """
        return self.__global_table.nrows

    def get_cols(self):
        """
        获取总列数
        :return:
        """
        return self.__global_table.ncols

    def get_cell_value(self, row, col):
        """
        获取单元格的值
        :param row: excel行数，索引从0开始，第一行索引是0
        :param col: Excel列数，索引从0开始，第一列索引是0
        :return:
        """
        return self.__global_table.cell_value(row, col)

    def settingStyle(self):
        """
        设置样式,该功能暂时未生效
        :return:
        """
        # xlwt 没有 easyfont() 这个 API，设置样式用的是 easyxf()。
        # 该样式目前既不返回也不参与写入，所以本方法仍处于"未生效"状态；
        # 如需真正生效：return style，并在写入时 sheet.write(row, col, value, style)
        style = xlwt.easyxf("font: bold on, color red")  # 粗体,红色

    def write_xls_value(self, row, col, value):
        """
        写入数据
        :param row: excel行数
        :param col: Excel列数
        :param value: 写入的值
        :return:
        """
        try:
            init_table = xlrd.open_workbook(self.file_path, formatting_info=True)
            copy_table = copy(init_table)
            # get_sheet 的参数是 sheet 索引或名称，原来传的是文件路径，必然抛异常；
            # 与 xls_obj() 读取的 sheet 保持同一个索引
            sheet = copy_table.get_sheet(XLS_SHEET_INDEX)
            sheet.write(row, col, value)
            copy_table.save(self.file_path)
        except PermissionError:
            logs.error("请先关闭xls文件")
            exit()

    def get_each_line(self, row):
        """
        获取每一行数据
        :param row: excel行数
        :return: 返回一整行的数据
        """
        try:
            return self.__global_table.row_values(row)
        except Exception as exp:
            logs.error(exp)

    def get_each_column(self,col=None):
        """
        获取每一列数据
        :param col: Excel列数
        :return: 返回一整列的数据 list格式
        """
        if col is None:
            # 原为 self.col：本类没有 col 属性，一旦走这个分支必然 AttributeError；
            # 未指定列时默认取第 0 列
            return self.__global_table.col_values(0)
        else:
            return self.__global_table.col_values(col)


