"""山西地电用电查询 - API 客户端"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import aiohttp

from .const import (
    BASE_URL,
    API_FEES,
    API_CONS_INFO,
    API_RECORD_LIST,
    API_LIST_BY_YEAR,
    API_DAYS_OF_MONTH,
    API_DAYS_ONLY,
)

_LOGGER = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/132.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/json;charset=UTF-8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


class SxgjdlApiError(Exception):
    """API 调用异常"""


class SxgjdlApiClient:
    """山西地电 API 客户端"""

    def __init__(
        self,
        cons_no: str,
        org_no: str,
        open_id: str = "",
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self.cons_no = cons_no
        self.org_no = org_no
        self.open_id = open_id
        self._session = session
        self._own_session = session is None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=HEADERS)
        return self._session

    async def close(self) -> None:
        if self._own_session and self._session and not self._session.closed:
            await self._session.close()

    async def _get(self, path: str, params: dict) -> dict:
        """发起 GET 请求并返回解析后的 JSON"""
        url = BASE_URL + path
        session = await self._get_session()
        try:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                resp.raise_for_status()
                data = await resp.json(content_type=None)
                _LOGGER.debug("GET %s params=%s -> %s", path, params, data)
                return data
        except aiohttp.ClientConnectorError as err:
            raise SxgjdlApiError(f"无法连接到服务器: {err}") from err
        except aiohttp.ClientResponseError as err:
            raise SxgjdlApiError(f"HTTP 错误 {err.status}: {err.message}") from err
        except Exception as err:
            raise SxgjdlApiError(f"请求异常: {err}") from err

    # ------------------------------------------------------------------ #
    #  公开接口                                                             #
    # ------------------------------------------------------------------ #

    async def get_fees(self) -> dict:
        """获取电费信息（余额、应收金额等）"""
        params: dict[str, Any] = {"consNo": self.cons_no}
        if self.open_id:
            params["openId"] = self.open_id
        return await self._get(API_FEES, params)

    async def get_cons_info(self) -> dict:
        """获取用户基本信息（户名、地址等）"""
        params = {"consNo": self.cons_no}
        return await self._get(API_CONS_INFO, params)

    async def get_record_list(self, year: int | None = None) -> dict:
        """获取指定年度每月用电量及电费汇总"""
        if year is None:
            year = datetime.now().year
        params = {
            "consNo": self.cons_no,
            "orgNo": self.org_no,
            "year": str(year),
        }
        return await self._get(API_RECORD_LIST, params)

    async def get_list_by_year(self, year: int | None = None) -> dict:
        """获取指定年度账单明细（含阶梯电价）"""
        if year is None:
            year = datetime.now().year
        bgn_ym = f"{year}01"
        end_ym = f"{year}12"
        params = {
            "consNo": self.cons_no,
            "orgNo": self.org_no,
            "bgnYm": bgn_ym,
            "endYm": end_ym,
        }
        return await self._get(API_LIST_BY_YEAR, params)

    async def get_days_of_month(self, year_month: str | None = None) -> dict:
        """获取指定月份每日用电量及预估电费，格式 YYYYMM"""
        if year_month is None:
            year_month = datetime.now().strftime("%Y%m")
        params = {
            "consNo": self.cons_no,
            "date": year_month,
        }
        return await self._get(API_DAYS_OF_MONTH, params)

    async def get_days_only_data(self, date: str | None = None) -> dict:
        """获取指定日期分时用电（峰/平/谷），格式 YYYYMMDD"""
        if date is None:
            date = datetime.now().strftime("%Y%m%d")
        params = {
            "consNo": self.cons_no,
            "date": date,
        }
        return await self._get(API_DAYS_ONLY, params)

    async def validate_connection(self) -> bool:
        """验证户号是否有效（用于 config flow）"""
        try:
            data = await self.get_cons_info()
            return data.get("flag") is True
        except SxgjdlApiError:
            return False
