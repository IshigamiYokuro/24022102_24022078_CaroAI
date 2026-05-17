"""Chạy thực nghiệm so sánh Minimax và Alpha-Beta."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List

from caro_ai import chon_nuoc_di, sao_chep_ban_co
from trang_thai_mau import lay_trang_thai_mau


def chay_benchmark(cac_do_sau: List[int] | None = None) -> List[Dict[str, object]]:
    if cac_do_sau is None:
        cac_do_sau = [1, 2, 3]

    ket_qua_tong: List[Dict[str, object]] = []
    cac_trang_thai = lay_trang_thai_mau()

    for ten_trang_thai, ban_co_goc in cac_trang_thai:
        for do_sau in cac_do_sau:
            ket_qua_theo_thuat_toan = {}
            for thuat_toan in ["minimax", "alpha-beta"]:
                ban_co = sao_chep_ban_co(ban_co_goc)
                ket_qua = chon_nuoc_di(ban_co, do_sau, thuat_toan)
                nuoc_di_text = "None" if ket_qua.nuoc_di is None else f"({ket_qua.nuoc_di[0] + 1},{ket_qua.nuoc_di[1] + 1})"
                dong = {
                    "trang_thai": ten_trang_thai,
                    "do_sau": do_sau,
                    "thuat_toan": ket_qua.thuat_toan,
                    "nuoc_di": nuoc_di_text,
                    "gia_tri": ket_qua.gia_tri,
                    "so_trang_thai_da_xet": ket_qua.so_trang_thai_da_xet,
                    "thoi_gian_giay": round(ket_qua.thoi_gian_giay, 6),
                }
                ket_qua_tong.append(dong)
                ket_qua_theo_thuat_toan[ket_qua.thuat_toan] = dong

            # Thêm dòng so sánh giảm trạng thái giữa hai thuật toán.
            mm = ket_qua_theo_thuat_toan["Minimax"]
            ab = ket_qua_theo_thuat_toan["Alpha-Beta"]
            so_mm = int(mm["so_trang_thai_da_xet"])
            so_ab = int(ab["so_trang_thai_da_xet"])
            ti_le_giam = 0 if so_mm == 0 else (so_mm - so_ab) * 100 / so_mm
            ket_qua_tong.append(
                {
                    "trang_thai": ten_trang_thai,
                    "do_sau": do_sau,
                    "thuat_toan": "So sanh",
                    "nuoc_di": f"MM {mm['nuoc_di']} | AB {ab['nuoc_di']}",
                    "gia_tri": f"MM {mm['gia_tri']} | AB {ab['gia_tri']}",
                    "so_trang_thai_da_xet": f"giam {ti_le_giam:.2f}%",
                    "thoi_gian_giay": "",
                }
            )

    return ket_qua_tong


def luu_csv(ket_qua: List[Dict[str, object]], duong_dan: Path) -> None:
    if not ket_qua:
        return
    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    with duong_dan.open("w", newline="", encoding="utf-8-sig") as tep:
        writer = csv.DictWriter(tep, fieldnames=list(ket_qua[0].keys()))
        writer.writeheader()
        writer.writerows(ket_qua)


def main() -> None:
    ket_qua = chay_benchmark()
    duong_dan = Path(__file__).resolve().parent.parent / "ket_qua_thuc_nghiem.csv"
    luu_csv(ket_qua, duong_dan)

    print(f"Đã lưu kết quả vào: {duong_dan}")
    print("\nMột số dòng kết quả đầu:")
    for dong in ket_qua[:12]:
        print(dong)


if __name__ == "__main__":
    main()
