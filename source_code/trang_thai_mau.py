"""Các trạng thái mẫu dùng để benchmark Minimax và Alpha-Beta."""

from __future__ import annotations

from typing import List, Tuple

from caro_ai import BanCo, MAY, NGUOI, tao_ban_co


def tao_tu_nuoc_di(cac_nuoc: List[Tuple[int, int, str]], kich_thuoc: int = 9) -> BanCo:
    """Tạo bàn cờ từ danh sách nước đi 1-based: (hàng, cột, quân)."""
    ban_co = tao_ban_co(kich_thuoc)
    for hang, cot, quan in cac_nuoc:
        ban_co[hang - 1][cot - 1] = quan
    return ban_co


def lay_trang_thai_mau() -> List[Tuple[str, BanCo]]:
    """Trả về ít nhất 5 trạng thái để kiểm thử theo yêu cầu báo cáo."""
    return [
        (
            "Dau van - ban co rong",
            tao_tu_nuoc_di([]),
        ),
        (
            "Giua van - hai ben da co nhieu quan",
            tao_tu_nuoc_di(
                [
                    (5, 5, MAY),
                    (5, 6, NGUOI),
                    (4, 5, MAY),
                    (6, 5, NGUOI),
                    (4, 4, MAY),
                    (6, 6, NGUOI),
                    (3, 5, MAY),
                    (7, 5, NGUOI),
                ]
            ),
        ),
        (
            "May co the thang ngay",
            tao_tu_nuoc_di(
                [
                    (5, 3, MAY),
                    (5, 4, MAY),
                    (5, 5, MAY),
                    (3, 3, NGUOI),
                    (4, 7, NGUOI),
                    (6, 6, NGUOI),
                ]
            ),
        ),
        (
            "Nguoi sap thang - may can chan",
            tao_tu_nuoc_di(
                [
                    (4, 3, NGUOI),
                    (4, 4, NGUOI),
                    (4, 5, NGUOI),
                    (5, 5, MAY),
                    (6, 6, MAY),
                    (3, 7, MAY),
                ]
            ),
        ),
        (
            "Hai ben deu co co hoi tan cong",
            tao_tu_nuoc_di(
                [
                    (5, 4, MAY),
                    (5, 5, MAY),
                    (6, 5, MAY),
                    (4, 4, NGUOI),
                    (4, 5, NGUOI),
                    (4, 6, NGUOI),
                    (6, 4, NGUOI),
                    (7, 5, MAY),
                ]
            ),
        ),
        (
            "Nhieu nhanh hop le",
            tao_tu_nuoc_di(
                [
                    (3, 3, MAY),
                    (3, 4, NGUOI),
                    (3, 5, MAY),
                    (4, 3, NGUOI),
                    (4, 4, MAY),
                    (4, 5, NGUOI),
                    (5, 3, MAY),
                    (5, 4, NGUOI),
                    (5, 5, MAY),
                    (6, 6, NGUOI),
                    (6, 7, MAY),
                    (7, 6, NGUOI),
                ]
            ),
        ),
    ]
