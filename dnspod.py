#!/usr/bin/env python
# -*-coding:utf-8-*-

__version__ = '0.2'
__author__ = 'Mush (btyh17mxy@gmail.com)'

'''
Copyright (c) 2014 Mush Mo
All rights reserved.

file:       dnspod.py
summary:    提供DNSPod域名和记录的增删改查.

version:    0.2
authors:    Mush (btyh17mxy@gmail.com)

time:       2014-06-07
time:       2015-08-27
'''
import requests
import logging
import unittest
DEBUG_LEVEL = logging.DEBUG
try:
    import colorizing_stream_handler
    root = logging.getLogger()
    root.setLevel(DEBUG_LEVEL)
    root.addHandler(colorizing_stream_handler.ColorizingStreamHandler())
except Exception, e:
    root = logging.getLogger()
    root.setLevel(DEBUG_LEVEL)
    root.addHandler(logging.StreamHandler())


class DNSPodError(Exception):
    ''' 异常基类.
    '''
    pass


class LoginError(DNSPodError):
    ''' 登陆异常，在登陆失败时抛出.
    '''
    pass


class DomainError(DNSPodError):
    ''' 域名操作异常.
    '''
    pass


ERROR_CODE = {
    '-1': LoginError,
}

DOMAIN_TYPE = {
    'all': u'所有域名',
    'mine': u'我的域名',
    'share': u'共享给我的域名',
    'ismark': u'星标域名',
    'pause': u'暂停域名',
    'vip': u'VIP域名',
    'recent': u'最近操作过的域名',
    'share_out': u'我共享出去的域名',
}


class DNSPodBase(object):
    ''' API基类.
    '''

    def __init__(self, token_id, token, cookie='', **kwargs):
        '''初始化.
        设置url和基本参数及请求头.
        '''
        self.base_url = 'https://dnsapi.cn/'
        self.payload = {
            'login_token': "%s,%s" % (token_id, token),
            'format': "json",
        }
        self.headers = {
            'User-Agent': 'DNSPodDemo/0.1(btyh17mxy@gmail.com)',
            "Accept": "text/json",
            'Cookies': cookie,
        }

    def request(self, url, **kwargs):
        '''发起请求.
        '''
        data = self.payload
        data.update(kwargs)

        r = requests.post(url, data=data, headers=self.headers)

        try:
            response = r.json()
        except Exception, e:
            logging.error(e)
            raise DNSPodError(e)

        code = response[u'status']['code']
        message = response[u'status']['message']

        if code == u'1':
            logging.info(message)
            response.pop(u'status')
            logging.info(response)
            return response

        logging.error(message)
        if code in ERROR_CODE:
            raise ERROR_CODE[code](message)

        raise DNSPodError(message)


