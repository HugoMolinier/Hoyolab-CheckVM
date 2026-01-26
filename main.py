import os

from dataclasses import dataclass
from typing import Optional
import requests

from DiscordNotifier import DiscordWebhookClient
from dotenv import load_dotenv

load_dotenv()

GAME_DATA = {
    "hk4e_global": {
        "game_name": "Genshin Impact",
        "main": "Traveler",
        "act_id": "e202102251931481",
        "info_url": "https://sg-hk4e-api.hoyolab.com/event/sol/info",
        "reward_url": "https://sg-hk4e-api.hoyolab.com/event/sol/home",
        "sign_url": "https://sg-hk4e-api.hoyolab.com/event/sol/sign"
    },
    "hkrpg_global": {
        "game_name": "Honkai: Star Rail",
        "main": "Trailblazer",
        "act_id": "e202303301540311",
        "info_url": "https://sg-public-api.hoyolab.com/event/luna/hkrpg/os/info",
        "reward_url": "https://sg-public-api.hoyolab.com/event/luna/hkrpg/os/home",
        "sign_url": "https://sg-public-api.hoyolab.com/event/luna/hkrpg/os/sign"
    },
    "nap_global": {
        "game_name": "Zenless Zone Zero",
        "main": "Proxy",
        "act_id": "e202406031448091",
        "info_url": "https://sg-act-nap-api.hoyolab.com/event/luna/zzz/os/info",
        "reward_url": "https://sg-act-nap-api.hoyolab.com/event/luna/zzz/os/home",
        "sign_url": "https://sg-act-nap-api.hoyolab.com/event/luna/zzz/os/sign"
    },
}


@dataclass
class GameAccount:
    game_biz: str
    region_name: str
    game_uid: str
    level: int
    nickname: str
    region: str
    claimed_reward: Optional["Reward"] = None

    def __init__(self, **kwargs):
        # Remplissage automatique des champs connus
        self.game_biz = kwargs.get("game_biz")
        self.region_name = kwargs.get("region_name", "").split(" ")[0]
        self.game_uid = kwargs.get("game_uid")
        self.level = kwargs.get("level")
        self.nickname = kwargs.get("nickname")
        self.region = kwargs.get("region")


@dataclass
class CheckInInfo:
    is_sign: bool
    total_sign_day: int
    def __init__(self, **kwargs):
        self.is_sign = kwargs.get("is_sign")
        self.total_sign_day = kwargs.get("total_sign_day")


@dataclass
class Reward:
    name: str
    cnt: int
    icon: str
    game_name: Optional[str] = None
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.cnt = kwargs.get("cnt")
        self.icon = kwargs.get("icon")
        self.game_name = None



class ApiClient:
    def __init__(self, headers):
        self.session = requests.Session()
        self.headers = headers

    def _request(self, url):
        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if "retcode" not in data or "data" not in data:
                raise Exception(f"Unexpected JSON format from {url}")

            return data
        except requests.exceptions.RequestException as e:
            return

    def _check_json_format(self, data, url, required_fields):
        for field in required_fields:
            if isinstance(field, str):
                if field not in data:
                    return False
            elif isinstance(field, list):
                if not self._check_json_format(data.get(field[0]), url, field[1:]):
                    return False

        return True


class HoyolabClient(ApiClient):
    def __init__(self, cookie, notifier):
        headers = {
            "Cookie": cookie,
            "User-Agent": os.environ.get("USER_AGENT",
                                         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.47"),
            "Referer": "https://act.hoyolab.com/",
            "Origin": "https://act.hoyolab.com/",
            "Accept-Encoding": "gzip, deflate, br"
        }
        self.notifier = notifier
        super().__init__(headers)
        self.cookie = cookie

    def verify_cookie(self):
        url = "https://api-account-os.hoyolab.com/auth/api/getUserAccountInfoByLToken"
        res = self._request(url)
        if not res or res["retcode"] != 0:
            raise Exception("Invalid cookie")

    def get_game_accounts(self):
        url = "https://api-os-takumi.hoyolab.com/binding/api/getUserGameRolesByCookie"
        res = self._request(url)
        if not self._check_json_format(res, url, ["data", ["list"]]):
            return []

        accounts = [GameAccount(**account) for account in res["data"]["list"]]
        return accounts

    def check_in(self, account):
        if account.game_biz not in GAME_DATA:
            raise Exception("Unsupported game")

        data = GAME_DATA[account.game_biz]
        act_id = data["act_id"]
        info_res = self._request(f"{data['info_url']}?act_id={act_id}")
        if not self._check_json_format(info_res, data["info_url"], ["data"]):
            return
        rewards_res = self._request(f"{data['reward_url']}?act_id={act_id}")
        if not self._check_json_format(rewards_res, data["reward_url"], ["data", ["awards"]]):
            return

        info = CheckInInfo(**info_res["data"])
        rewards = [Reward(**reward) for reward in rewards_res["data"]["awards"]]


        if not info.is_sign:
            try:
                sign_res = self.session.post(f"{data['sign_url']}?act_id={act_id}", headers=self.headers)
                sign_res.raise_for_status()
                sign_res_json = sign_res.json()
                if "retcode" not in sign_res_json or sign_res_json["retcode"] != 0:
                    raise Exception(f"Failed to check in: {sign_res_json.get('message', 'Unknown error')}")

                reward = rewards[info.total_sign_day]
                reward.game_name = data["game_name"]
                account.claimed_reward = reward
            except requests.exceptions.RequestException as e:
                return
        else:
            self.notifier.send_error(f"You've already checked in today, {data['main']}")


def check_in(client, accounts):
    for account in accounts:
        try:
            client.check_in(account)
            if account.claimed_reward:
                client.notifier.send_notification(account, account.claimed_reward)
        except Exception as _:
            return


def run():
    cookie = os.environ.get("COOKIE")
    if not cookie:
        raise Exception("COOKIE environment variable not set")

    webhook_url = os.environ.get("DISCORD_WEBHOOK")
    notifier = DiscordWebhookClient(webhook_url)

    cookies = cookie.split('#')

    for i, cookie in enumerate(cookies):
        client = HoyolabClient(cookie, notifier)

        try:
            client.verify_cookie()
        except Exception as _:
            continue


        accounts = client.get_game_accounts()
        check_in(client, accounts)


run()
