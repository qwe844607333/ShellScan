#!/usr/bin/env python
# coding=utf-8 
import os  
import pdb 
from lib.common import check_shell

class Backdoor_Analysis:
    def __init__(self):
        pass 

    def check_cron(self): 
        command = ['wget','curl','base64']
        risk = 0
        try:
            cron_dir_list = ['/var/spool/cron/', '/etc/cron.d/', '/etc/cron.daily/', '/etc/cron.weekly/','/etc/cron.hourly/', '/etc/cron.monthly/']
            for cron_dir in cron_dir_list:
                for file in os.listdir(cron_dir):
                    path = cron_dir + file 
                    f = open(path)
                    for line in f.readlines():
                        result = check_shell(line)
                        if result:
                            risk = 1
                            print('  [1]定时任务检测    [ 存在风险 ]')
                            print('  检测到定时任务文件: {} 中存在反弹SHELL: {}，请进一步确认'.format(path,result.strip()))
                        else:
                            for i in command:
                                if i in line:
                                    risk = 1
                                    print('  [1]定时任务检测    [ 存在风险 ]')
                                    print '  检测到定时任务文件: {} 中存在敏感命令: {}, 请进一步确认'.format(path,i)
                                    break  
            if not risk:
                print('  [1]定时任务检测   [ OK ] ')



        except Exception,e:
            print e  

    def check_SSHwrapper(self):
        sshd = ['/sbin/sshd','/usr/sbin/sshd']
        try:
            for i in sshd:
                infos = os.popen("file {} 2>/dev/null".format(i)).read().splitlines()
                if ('ELF' not in infos[0]) and ('executable' not in infos[0]):
                    print('  [2]SSH Wrapper后门检测    [ 存在风险 ]')
                    print('  {} 被篡改,文件非可执行文件'.format(i)) 
                else:
                    print('  [2]SSH Wrapper后门检测    [ OK ]')
        except Exception,e:
            print(e) 

    def check_setuid(self):
        try:
            file_infos = os.popen("find / ! -path '/proc/*' -type f -perm -4000 2>/dev/null | grep -vE 'pam_timestamp_check|unix_chkpwd|ping|mount|su|pt_chown|ssh-keysign|at|passwd|chsh|crontab|chfn|usernetctl|staprun|newgrp|chage|dhcp|helper|pkexec|top|Xorg|nvidia-modprobe|quota|login|security_authtrampoline|authopen|traceroute6|traceroute|ps'").read().splitlines()
            if file_infos:
                print('  [3]suid权限检测    [ 存在风险 ]')
                for info in file_infos:
                    print('文件{}设置了suid属性，请确认是否为后门文件'.format(info))
            else:
                print('  [3]suid权限检测    [ OK ]')
        except Excpetion,e:
            print(e) 

    def check_sshkey(self):
        white_list = ['ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAmEXGvVqupmK8X45RTQqGee2LTNKc1Qv+gpCxdGv8AMKMtBihxbDumllCBmlvQdeTyVqaebnZD9SrgWzSKqKtCCgDHVtok3pUMGKrTiXaOnvm26vu+WVC7e50MXryBXkcwEFT2Mxi607R2jdjqgaf6yihUXHX+HluIJv3yunzOez3sq/ogGEJMtn1lWGY57e0vTv34tikClllDq2w0W885mubKOYpVKGfBFCxyxpyshgxatVdqcKj75hpeFzQgEissKG7Q++eyb72qPDJY3RTltSZhFCh1gLF0THofkF+UR0Zbmeb1q7nSV0A9JIUxpuucfytGdKczpqyE3EQrVehsw==','ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAtqjF//kd2rdvFaQfDkaoYfefwp9NMxG4ANV68nV/YF4iNrUrp9Y+uzZje6KECvIV21QNgt2d4Isk29tFnWrBmu7ZBBDgALnw6oA7cvp9goie1HW59DCgdoLvv+2rPoKY+6oLieLL/ZjpMof0MA3nCGkCESHb/qdvTnf6ozEdVdkvTREdNc4MPdaoqhcTxo5F9+mb2r5nMk2oIRAtIWZXZbmRqIXySdDPLfGNF0sxWxGdeMfmJlsvG1/Zx8GzOlpYKGFzkCvdrqEd3C4yccGNUG1+0jkxE+XUDLfXsHrf7N7dvlMZuFDuay5BXL5KSxecvNhM9FZ2E6pNKFDkrTtfJw==','ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC9h01bENBKgDQSZd4VxHcDqHSzoosOGp/+MHiQX9bclXDFAOGR/t+VcTr+uDlZMBmXBSpVUpeKN0VI0/PBXtZowwZp9RZ/xZc5Hc+5oz9FsWpVWRmm0a2A/VzvC4k14xYnbjHn+2r/OhAh2Ou3IV6fnJSuDYg3Xzu4CZQxrOfgGyFD/mRx4EI25aBmCBMjr+EEckxHOoPCYjP0VZSnmUvIxT1Aft3sLTJ/xAS0pVK4meKG5P5M+SYKvGwytehaMhiyhNMBhxpmZ/83gg3D61s6STflA5HzSFDU+qs34/oMEfOIEEVGbTUfOYHtg2kOSK0OdYebKEIgbyv0K50rcayX']
        try:
            if os.path.exists('/root/.ssh/authorized_keys'):
                with open('/root/.ssh/authorized_keys') as f:
                    for line in f:
                        l = line.split()[0] + ' ' + line.split()[1]
                        if l in white_list:
                            continue
                        else:
                            print('  [4]SSH公钥检测    [ 存在风险 ]')
                            print('  请确认以下公钥是否合法:')
                            print('  {}'.format(line))
            else:
                print('  [4]SSH公钥检测    [ OK ]')
                return 0  
        except:
            print('SSH公钥检测错误')
            pass




    def run(self):
        print('\n常见后门检测开始')
        self.check_cron()
        self.check_SSHwrapper()
        self.check_setuid()
        self.check_sshkey()