class Domain(DNSPodBase):
    '''
    提供域名操作.
    '''
    def __init__(self, token_id, token, cookie='', **kwargs):
        super(Domain, self).__init__(token_id, token, cookie, **kwargs)
        self.base_url = self.base_url+'Domain'

    def create(self, domain, group_id='', is_mark=False):
        '''
        增加域名.

        Args:
            domain 域名, 没有 www, 如 dnspod.com
            group_id 域名分组ID，可选参数
            is_mark {yes|no} 是否星标域名，可选参数

        Raise:
            6 域名无效
            7 域名已存在
            11 域名已经存在并且是其它域名的别名
            12 域名已经存在并且您没有权限管理
            41 网站内容不符合DNSPod解析服务条款，域名添加失败
        '''
        url = self.base_url + '.Create'
        data = locals().copy()
        data.pop('self')

        return self.request(**data)

    def remove(self, domain=None, domain_id=None):
        '''
        删除域名

        Args:
            domain_id 或 domain，分别对应域名ID和域名，提交其中一个即可

        Raises:
            -15 域名已被封禁
            6 域名ID错误
            7 域名已锁定
            8 VIP域名不可以删除
            9 非域名所有者
        '''
        if not domain_id and not domain:
            logging.error(u'必须指定一个domain_id或domain, 二者不能都为空')
            raise DNSPodError(u'必须指定一个domain_id或domain, 二者不能都为空')

        url = self.base_url + '.Remove'

        data = locals().copy()
        data.pop('self')

        return self.request(**data)

    def list(self, type='all', offset=0, length=3000, group_id=None):
        '''
        获取域名列表.

        Args:
            type 域名权限种类，可选参数，默认为’all’。包含以下类型：
                all：所有域名
                mine：我的域名
                share：共享给我的域名
                ismark：星标域名
                pause：暂停域名
                vip：VIP域名
                recent：最近操作过的域名
                share_out：我共享出去的域名
            offset 记录开始的偏移，第一条记录为 0，依次类推，可选参数
            length 共要获取的记录的数量，比如获取20条，则为20，可选参数
            group_id 分组ID，获取指定分组的域名，可选参数

        Raises:
            6 记录开始的偏移无效
            7 共要获取的记录的数量无效
            9 没有任何域名
        '''
        if type not in DOMAIN_TYPE.keys():
            logging.error(
                u'域名类型错误，可选类型为all,mine,share,ismark,pause,vip,recent,share_out'
            )
            raise DNSPodError('域名类型错误')

        url = self.base_url + '.List'

        data = locals().copy()
        data.pop('self')

        return self.request(**data)

    def status(self,  status, domain=None, domain_id=None):
        '''设置域名状态.

        Args:
            domain_id 或 domain，分别对应域名ID和域名，提交其中一个即可
            status {enable, disable} 域名状态

        Raises:
            -15 域名已被封禁
            -7 企业账号的域名需要升级才能设置
            -8 代理名下用户的域名需要升级才能设置
            6 域名ID错误
            7 域名被锁定
            8 非域名所有者
        '''
        if not domain_id and not domain:
            logging.error(u'必须指定一个domain_id或domain, 二者不能都为空')
            raise DNSPodError(u'必须指定一个domain_id或domain, 二者不能都为空')
        if status not in ('enable', 'disable'):
            logging.error(u'域名状态必须为enable 或 disable')
            raise DNSPodError(u'域名状态必须为enable 或 disable')

        url = self.base_url + '.Status'

        data = locals().copy()
        data.pop('self')

        return self.request(**data)

    def info(self, domain=None, domain_id=None):
        '''获取域名信息

        Args:
            domain_id 或 domain，分别对应域名ID和域名，提交其中一个即可

        Raises:
            -7 企业账号的域名需要升级才能设置
            -8 代理名下用户的域名需要升级才能设置
            6 域名ID错误
            8 非域名所有者
        '''
        if not domain_id and not domain:
            logging.error(u'必须指定一个domain_id或domain, 二者不能都为空')
            raise DNSPodError(u'必须指定一个domain_id或domain, 二者不能都为空')

        url = self.base_url + '.Info'

        data = locals().copy()
        data.pop('self')

        return self.request(**data)

    def domain_id_by_domain(self, domain):
        return self.info(domain=domain)['domain']['id']

    def lockstatus(self, domain=None, domain_id=None):
        '''获取域名锁定状态

        Args:
            domain_id 或 domain，分别对应域名ID和域名，提交其中一个即可

        Raises:
            -15 域名已被封禁
            -7 企业账号的域名需要升级才能设置
            -8 代理名下用户的域名需要升级才能设置
            6 域名ID错误
            7 域名没有锁定
        '''
        if not domain_id and not domain:
            logging.error(u'必须指定一个domain_id或domain, 二者不能都为空')
            raise DNSPodError(u'必须指定一个domain_id或domain, 二者不能都为空')

        url = self.base_url + '.Lockstatus'

        data = locals().copy()
        data.pop('self')

        return self.request(**data)


