#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import base64
import json
import sys
import os
from urllib.parse import quote, urlencode
from typing import List, Dict, Any
import tkinter as tk
from tkinter import ttk, messagebox, font
import pyperclip
import re
from urllib.parse import unquote, urlparse, parse_qs

class ClashToV2ray:
    """Clash 配置转换为 v2rayN 链接的转换器"""

    def __init__(self, input_file: str):
        """
        初始化转换器

        Args:
            input_file (str): Clash 配置文件路径
        """
        self.input_file = input_file
        self.proxies = []
        # 调用 load_yaml 方法加载 YAML 文件
        self.load_yaml()

    def load_yaml(self):
        """加载 YAML 文件并解析内容"""
        with open(self.input_file, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            self.proxies = config.get('proxies', [])

    def generate_vless_link(self, proxy: Dict[str, Any]) -> str:
        """
        生成 VLESS 节点链接

        Args:
            proxy (Dict[str, Any]): 节点配置信息

        Returns:
            str: VLESS 节点链接
        """
        # 基础参数
        server = proxy['server']
        port = str(proxy['port'])
        uuid = proxy['uuid']
        name = quote(proxy.get('name', 'Unknown'))
        
        # 构建参数字典
        params = {}

        # 添加加密方式（VLESS 默认为 none）
        params["encryption"] = "none"

        # 处理流控制（flow）
        flow = proxy.get('flow', '')
        if flow:
            params["flow"] = flow

        # 处理传输协议
        network = proxy.get('network', 'tcp')
        params["type"] = network

        # 处理 TCP 特定设置
        if network == 'tcp':
            params["headerType"] = "none"

        # 处理 TLS 相关设置
        if proxy.get('tls', False):
            # 检查是否有 Reality 配置
            reality_opts = proxy.get('reality-opts', {})

            if reality_opts:
                # Reality 加密
                params["security"] = "reality"

                # 添加 public-key
                public_key = reality_opts.get('public-key', '')
                if public_key:
                    params["pbk"] = public_key

                # 添加 short-id
                short_id = reality_opts.get('short-id', '')
                if short_id:
                    params["sid"] = short_id
            else:
                # 普通 TLS 加密
                params["security"] = "tls"

            # 添加 SNI 设置（servername）
            servername = proxy.get('servername', '')
            if servername:
                params["sni"] = servername

            # 添加客户端指纹（fingerprint）
            fingerprint = proxy.get('client-fingerprint', '')
            if fingerprint:
                params["fp"] = fingerprint

        # 处理 WebSocket 相关设置
        if network == 'ws':
            # 处理 ws-opts
            ws_opts = proxy.get('ws-opts', {})

            # 处理路径
            path = ws_opts.get('path', '')
            if path:
                params["path"] = path

            # 处理主机头
            headers = ws_opts.get('headers', {})
            host = headers.get('Host', '')
            if host:
                params["host"] = host

        # 构建基础URL
        base_url = f"vless://{uuid}@{server}:{port}"

        # 添加查询参数
        query_string = urlencode({k: v for k, v in params.items() if v})

        # 添加节点名称
        return f"{base_url}?{query_string}#{name}"

    def generate_vmess_link(self, proxy: Dict[str, Any]) -> str:
        """
        生成 VMess 节点链接

        Args:
            proxy (Dict[str, Any]): 节点配置信息

        Returns:
            str: VMess 节点链接
        """
        # 构建基本配置
        vmess_config = {
            "v": "2",
            "ps": proxy.get('name', 'Unknown'),
            "add": proxy['server'],
            "port": str(proxy['port']),
            "id": proxy['uuid'],
            "aid": str(proxy.get('alterId', 0)),
            "net": proxy.get('network', 'tcp'),
            "type": "vmess",  # 设置类型为 vmess
            "tls": "tls" if proxy.get('tls', False) else ""
        }

        # 处理加密方式
        cipher = proxy.get('cipher', 'auto')
        vmess_config["scy"] = cipher

        # 处理 WebSocket 配置
        if proxy.get('network') == 'ws':
            # 从 ws-opts 获取路径和主机头
            ws_opts = proxy.get('ws-opts', {})

            # 设置路径
            path = ws_opts.get('path', '')
            vmess_config["path"] = path

            # 设置主机头
            headers = ws_opts.get('headers', {})
            host = headers.get('Host', '')
            vmess_config["host"] = host

        # 处理 SNI
        sni = proxy.get('servername', '')
        if sni:
            vmess_config["sni"] = sni
        elif host:
            # 如果没有设置 servername，但有 Host 头，用它作为 SNI
            vmess_config["sni"] = host

        # 处理指纹和 ALPN
        vmess_config["fp"] = proxy.get('client-fingerprint', '')
        vmess_config["alpn"] = proxy.get('alpn', '')

        # 转换为 JSON 并编码
        json_str = json.dumps(vmess_config)
        return f"vmess://{base64.b64encode(json_str.encode()).decode()}"
        
    def generate_ss_link(self, proxy: Dict[str, Any]) -> str:
        """
        生成 Shadowsocks 节点链接

        Args:
            proxy (Dict[str, Any]): 节点配置信息

        Returns:
            str: Shadowsocks 节点链接
        """
        method = proxy['cipher']
        password = proxy['password']
        server = proxy['server']
        port = proxy['port']
        name = quote(proxy.get('name', 'Unknown'))
        
        ss_config = f"{method}:{password}@{server}:{port}"
        base64_str = base64.b64encode(ss_config.encode()).decode()
        return f"ss://{base64_str}#{name}"
        
    def generate_trojan_link(self, proxy: Dict[str, Any]) -> str:
        """
        生成 Trojan 节点链接

        Args:
            proxy (Dict[str, Any]): 节点配置信息

        Returns:
            str: Trojan 节点链接
        """
        # 基础参数
        password = proxy['password']
        server = proxy['server']
        port = proxy['port']
        name = quote(proxy.get('name', 'Unknown'))

        # 构建参数字典
        params = {}

        # Trojan 默认使用 TLS
        params["security"] = "tls"

        # 处理 SNI
        sni = proxy.get('sni', '')
        if sni:
            params["sni"] = sni

        # 处理证书验证
        if proxy.get('skip-cert-verify', False):
            params["allowInsecure"] = "1"

        # 处理传输协议
        network = proxy.get('network', 'tcp')
        params["type"] = network

        # 处理 WebSocket 相关设置
        if network == 'ws':
            # 处理 ws-opts
            ws_opts = proxy.get('ws-opts', {})

            # 处理路径
            path = ws_opts.get('path', '')
            if path:
                params["path"] = path

            # 处理主机头
            headers = ws_opts.get('headers', {})
            host = headers.get('Host', '')
            if host:
                params["host"] = host
        elif network == 'tcp':
            # TCP 特定设置
            params["headerType"] = "none"

        # 构建基础URL
        base_url = f"trojan://{password}@{server}:{port}"

        # 添加查询参数
        query_string = urlencode({k: v for k, v in params.items() if v})

        # 添加节点名称
        return f"{base_url}?{query_string}#{name}"

    def generate_hysteria2_link(self, proxy: Dict[str, Any]) -> str:
        """
        生成 Hysteria2 节点链接

        Args:
            proxy (Dict[str, Any]): 节点配置信息

        Returns:
            str: Hysteria2 节点链接
        """
        # 必需参数
        server = proxy['server']
        port = str(proxy['port'])  # 使用 port 而不是 ports

        # 密码可能存在于 password 或 auth 字段中
        password = proxy.get('password', proxy.get('auth', ''))

        # 节点名称
        name = quote(proxy.get('name', 'Unknown'))

        # 构建参数
        params = {}

        # 添加 SNI，如果没有设置，默认使用服务器地址
        params["sni"] = proxy.get("sni", server)

        # 添加 ALPN 参数
        params["alpn"] = "h3,h2"

        # 处理证书验证
        if proxy.get("skip-cert-verify", False):
            params["insecure"] = "1"

        # 添加可选的上传下载速度参数
        up_mbps = proxy.get("up_mbps", "")
        down_mbps = proxy.get("down_mbps", "")
        if up_mbps:
            params["up"] = str(up_mbps)
        if down_mbps:
            params["down"] = str(down_mbps)

        # 构建基础URL
        base_url = f"hysteria2://{password}@{server}:{port}"

        # 构建查询字符串并添加节点名称
        query_string = urlencode(params)
        return f"{base_url}?{query_string}#{name}"
        
    def convert(self) -> List[str]:
        """
        转换所有节点配置为 v2rayN 可用的链接

        Returns:
            List[str]: 转换后的节点链接列表
        """
        links = []
        for proxy in self.proxies:
            try:
                if proxy['type'] == 'vmess':
                    links.append(self.generate_vmess_link(proxy))
                elif proxy['type'] == 'ss':
                    links.append(self.generate_ss_link(proxy))
                elif proxy['type'] == 'trojan':
                    links.append(self.generate_trojan_link(proxy))
                elif proxy['type'] == 'hysteria2':
                    links.append(self.generate_hysteria2_link(proxy))
                elif proxy['type'] == 'vless':
                    links.append(self.generate_vless_link(proxy))
            except KeyError as e:
                print(f"警告: 节点 {proxy.get('name', 'Unknown')} 缺少必要配置项: {str(e)}")
                continue
            except Exception as e:
                print(f"警告: 处理节点 {proxy.get('name', 'Unknown')} 时出错: {str(e)}")
                continue
                
        return links

class V2rayToClash:
    """V2rayN 链接转换为 Clash 配置的转换器"""
    
    def __init__(self):
        self.proxies = []
    
    def parse_vmess_link(self, link: str) -> Dict[str, Any]:
        """解析VMess链接"""
        try:
            # 移除 vmess:// 前缀
            base64_str = link.replace('vmess://', '')
            
            # Base64解码
            json_str = base64.b64decode(base64_str).decode('utf-8')
            config = json.loads(json_str)
            
            # 转换为Clash格式
            proxy = {
                'name': config.get('ps', 'VMess节点'),
                'type': 'vmess',
                'server': config.get('add', ''),
                'port': int(config.get('port', 443)),
                'uuid': config.get('id', ''),
                'alterId': int(config.get('aid', 0)),
                'cipher': config.get('scy', 'auto'),
                'network': config.get('net', 'tcp'),
                'tls': bool(config.get('tls'))
            }
            
            # 处理WebSocket配置
            if proxy['network'] == 'ws':
                ws_opts = {}
                if config.get('path'):
                    ws_opts['path'] = config.get('path')
                if config.get('host'):
                    ws_opts['headers'] = {'Host': config.get('host')}
                if ws_opts:
                    proxy['ws-opts'] = ws_opts
            
            # 处理TLS相关配置
            if proxy['tls']:
                if config.get('sni'):
                    proxy['servername'] = config.get('sni')
                if config.get('fp'):
                    proxy['client-fingerprint'] = config.get('fp')
                if config.get('alpn'):
                    proxy['alpn'] = config.get('alpn').split(',')
            
            return proxy
            
        except Exception as e:
            print(f"解析VMess链接失败: {str(e)}")
            return None
    
    def parse_vless_link(self, link: str) -> Dict[str, Any]:
        """解析VLESS链接"""
        try:
            # 解析URL
            parsed = urlparse(link)
            
            # 基础配置
            proxy = {
                'name': unquote(parsed.fragment) if parsed.fragment else 'VLESS节点',
                'type': 'vless',
                'server': parsed.hostname,
                'port': parsed.port or 443,
                'uuid': parsed.username
            }
            
            # 解析查询参数
            params = parse_qs(parsed.query)
            
            # 处理加密方式
            if 'encryption' in params:
                proxy['encryption'] = params['encryption'][0]
            
            # 处理流控制
            if 'flow' in params:
                proxy['flow'] = params['flow'][0]
            
            # 处理传输协议
            if 'type' in params:
                proxy['network'] = params['type'][0]
            
            # 处理TLS/Reality
            if 'security' in params:
                security = params['security'][0]
                if security == 'tls':
                    proxy['tls'] = True
                elif security == 'reality':
                    proxy['tls'] = True
                    reality_opts = {}
                    if 'pbk' in params:
                        reality_opts['public-key'] = params['pbk'][0]
                    if 'sid' in params:
                        reality_opts['short-id'] = params['sid'][0]
                    if reality_opts:
                        proxy['reality-opts'] = reality_opts
            
            # 处理SNI
            if 'sni' in params:
                proxy['servername'] = params['sni'][0]
            
            # 处理指纹
            if 'fp' in params:
                proxy['client-fingerprint'] = params['fp'][0]
            
            # 处理WebSocket配置
            if proxy.get('network') == 'ws':
                ws_opts = {}
                if 'path' in params:
                    ws_opts['path'] = params['path'][0]
                if 'host' in params:
                    ws_opts['headers'] = {'Host': params['host'][0]}
                if ws_opts:
                    proxy['ws-opts'] = ws_opts
            
            return proxy
            
        except Exception as e:
            print(f"解析VLESS链接失败: {str(e)}")
            return None
    
    def parse_ss_link(self, link: str) -> Dict[str, Any]:
        """解析Shadowsocks链接"""
        try:
            # 移除 ss:// 前缀
            content = link.replace('ss://', '')
            
            # 分离节点名称
            if '#' in content:
                content, name = content.split('#', 1)
                name = unquote(name)
            else:
                name = 'SS节点'
            
            # URL解码内容（处理%3D等编码）
            content = unquote(content)
            
            # 处理Base64编码的内容，添加填充
            def add_base64_padding(s):
                """为Base64字符串添加正确的填充"""
                missing_padding = len(s) % 4
                if missing_padding:
                    s += '=' * (4 - missing_padding)
                return s
            
            method = password = server = port = None
            
            # 尝试多种SS链接格式
            formats_tried = []
            
            # 格式1: ss://base64(method:password@server:port)#name
            try:
                formats_tried.append("格式1: 完整Base64编码")
                padded_content = add_base64_padding(content)
                decoded = base64.b64decode(padded_content).decode('utf-8')
                
                if '@' in decoded:
                    auth_part, server_part = decoded.split('@', 1)
                    if ':' in auth_part:
                        method, password = auth_part.split(':', 1)
                        if ':' in server_part:
                            server, port = server_part.rsplit(':', 1)
                        else:
                            raise ValueError("无效的server:port格式")
                    else:
                        raise ValueError("无效的method:password格式")
                else:
                    raise ValueError("缺少@符号")
                    
            except Exception as e1:
                # 格式2: ss://base64(method:password)@server:port#name
                try:
                    formats_tried.append("格式2: 部分Base64编码")
                    if '@' in content:
                        encoded_auth, server_part = content.split('@', 1)
                        # 移除可能的查询参数
                        if '?' in server_part:
                            server_part = server_part.split('?')[0]
                        
                        padded_auth = add_base64_padding(encoded_auth)
                        decoded_auth = base64.b64decode(padded_auth).decode('utf-8')
                        
                        if ':' in decoded_auth:
                            method, password = decoded_auth.split(':', 1)
                            if ':' in server_part:
                                server, port = server_part.rsplit(':', 1)
                            else:
                                raise ValueError("无效的server:port格式")
                        else:
                            raise ValueError("认证部分缺少冒号")
                    else:
                        raise ValueError("缺少@符号")
                        
                except Exception as e2:
                    # 格式3: ss://method:password@server:port#name (无Base64编码)
                    try:
                        formats_tried.append("格式3: 无Base64编码")
                        if '@' in content:
                            auth_part, server_part = content.split('@', 1)
                            if ':' in auth_part:
                                method, password = auth_part.split(':', 1)
                                if ':' in server_part:
                                    server, port = server_part.rsplit(':', 1)
                                else:
                                    raise ValueError("无效的server:port格式")
                            else:
                                raise ValueError("无效的method:password格式")
                        else:
                            raise ValueError("缺少@符号")
                            
                    except Exception as e3:
                        raise ValueError(f"所有格式都失败了: {formats_tried}")
            
            # 验证解析结果
            if not all([method, password, server, port]):
                raise ValueError(f"解析不完整: method={method}, password={bool(password)}, server={server}, port={port}")
            
            return {
                'name': name,
                'type': 'ss',
                'server': server,
                'port': int(port),
                'cipher': method,
                'password': password
            }
            
        except Exception as e:
            print(f"解析SS链接失败: {str(e)}")
            return None
    
    def parse_trojan_link(self, link: str) -> Dict[str, Any]:
        """解析Trojan链接"""
        try:
            # 解析URL
            parsed = urlparse(link)
            
            # 基础配置
            proxy = {
                'name': unquote(parsed.fragment) if parsed.fragment else 'Trojan节点',
                'type': 'trojan',
                'server': parsed.hostname,
                'port': parsed.port or 443,
                'password': parsed.username
            }
            
            # 解析查询参数
            params = parse_qs(parsed.query)
            
            # 处理SNI
            if 'sni' in params:
                proxy['sni'] = params['sni'][0]
            
            # 处理证书验证
            if 'allowInsecure' in params and params['allowInsecure'][0] == '1':
                proxy['skip-cert-verify'] = True
            
            # 处理传输协议
            if 'type' in params:
                proxy['network'] = params['type'][0]
            
            # 处理WebSocket配置
            if proxy.get('network') == 'ws':
                ws_opts = {}
                if 'path' in params:
                    ws_opts['path'] = params['path'][0]
                if 'host' in params:
                    ws_opts['headers'] = {'Host': params['host'][0]}
                if ws_opts:
                    proxy['ws-opts'] = ws_opts
            
            return proxy
            
        except Exception as e:
            print(f"解析Trojan链接失败: {str(e)}")
            return None
    
    def parse_hysteria2_link(self, link: str) -> Dict[str, Any]:
        """解析Hysteria2链接"""
        try:
            # 解析URL
            parsed = urlparse(link)
            
            # 基础配置
            proxy = {
                'name': unquote(parsed.fragment) if parsed.fragment else 'Hysteria2节点',
                'type': 'hysteria2',
                'server': parsed.hostname,
                'port': parsed.port or 443,
                'password': parsed.username
            }
            
            # 解析查询参数
            params = parse_qs(parsed.query)
            
            # 处理SNI
            if 'sni' in params:
                proxy['sni'] = params['sni'][0]
            
            # 处理证书验证
            if 'insecure' in params and params['insecure'][0] == '1':
                proxy['skip-cert-verify'] = True
            
            # 处理上传下载速度
            if 'up' in params:
                proxy['up_mbps'] = int(params['up'][0])
            if 'down' in params:
                proxy['down_mbps'] = int(params['down'][0])
            
            return proxy
            
        except Exception as e:
            print(f"解析Hysteria2链接失败: {str(e)}")
            return None
    
    def parse_links(self, links_text: str) -> List[Dict[str, Any]]:
        """解析多个节点链接"""
        links = []
        lines = links_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            try:
                if line.startswith('vmess://'):
                    proxy = self.parse_vmess_link(line)
                elif line.startswith('vless://'):
                    proxy = self.parse_vless_link(line)
                elif line.startswith('ss://'):
                    proxy = self.parse_ss_link(line)
                elif line.startswith('trojan://'):
                    proxy = self.parse_trojan_link(line)
                elif line.startswith('hysteria2://'):
                    proxy = self.parse_hysteria2_link(line)
                else:
                    print(f"不支持的协议类型: {line[:20]}...")
                    continue
                
                if proxy:
                    links.append(proxy)
                    
            except Exception as e:
                print(f"解析链接失败: {str(e)}")
                continue
        
        return links
    
    def convert_to_yaml(self, links_text: str) -> str:
        """将节点链接转换为Clash YAML配置"""
        proxies = self.parse_links(links_text)
        
        if not proxies:
            return ""
        
        # 构建基础Clash配置
        clash_config = {
            'port': 7890,
            'socks-port': 7891,
            'allow-lan': False,
            'mode': 'Rule',
            'log-level': 'info',
            'external-controller': '127.0.0.1:9090',
            'proxies': proxies,
            'proxy-groups': [
                {
                    'name': '🚀 节点选择',
                    'type': 'select',
                    'proxies': ['♻️ 自动选择', '🎯 全球直连'] + [proxy['name'] for proxy in proxies]
                },
                {
                    'name': '♻️ 自动选择',
                    'type': 'url-test',
                    'proxies': [proxy['name'] for proxy in proxies],
                    'url': 'http://www.gstatic.com/generate_204',
                    'interval': 300
                },
                {
                    'name': '🎯 全球直连',
                    'type': 'select',
                    'proxies': ['DIRECT']
                }
            ],
            'rules': [
                'DOMAIN-SUFFIX,local,DIRECT',
                'IP-CIDR,127.0.0.0/8,DIRECT',
                'IP-CIDR,172.16.0.0/12,DIRECT',
                'IP-CIDR,192.168.0.0/16,DIRECT',
                'IP-CIDR,10.0.0.0/8,DIRECT',
                'IP-CIDR,17.0.0.0/8,DIRECT',
                'IP-CIDR,100.64.0.0/10,DIRECT',
                'GEOIP,CN,DIRECT',
                'MATCH,🚀 节点选择'
            ]
        }
        
        return yaml.dump(clash_config, default_flow_style=False, allow_unicode=True, sort_keys=False)

class V2rayConfigGenerator:
    """生成 V2Ray config.json 配置文件的类"""
    
    def __init__(self):
        pass
    
    def generate_vmess_outbound(self, proxy: Dict[str, Any]) -> Dict[str, Any]:
        """生成VMess出站配置"""
        outbound = {
            "tag": proxy.get('name', 'vmess-out'),
            "protocol": "vmess",
            "settings": {
                "vnext": [
                    {
                        "address": proxy['server'],
                        "port": proxy['port'],
                        "users": [
                            {
                                "id": proxy['uuid'],
                                "alterId": proxy.get('alterId', 0),
                                "security": proxy.get('cipher', 'auto')
                            }
                        ]
                    }
                ]
            }
        }
        
        # 处理流配置
        stream_settings = {
            "network": proxy.get('network', 'tcp')
        }
        
        # 处理TLS
        if proxy.get('tls', False):
            stream_settings["security"] = "tls"
            tls_settings = {}
            if proxy.get('servername'):
                tls_settings["serverName"] = proxy['servername']
            if proxy.get('client-fingerprint'):
                tls_settings["fingerprint"] = proxy['client-fingerprint']
            if proxy.get('alpn'):
                tls_settings["alpn"] = proxy['alpn'] if isinstance(proxy['alpn'], list) else [proxy['alpn']]
            if tls_settings:
                stream_settings["tlsSettings"] = tls_settings
        
        # 处理WebSocket
        if proxy.get('network') == 'ws':
            ws_settings = {}
            ws_opts = proxy.get('ws-opts', {})
            if ws_opts.get('path'):
                ws_settings["path"] = ws_opts['path']
            if ws_opts.get('headers'):
                ws_settings["headers"] = ws_opts['headers']
            if ws_settings:
                stream_settings["wsSettings"] = ws_settings
        
        outbound["streamSettings"] = stream_settings
        return outbound
    
    def generate_vless_outbound(self, proxy: Dict[str, Any]) -> Dict[str, Any]:
        """生成VLESS出站配置"""
        outbound = {
            "tag": proxy.get('name', 'vless-out'),
            "protocol": "vless",
            "settings": {
                "vnext": [
                    {
                        "address": proxy['server'],
                        "port": proxy['port'],
                        "users": [
                            {
                                "id": proxy['uuid'],
                                "encryption": proxy.get('encryption', 'none')
                            }
                        ]
                    }
                ]
            }
        }
        
        # 处理流控制
        if proxy.get('flow'):
            outbound["settings"]["vnext"][0]["users"][0]["flow"] = proxy['flow']
        
        # 处理流配置
        stream_settings = {
            "network": proxy.get('network', 'tcp')
        }
        
        # 处理TLS/Reality
        if proxy.get('tls', False):
            reality_opts = proxy.get('reality-opts', {})
            if reality_opts:
                # Reality配置
                stream_settings["security"] = "reality"
                reality_settings = {}
                if reality_opts.get('public-key'):
                    reality_settings["publicKey"] = reality_opts['public-key']
                if reality_opts.get('short-id'):
                    reality_settings["shortId"] = reality_opts['short-id']
                if proxy.get('servername'):
                    reality_settings["serverName"] = proxy['servername']
                if proxy.get('client-fingerprint'):
                    reality_settings["fingerprint"] = proxy['client-fingerprint']
                stream_settings["realitySettings"] = reality_settings
            else:
                # 普通TLS
                stream_settings["security"] = "tls"
                tls_settings = {}
                if proxy.get('servername'):
                    tls_settings["serverName"] = proxy['servername']
                if proxy.get('client-fingerprint'):
                    tls_settings["fingerprint"] = proxy['client-fingerprint']
                if tls_settings:
                    stream_settings["tlsSettings"] = tls_settings
        
        # 处理WebSocket
        if proxy.get('network') == 'ws':
            ws_settings = {}
            ws_opts = proxy.get('ws-opts', {})
            if ws_opts.get('path'):
                ws_settings["path"] = ws_opts['path']
            if ws_opts.get('headers'):
                ws_settings["headers"] = ws_opts['headers']
            if ws_settings:
                stream_settings["wsSettings"] = ws_settings
        
        outbound["streamSettings"] = stream_settings
        return outbound
    
    def generate_shadowsocks_outbound(self, proxy: Dict[str, Any]) -> Dict[str, Any]:
        """生成Shadowsocks出站配置"""
        return {
            "tag": proxy.get('name', 'ss-out'),
            "protocol": "shadowsocks",
            "settings": {
                "servers": [
                    {
                        "address": proxy['server'],
                        "port": proxy['port'],
                        "method": proxy['cipher'],
                        "password": proxy['password']
                    }
                ]
            }
        }
    
    def generate_trojan_outbound(self, proxy: Dict[str, Any]) -> Dict[str, Any]:
        """生成Trojan出站配置"""
        outbound = {
            "tag": proxy.get('name', 'trojan-out'),
            "protocol": "trojan",
            "settings": {
                "servers": [
                    {
                        "address": proxy['server'],
                        "port": proxy['port'],
                        "password": proxy['password']
                    }
                ]
            }
        }
        
        # 处理流配置
        stream_settings = {
            "network": proxy.get('network', 'tcp'),
            "security": "tls"
        }
        
        # TLS设置
        tls_settings = {}
        if proxy.get('sni'):
            tls_settings["serverName"] = proxy['sni']
        if proxy.get('skip-cert-verify', False):
            tls_settings["allowInsecure"] = True
        if tls_settings:
            stream_settings["tlsSettings"] = tls_settings
        
        # 处理WebSocket
        if proxy.get('network') == 'ws':
            ws_settings = {}
            ws_opts = proxy.get('ws-opts', {})
            if ws_opts.get('path'):
                ws_settings["path"] = ws_opts['path']
            if ws_opts.get('headers'):
                ws_settings["headers"] = ws_opts['headers']
            if ws_settings:
                stream_settings["wsSettings"] = ws_settings
        
        outbound["streamSettings"] = stream_settings
        return outbound
    
    def convert_to_v2ray_config(self, input_content: str, input_type: str = "auto") -> str:
        """将输入内容转换为V2Ray config.json格式"""
        proxies = []
        
        # 根据输入类型解析节点
        if input_type == "auto":
            # 自动检测输入类型
            if input_content.strip().startswith(('vmess://', 'vless://', 'ss://', 'trojan://', 'hysteria2://')):
                # V2rayN链接格式
                converter = V2rayToClash()
                proxies = converter.parse_links(input_content)
            else:
                # 假设是Clash YAML格式
                try:
                    temp_file = 'temp_config.yaml'
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        f.write(input_content)
                    
                    converter = ClashToV2ray(temp_file)
                    converter.load_yaml()
                    proxies = converter.proxies
                    
                    os.remove(temp_file)
                except:
                    return ""
        
        if not proxies:
            return ""
        
        # 生成出站配置
        outbounds = []
        
        for proxy in proxies:
            try:
                if proxy['type'] == 'vmess':
                    outbounds.append(self.generate_vmess_outbound(proxy))
                elif proxy['type'] == 'vless':
                    outbounds.append(self.generate_vless_outbound(proxy))
                elif proxy['type'] == 'ss':
                    outbounds.append(self.generate_shadowsocks_outbound(proxy))
                elif proxy['type'] == 'trojan':
                    outbounds.append(self.generate_trojan_outbound(proxy))
                # 注意：Hysteria2 在标准V2Ray中不支持，跳过
            except Exception as e:
                print(f"生成出站配置失败 {proxy.get('name', 'Unknown')}: {str(e)}")
                continue
        
        # 添加直连和阻断出站
        outbounds.extend([
            {
                "tag": "direct",
                "protocol": "freedom",
                "settings": {}
            },
            {
                "tag": "blocked",
                "protocol": "blackhole",
                "settings": {
                    "response": {
                        "type": "http"
                    }
                }
            }
        ])
        
        # 生成完整的V2Ray配置
        v2ray_config = {
            "log": {
                "loglevel": "warning"
            },
            "inbounds": [
                {
                    "tag": "socks-in",
                    "port": 1080,
                    "listen": "127.0.0.1",
                    "protocol": "socks",
                    "sniffing": {
                        "enabled": True,
                        "destOverride": ["http", "tls"]
                    },
                    "settings": {
                        "auth": "noauth",
                        "udp": True
                    }
                },
                {
                    "tag": "http-in",
                    "port": 8080,
                    "listen": "127.0.0.1",
                    "protocol": "http",
                    "sniffing": {
                        "enabled": True,
                        "destOverride": ["http", "tls"]
                    },
                    "settings": {}
                }
            ],
            "outbounds": outbounds,
            "routing": {
                "rules": [
                    {
                        "type": "field",
                        "ip": [
                            "0.0.0.0/8",
                            "10.0.0.0/8",
                            "100.64.0.0/10",
                            "127.0.0.0/8",
                            "169.254.0.0/16",
                            "172.16.0.0/12",
                            "192.0.0.0/24",
                            "192.0.2.0/24",
                            "192.168.0.0/16",
                            "198.18.0.0/15",
                            "198.51.100.0/24",
                            "203.0.113.0/24",
                            "::1/128",
                            "fc00::/7",
                            "fe80::/10"
                        ],
                        "outboundTag": "direct"
                    },
                    {
                        "type": "field",
                        "domain": [
                            "geosite:cn"
                        ],
                        "outboundTag": "direct"
                    },
                    {
                        "type": "field",
                        "ip": [
                            "geoip:cn",
                            "geoip:private"
                        ],
                        "outboundTag": "direct"
                    }
                ]
            }
        }
        
        # 如果有多个节点，设置第一个为默认出站
        if len([o for o in outbounds if o['tag'] not in ['direct', 'blocked']]) > 0:
            first_proxy_tag = next(o['tag'] for o in outbounds if o['tag'] not in ['direct', 'blocked'])
            v2ray_config["routing"]["rules"].append({
                "type": "field",
                "network": "tcp,udp",
                "outboundTag": first_proxy_tag
            })
        
        return json.dumps(v2ray_config, indent=2, ensure_ascii=False)

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python clash_to_v2ray.py <clash配置文件路径>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = os.path.splitext(input_file)[0] + '_v2ray_links.txt'
    
    try:
        converter = ClashToV2ray(input_file)
        converter.load_yaml()
        links = converter.convert()
        
        if not links:
            print("警告: 未能成功转换任何节点")
            sys.exit(1)
            
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(links))
            
        print(f"转换完成！共转换 {len(links)} 个节点")
        print(f"结果已保存至: {output_file}")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)

