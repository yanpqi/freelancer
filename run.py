#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys,os

# 定义星系膨胀系统
#SYSTEM_SCALE_X = 1.566
#SYSTEM_SCALE_Y = 1.566
SYSTEM_SCALE_X = 3.6
SYSTEM_SCALE_Y = 3.6

# 定义地图原点在方格坐标系统中的位置
ORIGIN_POINT_X = 4
ORIGIN_POINT_Y = 4

# 定义方格内导航坐标区块数
INNER_SECTION_X = 2
INNER_SECTION_Y = 2

class Sys_Database:
    def __init__(self):
        self.sys_info = {}
        self.init_coordinate()
        self.no_show = ['Trade_Lane_Ring',
                        'wplatform',
                        'hazard_buoy',
                        'small_wplatform',
                        'wplatform_mineable',
                        'space_tankl4',
                        'space_tanklx4',
                        'Trade_Lane_Ring_Damage_B',
                        'Trade_Lane_Ring_Damage_A',
                        'invisible_base',
                        'wplatform_ice',
                        'depot_Hfuel',
                        'gas_miner_nodock',
                        'wplatform_special'
                        ]
    def init_coordinate(self, scale=None):
        scale_x = SYSTEM_SCALE_X if not scale else scale
        scale_y = SYSTEM_SCALE_Y if not scale else scale
        print('use scale %f' %scale_x)
        self.ORIGIN_TRANS_X = 40000 * scale_x
        self.ORIGIN_TRANS_Y = 40000 * scale_y

        self.PER_SCALE_X = self.ORIGIN_TRANS_X / ORIGIN_POINT_X
        self.PER_SCALE_Y = self.ORIGIN_TRANS_Y / ORIGIN_POINT_Y

        self.PER_SCALE_XI = self.PER_SCALE_X / INNER_SECTION_X
        self.PER_SCALE_YI = self.PER_SCALE_Y / INNER_SECTION_Y

    def load_baese(self, file_name):
        with open(file_name) as f:
            lines = f.readlines()
            for l in lines:
                parts = l.split('=')
                code = parts[0].strip().lower()
                if code not in self.sys_info.keys():
                    self.sys_info[code] = {'sys_name':'', 'bases':[], 'holes': [], 'scale': SYSTEM_SCALE_X}
                self.sys_info[code]['sys_name'] = parts[1].strip()

    def set_scale(self, file_name):
        f = Db_Connector(file_name)
        objects = f.query('system')
        for o in objects:
          if o.has_key('nickname') and o.has_key('NavMapScale'):
              nickname = o['nickname']
              scale = o['NavMapScale']
              info = self.query(nickname)
              if info:
                  info['scale'] = float(scale)

    def do_work(self):
        for uni_sys in self.sys_info.keys():
            self.load_base(uni_sys)

    def query(self, name):
        name = name.lower()
        if name in self.sys_info.keys():
            return self.sys_info[name]
        return None

    def query_sys_name(self, name):
        name = name.lower()
        if name in self.sys_info.keys():
            return self.sys_info[name]['sys_name']
        return None


    def load_base(self, uni_sys):
        print('loading universe system %s map' %uni_sys)
        #有几个星系配置文件命名不规范，需要单独处理
        no_regular = {
            'BW03': 'Bw03',
            'IW01': 'Iw01',
            'FP7' : 'fp7_system',
        }

        file_name = "SYSTEMS/" + uni_sys.upper() + "/" + uni_sys + ".ini"
        if not os.path.exists(file_name):
            file_name = "SYSTEMS/" + uni_sys.upper() + "/" + uni_sys.upper() + ".ini"
        if not os.path.exists(file_name) and uni_sys.upper() in no_regular:
            file_name = "SYSTEMS/" + uni_sys.upper() + "/" + no_regular[uni_sys.upper()] + ".ini"
        if not os.path.exists(file_name):
            print('can not load universe system %s map file %s' %(uni_sys, file_name))
            return

        f = Db_Connector(file_name)
        objects = f.query('Object')
        if not objects:
            print('%s has no objects you wanted', uni_sys)
            return
        info = self.query(uni_sys)
        bases = info['bases']
        holes = info['holes']
        scale = info['scale']
        self.init_coordinate(scale)

        for o in objects:
          if o.has_key('nickname'):
              nickname = o['nickname']
              #print(nickname + ' pos is '+ o['pos'])
              arch_type = ''
              if o.has_key('archetype'):
                  arch_type = o['archetype']
                  if arch_type.find('dmg') > 0 or arch_type.find('hull') > 0 or arch_type in self.no_show:
                      continue
              if nickname.find('_to_') > 0:
                  parts = nickname.split('_to_')
                  nickname = parts[1][:4]
                  #print('add system ' + nickname)
                  nickname = self.query_sys_name(nickname)
                  if nickname:
                      holes.append({'name': nickname, 'pos': self.compute_position(o['pos'], scale), 'origin': self.origin_position(o['pos']), 'arch': arch_type})
              else:
                  bases.append({'name': nickname, 'pos': self.compute_position(o['pos'], scale), 'origin': self.origin_position(o['pos']), 'arch': arch_type})

    def origin_position(self, position):
        position = position.split(',')
        ret = '(%d, %d)' %(int(float(position[0].strip())), int(float(position[2].strip())))
        return ret
    def compute_position(self, position, scale):
        position = position.split(',')
        trans_y = float(position[2].strip()) + self.ORIGIN_TRANS_X
        trans_x = float(position[0].strip()) + self.ORIGIN_TRANS_Y
        outter_y = int(trans_y / self.PER_SCALE_X)
        outter_x = int(trans_x / self.PER_SCALE_Y)
        inner_y = (int(trans_y) % int(self.PER_SCALE_X)) / self.PER_SCALE_XI + 1
        inner_x = (int(trans_x) % int(self.PER_SCALE_Y)) / self.PER_SCALE_YI + 1
        y = 1 + int(trans_y)
        x = ord('A') + int(trans_x)
        ret = '%d%s (%.1f, %.1f)' %(1 + outter_y, chr(ord('A') + outter_x), inner_y, inner_x)
        return ret

    def bases(self, name):
        uni_sys = self.query(name)
        if not uni_sys:
            print('%s system not exists')
        return uni_sys['bases']

    def holes(self, name):
        uni_sys = self.query(name)
        if not uni_sys:
            print('%s system not exists')
        return uni_sys['holes']

    def output(self, file_name):
        content = ''
        sys_list = sorted(self.sys_info.keys())
        for uni_sys in sys_list:
            sys_info = self.sys_info[uni_sys]
            uni_sys_info = '\n[%s %s %f]\n' %(uni_sys,str(sys_info['sys_name']), sys_info['scale'])
            uni_sys_info += '<跳跃>\n'
            if len(sys_info['holes']) <= 0:
                uni_sys_info += '0\n'
            for b in sys_info['holes']:
                uni_sys_info += '%s: %s %s %s \n' %(b['name'], b['pos'], b['origin'], b['arch'])
            uni_sys_info += '<基地>\n'
            if len(sys_info['bases']) <= 0:
                uni_sys_info += '0\n'
            for b in sys_info['bases']:
                uni_sys_info += '%s: %s %s %s \n' %(b['name'], b['pos'], b['origin'], b['arch'])
            content += uni_sys_info
        with open(file_name, 'w') as f:
            f.write(content)
  
class Db_Connector:
  def __init__(self, config_file_path):
      self.sec_list = {}
      with open(config_file_path, 'r') as f:
          lines = f.readlines()
          for line in lines:
              line = line.strip()
              if len(line) <= 1:
                  continue
              #print('%s has %d chars' %(line, len(line)))
              if line[0] == '[' and line[-1] == ']':
                  select = line[1:-1]
                  sel_obj = {}
                  if select in self.sec_list:
                      self.sec_list[select].append(sel_obj)
                  else:
                      self.sec_list[select] = []
                      self.sec_list[select].append(sel_obj)
              else:
                  #print(line)
                  if line[0] == ';':
                      continue
                  kv_line = line.split('=')
                  if len(kv_line) < 2:
                      sel_obj[kv_line[0].strip()] = ''
                  else:
                      sel_obj[kv_line[0].strip()] = kv_line[1].strip()
  def sections(self):
      return self.sec_list.keys()

  def query(self, section):
      if section in self.sec_list.keys():
          return self.sec_list[section]
      return None

if __name__ == "__main__":
  db = Sys_Database()
  db.load_baese('GAMEDATA_systems.txt')
  db.set_scale('universe.ini')
  db.do_work()
  db.output('output.txt')