class Record(DNSPodBase):
    '''记录操作.
    '''

    def __init__(self, token_id, token, cookie='', **kwargs):
        super(Record, self).__init__(token_id, token, cookie, **kwargs)
        self.base_url = self.base_url+'Record'

    def create(
            self,
            domain_id,
            value,
            record_line,
            record_type=u'默认',
            mx=None,
            ttl=600,
            sub_domain=u'@'
    ):
        '''添加记录.

        Args:
            domain_id 域名ID, 必选
            sub_domain 主机记录, 如 www, 默认@，可选
            record_type 记录类型，通过API记录类型获得，大写英文，比如：A, 必选
            record_line 记录线路，通过API记录线路获得，中文，比如：默认, 必选
            value 记录值, 必选.
            mx {1-20} MX优先级, 当记录类型是 MX 时有效，范围1-20, MX记录必选
            ttl {1-604800} TTL，范围1-604800，不同等级域名最小值不同, 可选

        Raises:
            -15 域名已被封禁
            -7 企业账号的域名需要升级才能设置
            -8 代理名下用户的域名需要升级才能设置
            6 缺少参数或者参数错误
            7 不是域名所有者或者没有权限
            21 域名被锁定
            22 子域名不合法
            23 子域名级数超出限制
            24 泛解析子域名错误
            25 轮循记录数量超出限制
            26 记录线路错误
            27 记录类型错误
            30 MX 值错误，1-20
            31 存在冲突的记录(A记录、CNAME记录、URL记录不能共存)
            32 记录的TTL值超出了限制
            33 AAAA 记录数超出限制
            34 记录值非法
            36 @主机的NS纪录只能添加默认线路
            82 不能添加黑名单中的IP
        '''

        ttl = int(ttl)
        if mx and mx not in range(1, 21):
            logging.error(u'mx out of range')
            raise DNSPodError(u'mx out of range')
        if ttl not in range(1, 604801):
            logging.error(u'ttl out of range')
            raise DNSPodError(u'ttl out of range')
        if record_type == 'MX' and not mx:
            logging.error(u'MX记录必须指定mx优先级')
            raise DNSPodError(u'MX记录必须指定mx优先级')

        url = self.base_url + '.Create'

        data = locals().copy()
        data.pop('self')
        return self.request(**data)

    def modify(self, domain_id, record_id, record_type, value,
               record_line="默认", sub_domain='@', mx=1, ttl=600):
        '''修改记录
        Args:
            domain_id 域名ID，必选
            record_id 记录ID，必选
            sub_domain 主机记录，默认@，如 www，可选
            record_type 记录类型，通过API记录类型获得，大写英文，比如：A，必选
            record_line 记录线路，通过API记录线路获得，中文，比如：默认，必选
            value 记录值,必选
            mx {1-20} MX优先级, 当记录类型是 MX 时有效，范围1-20, mx记录必选
            ttl {1-604800} TTL，范围1-604800，不同等级域名最小值不同，可选

        Raises:
            -15 域名已被封禁
            -7 企业账号的域名需要升级才能设置
            -8 代理名下用户的域名需要升级才能设置
            6 域名ID错误
            7 不是域名所有者或没有权限
            8 记录ID错误
            21 域名被锁定
            22 子域名不合法
            23 子域名级数超出限制
            24 泛解析子域名错误
            25 轮循记录数量超出限制
            26 记录线路错误
            27 记录类型错误
            29 TTL 值太小
            30 MX 值错误，1-20
            31 URL记录数超出限制
            32 NS 记录数超出限制
            33 AAAA 记录数超出限制
            34 记录值非法
            35 添加的IP不允许
            36 @主机的NS纪录只能添加默认线路
            82 不能添加黑名单中的IP
        '''
        if mx not in range(1, 21):
            logging.error(u'mx out of range')
            raise DNSPodError(u'mx out of range')
        if ttl not in range(1, 604801):
            logging.error(u'ttl out of range')
            raise DNSPodError(u'ttl out of range')
        if record_type == 'MX' and not mx:
            logging.error(u'MX记录必须指定mx优先级')
            raise DNSPodError(u'MX记录必须指定mx优先级')

        url = self.base_url + '.Modify'

        data = locals().copy()
        data.pop('self')

        return self.request(**data)

    def list(self, domain_id, offset=0, length=None, sub_domain=None):
        '''记录列表.

        Args:
            domain_id 域名ID，必选
            offset 记录开始的偏移，第一条记录为 0，依次类推，可选
            length 共要获取的记录的数量，比如获取20条，则为20，可选
            sub_domain 子域名，如果指定则只返回此子域名的记录，可选

        Raises:
            -7 企业账号的域名需要升级才能设置
            -8 代理名下用户的域名需要升级才能设置
            6 域名ID错误
            7 记录开始的偏移无效
            8 共要获取的记录的数量无效
            9 不是域名所有者
            10 没有记录
        '''
        url = self.base_url + '.List'

        data = locals().copy()
        data.pop('self')

        return self.request(**data)

    def remove(self, domain_id, record_id):
        '''删除记录.

        Args:
            domain_id 域名ID，必选
            record_id 记录ID，必选

        Raises:
            -15 域名已被封禁
            -7 企业账号的域名需要升级才能设置
            -8 代理名下用户的域名需要升级才能设置
            6 域名ID错误
            7 不是域名所有者或没有权限
            8 记录ID错误
            21 域名被锁定
        '''
        url = self.base_url + '.Remove'

        data = locals().copy()
        data.pop('self')

        return self.request(**data)

    def dDNS(self, domain_id, record_id, sub_domain, record_line, value=None):
        '''更新动态DNS记录.

        Args:
            domain_id 域名ID，必选
            record_id 记录ID，必选
            sub_domain 主机记录，如 www
            record_line 记录线路，通过API记录线路获得，中文，比如：默认，必选
            value IP地址，例如：6.6.6.6，可选

        Raises:
            -15 域名已被封禁
            -7 企业账号的域名需要升级才能设置
            -8 代理名下用户的域名需要升级才能设置
            6 域名ID错误
            7 不是域名所有者或没有权限
            8 记录ID错误
            21 域名被锁定
            22 子域名不合法
            23 子域名级数超出限制，比如免费套餐域名不支持三级域名
            24 泛解析子域名错误，比如免费套餐载名不支持 a*
            25 轮循记录数量超出限制，比如免费套餐域名只能存在两条轮循记录
            26 记录线路错误，比如免费套餐域名不支持移动、国外
        '''
        url = self.base_url + '.Ddns'

        data = locals().copy()
        data.pop('self')

        return self.request(**data)

    def remark(self, domain_id, record_id, remark):
        '''设置记录备注.

        Args:
            domain_id 域名ID，必选
            record_id 记录ID，必选
            remark 域名备注，删除备注请提交空内容，必选

        Raises:
            6 域名ID错误
            8 记录 ID 错误
        '''
        url = self.base_url + '.Remark'

        data = locals().copy()
        data.pop('self')

        return self.request(**data)

    def info(self, domain_id, record_id):
        '''获取记录信息.

        Args:
            domain_id 域名ID，必选
            record_id 记录ID，必选

        Raises:
            -15 域名已被封禁
            -7 企业账号的域名需要升级才能设置
            -8 代理名下用户的域名需要升级才能设置
            6 域名ID错误
            7 不是域名所有者或没有权限
            8 记录ID错误
        '''
        url = self.base_url + '.Info'

        data = locals().copy()
        data.pop('self')

        return self.request(**data)

    def get_record_id(self, domain_id, record_name, record_type="A"):
        record = [
            item for item in self.list(domain_id)['records']
            if item["name"] == record_name and item['type'] == record_type
        ]
        if not record:
            return None
        else:
            return record[0]['id']

    def status(self, domain_id, record_id, status):
        '''设置记录状态.

        Args:
            domain_id 域名ID，必选
            record_id 记录ID，必选
            status {enable|disable} 新的状态，必选

        Raises:
            -15 域名已被封禁
            -7 企业账号的域名需要升级才能设置
            -8 代理名下用户的域名需要升级才能设置
            6 域名ID错误
            7 不是域名所有者或没有权限
            8 记录ID错误
            21 域名被锁定
        '''
        if status not in ('enable', 'disable'):
            logging.error(u'记录状态必须为enable 或 disable')
            raise DNSPodError(u'记录状态必须为enable 或 disable')

        url = self.base_url + '.Status'

        data = locals().copy()
        data.pop('self')

        return self.request(**data)


class DomainTest(unittest.TestCase):
    # ID：10655
    # Token：e229e078d113eccd8bf0b33ef10123e5
    def setUp(self):
        self.domain = Domain('10655', 'e229e078d113eccd8bf0b33ef10123e5')
        try:
            self.domain.create('btyh17mxy.com')
        except Exception, e:
            logging.error(e)

    def tearDown(self):
        try:
            self.domain.remove(domain='btyh17mxy.com')
        except Exception, e:
            logging.error(e)

    def testCreate(self):
        self.domain.create('btyh17mxytest.com')
        self.domain.remove('btyh17mxytest.com')
        print self.domain.list()
        self.domain.status('disable', 'btyh17mxy.com')
        self.domain.info('btyh17mxy.com')


if __name__ == '__main__':
    pass