def create_gui():
    """创建现代化的双向转换GUI界面"""
    
    # 创建主窗口
    root = tk.Tk()
    root.title("🚀 节点转换工具 - 双向转换版")
    root.geometry("1000x700")
    root.minsize(800, 600)
    
    # 设置主题
    style = ttk.Style()
    style.theme_use('clam')
    
    # 配置样式
    style.configure('Title.TLabel', font=('Microsoft YaHei UI', 12, 'bold'))
    style.configure('Subtitle.TLabel', font=('Microsoft YaHei UI', 10))
    style.configure('Action.TButton', font=('Microsoft YaHei UI', 10, 'bold'))
    style.configure('Tool.TButton', font=('Microsoft YaHei UI', 9))
    
    # 转换模式状态（在创建主窗口后创建）
    current_mode = tk.StringVar(value="none")  # "clash_to_v2ray", "v2ray_to_clash", "to_v2ray_config", "none"
    
    def update_button_styles():
        """更新按钮样式以显示当前选中状态"""
        # 重置所有按钮为未选中状态
        style.configure('Unselected.TButton', background='#f0f0f0', foreground='black')
        clash_to_v2ray_btn.configure(style='Unselected.TButton')
        v2ray_to_clash_btn.configure(style='Unselected.TButton')
        to_v2ray_config_btn.configure(style='Unselected.TButton')
        
        # 根据当前模式设置选中状态
        if current_mode.get() == "clash_to_v2ray":
            style.configure('Selected.TButton', background='#4CAF50', foreground='white')
            clash_to_v2ray_btn.configure(style='Selected.TButton')
        elif current_mode.get() == "v2ray_to_clash":
            style.configure('Selected.TButton', background='#2196F3', foreground='white')
            v2ray_to_clash_btn.configure(style='Selected.TButton')
        elif current_mode.get() == "to_v2ray_config":
            style.configure('Selected.TButton', background='#FF9800', foreground='white')
            to_v2ray_config_btn.configure(style='Selected.TButton')
    
    def paste_input():
        """粘贴输入内容"""
        try:
            content = pyperclip.paste()
            input_text.delete('1.0', tk.END)
            input_text.insert('1.0', content)
        except Exception as e:
            messagebox.showerror("错误", f"粘贴失败: {str(e)}")

    def clear_input():
        """清空输入"""
        input_text.delete('1.0', tk.END)

    def clear_output():
        """清空输出"""
        output_text.delete('1.0', tk.END)

    def convert_clash_to_v2ray():
        """Clash YAML转V2rayN链接"""
        try:
            # 设置当前模式并更新按钮样式
            current_mode.set("clash_to_v2ray")
            update_button_styles()
            
            yaml_content = input_text.get('1.0', tk.END).strip()
            if not yaml_content:
                messagebox.showwarning("警告", "请输入Clash YAML配置！")
                return
            
            # 创建临时文件保存YAML内容
            temp_file = 'temp_config.yaml'
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(yaml_content)
            
            # 使用现有的转换逻辑
            converter = ClashToV2ray(temp_file)
            converter.load_yaml()
            links = converter.convert()
            
            # 删除临时文件
            os.remove(temp_file)
            
            if not links:
                messagebox.showwarning("警告", "未找到可转换的节点！")
                return
            
            # 显示转换结果
            output_text.delete('1.0', tk.END)
            output_text.insert('1.0', '\n'.join(links))
            
            # 更新状态
            status_label.config(text=f"✅ [Clash→V2rayN] 成功转换 {len(links)} 个节点", foreground="green")
            
        except Exception as e:
            messagebox.showerror("错误", f"转换失败: {str(e)}")
            status_label.config(text="❌ 转换失败", foreground="red")

    def convert_v2ray_to_clash():
        """V2rayN链接转Clash YAML"""
        try:
            # 设置当前模式并更新按钮样式
            current_mode.set("v2ray_to_clash")
            update_button_styles()
            
            links_content = input_text.get('1.0', tk.END).strip()
            if not links_content:
                messagebox.showwarning("警告", "请输入V2rayN节点链接！")
                return
            
            # 使用反向转换器
            converter = V2rayToClash()
            yaml_content = converter.convert_to_yaml(links_content)
            
            if not yaml_content:
                messagebox.showwarning("警告", "未找到可转换的节点链接！")
                return
            
            # 显示转换结果
            output_text.delete('1.0', tk.END)
            output_text.insert('1.0', yaml_content)
            
            # 统计节点数量
            proxies = converter.parse_links(links_content)
            status_label.config(text=f"✅ [V2rayN→Clash] 成功转换 {len(proxies)} 个节点", foreground="green")
            
        except Exception as e:
            messagebox.showerror("错误", f"转换失败: {str(e)}")
            status_label.config(text="❌ 转换失败", foreground="red")

    def convert_to_v2ray_config():
        """转换为V2Ray config.json格式"""
        try:
            # 设置当前模式并更新按钮样式
            current_mode.set("to_v2ray_config")
            update_button_styles()
            
            input_content = input_text.get('1.0', tk.END).strip()
            if not input_content:
                messagebox.showwarning("警告", "请输入配置内容！")
                return
            
            # 使用V2Ray配置生成器
            generator = V2rayConfigGenerator()
            config_json = generator.convert_to_v2ray_config(input_content)
            
            if not config_json:
                messagebox.showwarning("警告", "未找到可转换的节点配置！")
                return
            
            # 显示转换结果
            output_text.delete('1.0', tk.END)
            output_text.insert('1.0', config_json)
            
            # 统计节点数量
            try:
                config_data = json.loads(config_json)
                proxy_count = len([o for o in config_data.get('outbounds', []) 
                                 if o['tag'] not in ['direct', 'blocked']])
                status_label.config(text=f"✅ [→V2Ray Config] 成功转换 {proxy_count} 个节点", foreground="green")
            except:
                status_label.config(text="✅ [→V2Ray Config] 转换完成", foreground="green")
            
        except Exception as e:
            messagebox.showerror("错误", f"转换失败: {str(e)}")
            status_label.config(text="❌ 转换失败", foreground="red")

    def copy_output():
        """复制输出内容到剪贴板"""
        try:
            output_content = output_text.get('1.0', tk.END).strip()
            if output_content:
                pyperclip.copy(output_content)
                messagebox.showinfo("成功", "已复制到剪贴板！")
                status_label.config(text="📋 已复制到剪贴板", foreground="blue")
            else:
                messagebox.showwarning("警告", "没有可复制的内容！")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {str(e)}")

    def swap_content():
        """交换输入输出内容"""
        try:
            input_content = input_text.get('1.0', tk.END)
            output_content = output_text.get('1.0', tk.END)
            
            input_text.delete('1.0', tk.END)
            output_text.delete('1.0', tk.END)
            
            input_text.insert('1.0', output_content)
            output_text.insert('1.0', input_content)
            
            status_label.config(text="🔄 已交换输入输出内容", foreground="orange")
        except Exception as e:
            messagebox.showerror("错误", f"交换失败: {str(e)}")

    # 创建主框架
    main_frame = ttk.Frame(root, padding="15")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 标题
    title_frame = ttk.Frame(main_frame)
    title_frame.pack(fill=tk.X, pady=(0, 15))
    
    title_label = ttk.Label(title_frame, text="🚀 节点配置转换工具", style='Title.TLabel')
    title_label.pack(side=tk.LEFT)
    
    subtitle_label = ttk.Label(title_frame, text="支持 Clash ⇄ V2rayN 双向转换 + V2Ray Config 生成", style='Subtitle.TLabel', foreground="gray")
    subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
    
    # 转换方向选择框架
    direction_frame = ttk.LabelFrame(main_frame, text="🔄 转换方向", padding="10")
    direction_frame.pack(fill=tk.X, pady=(0, 15))
    
    # 转换按钮组
    convert_frame = ttk.Frame(direction_frame)
    convert_frame.pack(fill=tk.X)
    
    clash_to_v2ray_btn = ttk.Button(convert_frame, text="📋 Clash YAML → V2rayN 链接", 
                                   command=convert_clash_to_v2ray, style='Action.TButton')
    clash_to_v2ray_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    v2ray_to_clash_btn = ttk.Button(convert_frame, text="🔗 V2rayN 链接 → Clash YAML", 
                                   command=convert_v2ray_to_clash, style='Action.TButton')
    v2ray_to_clash_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    to_v2ray_config_btn = ttk.Button(convert_frame, text="⚙️ 生成 V2Ray Config.json", 
                                    command=convert_to_v2ray_config, style='Action.TButton')
    to_v2ray_config_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    # 初始化按钮样式
    update_button_styles()
    
    swap_btn = ttk.Button(convert_frame, text="🔄 交换内容", command=swap_content, style='Tool.TButton')
    swap_btn.pack(side=tk.RIGHT)
    
    # 主内容区域 - 使用PanedWindow创建可调整大小的分割
    paned = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
    paned.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
    
    # 输入区域
    input_frame = ttk.LabelFrame(paned, text="📝 输入内容", padding="10")
    paned.add(input_frame, weight=1)
    
    # 输入工具栏
    input_toolbar = ttk.Frame(input_frame)
    input_toolbar.pack(fill=tk.X, pady=(0, 5))
    
    paste_btn = ttk.Button(input_toolbar, text="📋 粘贴", command=paste_input, style='Tool.TButton')
    paste_btn.pack(side=tk.LEFT, padx=(0, 5))
    
    clear_input_btn = ttk.Button(input_toolbar, text="🗑️ 清空", command=clear_input, style='Tool.TButton')
    clear_input_btn.pack(side=tk.LEFT, padx=(0, 5))
    
    input_info = ttk.Label(input_toolbar, text="支持粘贴 Clash YAML 配置或 V2rayN 节点链接（自动检测格式）", 
                          foreground="gray", font=('Microsoft YaHei UI', 8))
    input_info.pack(side=tk.RIGHT)
    
    # 输入文本框和滚动条
    input_text_frame = ttk.Frame(input_frame)
    input_text_frame.pack(fill=tk.BOTH, expand=True)
    
    input_text = tk.Text(input_text_frame, wrap=tk.WORD, font=('Consolas', 10))
    input_scrollbar_y = ttk.Scrollbar(input_text_frame, orient=tk.VERTICAL, command=input_text.yview)
    input_scrollbar_x = ttk.Scrollbar(input_text_frame, orient=tk.HORIZONTAL, command=input_text.xview)
    input_text.configure(yscrollcommand=input_scrollbar_y.set, xscrollcommand=input_scrollbar_x.set)
    
    input_text.grid(row=0, column=0, sticky='nsew')
    input_scrollbar_y.grid(row=0, column=1, sticky='ns')
    input_scrollbar_x.grid(row=1, column=0, sticky='ew')
    
    input_text_frame.grid_rowconfigure(0, weight=1)
    input_text_frame.grid_columnconfigure(0, weight=1)
    
    # 输出区域
    output_frame = ttk.LabelFrame(paned, text="📤 输出结果", padding="10")
    paned.add(output_frame, weight=1)
    
    # 输出工具栏
    output_toolbar = ttk.Frame(output_frame)
    output_toolbar.pack(fill=tk.X, pady=(0, 5))
    
    copy_btn = ttk.Button(output_toolbar, text="📋 复制结果", command=copy_output, style='Tool.TButton')
    copy_btn.pack(side=tk.LEFT, padx=(0, 5))
    
    clear_output_btn = ttk.Button(output_toolbar, text="🗑️ 清空", command=clear_output, style='Tool.TButton')
    clear_output_btn.pack(side=tk.LEFT, padx=(0, 5))
    
    output_info = ttk.Label(output_toolbar, text="转换结果将显示在此处", 
                           foreground="gray", font=('Microsoft YaHei UI', 8))
    output_info.pack(side=tk.RIGHT)
    
    # 输出文本框和滚动条
    output_text_frame = ttk.Frame(output_frame)
    output_text_frame.pack(fill=tk.BOTH, expand=True)
    
    output_text = tk.Text(output_text_frame, wrap=tk.WORD, font=('Consolas', 10))
    output_scrollbar_y = ttk.Scrollbar(output_text_frame, orient=tk.VERTICAL, command=output_text.yview)
    output_scrollbar_x = ttk.Scrollbar(output_text_frame, orient=tk.HORIZONTAL, command=output_text.xview)
    output_text.configure(yscrollcommand=output_scrollbar_y.set, xscrollcommand=output_scrollbar_x.set)
    
    output_text.grid(row=0, column=0, sticky='nsew')
    output_scrollbar_y.grid(row=0, column=1, sticky='ns')
    output_scrollbar_x.grid(row=1, column=0, sticky='ew')
    
    output_text_frame.grid_rowconfigure(0, weight=1)
    output_text_frame.grid_columnconfigure(0, weight=1)
    
    # 状态栏
    status_frame = ttk.Frame(main_frame)
    status_frame.pack(fill=tk.X, pady=(10, 0))
    
    status_label = ttk.Label(status_frame, text="准备就绪 - 请选择转换方向并输入内容", 
                            foreground="blue", font=('Microsoft YaHei UI', 9))
    status_label.pack(side=tk.LEFT)
    
    exit_btn = ttk.Button(status_frame, text="❌ 退出", command=root.quit, style='Tool.TButton')
    exit_btn.pack(side=tk.RIGHT)
    
    # 版本信息
    version_label = ttk.Label(status_frame, text="v2.0 - 双向转换版", 
                             foreground="gray", font=('Microsoft YaHei UI', 8))
    version_label.pack(side=tk.RIGHT, padx=(0, 10))
    
    return root

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # 命令行模式
        main()
    else:
        # GUI模式
        root = create_gui()
        root.mainloop()