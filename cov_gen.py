import sys
from typing import TextIO

from sv_cov import *
import xlrd

class FCOV:     #covergroup
    def __init__(self, sheets):
        self.sheets = sheets
        self.cp_line_state = 0
        self.cg_cp_info = []
        self.cov_struct_s = []
    def print_sheet(self):
        for sheet in self.sheets:
            self.cov_struct_s.append('covergroup '+ sheet.name +';')
            self.cov_struct_s.append('\t//  put options here if required')
            cp_info = [sheet.name, 0]
            print("row=%d" % sheet.nrows)
            for row in range(sheet.nrows):
                print(sheet.cell(row,0).value)
                if(sheet.cell(row,0).value == '#'):  #注释行
                    continue
                elif(sheet.cell(row,0).value == '^'): #标题行
                    self.parse_col_num(sheet, row)
                    self.cp_line_state = 1          # 标记下一行是要参数行
                elif (sheet.cell(row, 0).value == '$'):  # 结束标志
                    print("end covergroup")
                    self.cp_line_state = 0
                    self.cp.gen_it()
                    self.cov_struct_s.extend(self.cp.cov_struct_s)
                    print("end covergroup")
                elif(self.cp_line_state >0):        #
                    label = sheet.cell(row,self.label_col_num).value
                    #print("label = %s" %label)
                    if (('cp_' in label)or('cc_' in label)):   #cp-covergroup cc-cross
                        if(self.cp_line_state == 2 or self.cp_line_state == 3):
                            self.cp.gen_it()
                            #print(self.cp.cov_struct_s)
                            self.cov_struct_s.extend(self.cp.cov_struct_s)
                            print(self.cp)
                        self.cp_line_state = 2  #开始记录cp参数
                        cp_info[1] +=1
                        # finished consecutive structure
			            # process old structure
                        # print("target_col_num =%d" %self.target_col_num)
                        this_target = sheet.cell(row,self.target_col_num).value
                        this_iff = sheet.cell(row,self.iff_col_num).value
                        this_prefixs = sheet.cell(row,self.prefixs_col_num).value
                        # new a coverage structure
			            # print("new cov struct -"+label)
                        if('cp_' in label):
                            #label就是cp_name ,this_target
                            self.cp = COVERPOINT(label, this_target, this_iff, this_prefixs)
                        else:
                            print("instance cross")
                            self.cp = CROSS(label, this_target)

                    else:
                        if (self.cp_line_state == 2):
                            self.cp_line_state = 3

                        bin_type = sheet.cell(row, self.bin_type_col_num).value
                        bin_name = sheet.cell(row, self.bin_name_col_num).value
                        bin_name = sheet.cell(row, self.bin_name_col_num).value.rstrip(' ')
                        bin_val = self.de_float(sheet.cell(row, self.bin_val_col_num).value)
                        #print("bin_val=%s" % bin_val)
                        # Handle the decoding of ' character. To deal with strings like 2'b10, 32'hffff
                        # bin_val = bin_val.replace(u'\u2019', u'\'').encode('ascii', 'ignore')
                        print(bin_name)
                        if ('M_' in bin_name):
                            this_bin = PREDEF_BIN(bin_name, this_target, int(bin_val))
                            self.cp.add_predef_bins(this_bin)
                        elif (bin_name != ''):
                            print(bin_name)
                            if (bin_type == ''):
                                this_bin = COV_BIN(bin_name, bin_val)
                            else:
                                print(bin_name)
                                this_bin = COV_BIN(bin_name, bin_val, bin_type)
                            self.cp.add_bins(this_bin)

                        # add options to cp
                        # Options is independently to bins
                        if (self.cp_line_state == 2 or self.cp_line_state == 3):
                            option_exp = self.de_float(sheet.cell(row, self.cp_option_exp_col_num).value)
                        if (sheet.cell(row, self.cp_option_col_num).value != ''):
                            self.cp.add_options(sheet.cell(row, self.cp_option_col_num).value, option_exp)



            self.cg_cp_info.append(cp_info)
            self.cov_struct_s.append('endgroup\n')

    def de_float(self,in_val):
        if(isinstance(in_val, float)):  #判断in_val是不是float类型
            out = str(int(in_val))
        else:
            out = in_val 
        return out
  
    def parse_col_num(self, sheet, row):
        for col in range(1,sheet.ncols):
            if(sheet.cell(row,col).value=="LABEL"):
                self.label_col_num = col
            elif(sheet.cell(row,col).value=="TARGET"):
                self.target_col_num = col
            elif(sheet.cell(row,col).value=="IFF"):
                self.iff_col_num = col
            elif(sheet.cell(row,col).value=="BIN_TYPE"):
                self.bin_type_col_num = col
            elif(sheet.cell(row,col).value=="BIN_NAME"):
                self.bin_name_col_num = col
            elif(sheet.cell(row,col).value=="BIN_VAL"):
                self.bin_val_col_num = col
            elif(sheet.cell(row,col).value=="PREFIXS"):
                self.prefixs_col_num = col
            elif(sheet.cell(row,col).value=="OPTION"):
                self.cp_option_col_num = col
            elif(sheet.cell(row,col).value=="OPTION_EXP"):
                self.cp_option_exp_col_num = col
          

    def __str__(self):   ##魔术方法，当print输出该对象是就会执行定义的__str__
        s = 'Total summary => \n'
        for cg in self.cg_cp_info:
            s = s + "covergroup %12s, %4d coverpoints" %(cg[0], cg[1]) + '\n'  
        return s

if __name__ == "__main__":
    filename =r'FCOV_TEMPLATE.xlsx'
    #try:
    table = xlrd.open_workbook(filename)
    #except:
    #    print("File %s does not exist" % filename)
    #    exit()

    sheets = table.sheets()
    fcov = FCOV(sheets)
    fcov.print_sheet()
    print("打印covergroup：")
    print(fcov.cov_struct_s)

    ##产生sv文件
    filename_sp = filename.split(".xlsx")
    sv_filename = filename_sp[0]+".sv"
    #print(sv_filename)
    with  open(sv_filename,'w') as sv_f:
        for cov_struct in fcov.cov_struct_s:
            #print(cov_struct)
            sv_f.write(cov_struct+'\n')
            #sv_f.wirte('\r\n')

        sv_f.close()

    sys.stderr.write('%s'% fcov)
