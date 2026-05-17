"""
Caro AI console - Minimax va Alpha-Beta pruning.
Luật theo đề: bàn cờ tối thiểu 9x9, thắng khi có 4 quân liên tiếp,
không xét luật chặn hai đầu.

Quy ước:
- Người chơi: X
- Máy tính: O
- Ô trống: .

Tên biến dùng tiếng Việt không dấu để tránh lỗi mã hóa khi chạy Python.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import inf
from time import perf_counter
from typing import List, Optional, Sequence, Tuple

Quan = str
OCo = Tuple[int, int]
BanCo = List[List[Quan]]

NGUOI = "X"
MAY = "O"
TRONG = "."
SO_QUAN_THANG = 4
DIEM_THANG = 10_000_000

# 4 hướng đủ để kiểm tra mọi chuỗi: ngang, dọc, chéo xuống, chéo lên.
CAC_HUONG: Sequence[OCo] = ((0, 1), (1, 0), (1, 1), (1, -1))


@dataclass
class KetQuaTimKiem:
    """Kết quả một lần AI chọn nước đi."""

    nuoc_di: Optional[OCo]
    gia_tri: int
    do_sau: int
    so_trang_thai_da_xet: int
    thoi_gian_giay: float
    thuat_toan: str


def tao_ban_co(kich_thuoc: int = 9) -> BanCo:
    """Tạo bàn cờ rỗng."""
    if kich_thuoc < 9:
        raise ValueError("Kích thước bàn cờ phải tối thiểu là 9.")
    return [[TRONG for _ in range(kich_thuoc)] for _ in range(kich_thuoc)]


def sao_chep_ban_co(ban_co: BanCo) -> BanCo:
    """Tạo bản sao bàn cờ để dùng trong benchmark/test."""
    return [hang[:] for hang in ban_co]


def kich_thuoc_ban_co(ban_co: BanCo) -> int:
    return len(ban_co)


def trong_ban_co(ban_co: BanCo, hang: int, cot: int) -> bool:
    n = kich_thuoc_ban_co(ban_co)
    return 0 <= hang < n and 0 <= cot < n


def in_ban_co(ban_co: BanCo) -> None:
    """In bàn cờ ra console, dùng chỉ số 1-based cho người chơi dễ nhập."""
    n = kich_thuoc_ban_co(ban_co)
    print("\n   " + " ".join(f"{i:2d}" for i in range(1, n + 1)))
    for chi_so_hang, hang in enumerate(ban_co, start=1):
        print(f"{chi_so_hang:2d} " + " ".join(f" {o}" for o in hang))
    print()


def dat_quan(ban_co: BanCo, hang: int, cot: int, quan: Quan) -> bool:
    """Đặt quân nếu ô hợp lệ và còn trống. Trả về True nếu đặt được."""
    if not trong_ban_co(ban_co, hang, cot):
        return False
    if ban_co[hang][cot] != TRONG:
        return False
    ban_co[hang][cot] = quan
    return True


def xoa_quan(ban_co: BanCo, hang: int, cot: int) -> None:
    ban_co[hang][cot] = TRONG


def ban_co_day(ban_co: BanCo) -> bool:
    return all(o != TRONG for hang in ban_co for o in hang)


def kiem_tra_thang(ban_co: BanCo, quan: Quan) -> bool:
    """Kiểm tra một quân có đủ 4 quân liên tiếp hay chưa."""
    n = kich_thuoc_ban_co(ban_co)
    for hang in range(n):
        for cot in range(n):
            if ban_co[hang][cot] != quan:
                continue
            for buoc_hang, buoc_cot in CAC_HUONG:
                du_4_quan = True
                for k in range(SO_QUAN_THANG):
                    h = hang + k * buoc_hang
                    c = cot + k * buoc_cot
                    if not trong_ban_co(ban_co, h, c) or ban_co[h][c] != quan:
                        du_4_quan = False
                        break
                if du_4_quan:
                    return True
    return False


def trang_thai_ket_thuc(ban_co: BanCo) -> Optional[str]:
    """Trả về MAY/NGUOI/'hoa' nếu kết thúc, ngược lại trả về None."""
    if kiem_tra_thang(ban_co, MAY):
        return MAY
    if kiem_tra_thang(ban_co, NGUOI):
        return NGUOI
    if ban_co_day(ban_co):
        return "hoa"
    return None


def lay_cac_o_da_danh(ban_co: BanCo) -> List[OCo]:
    return [
        (hang, cot)
        for hang, dong in enumerate(ban_co)
        for cot, o in enumerate(dong)
        if o != TRONG
    ]


def _do_dai_chuoi_qua_o(ban_co: BanCo, hang: int, cot: int, quan: Quan, huong: OCo) -> int:
    """Đếm độ dài chuỗi liên tiếp nếu đặt `quan` tại ô (hang, cot)."""
    buoc_hang, buoc_cot = huong
    tong = 1

    h, c = hang + buoc_hang, cot + buoc_cot
    while trong_ban_co(ban_co, h, c) and ban_co[h][c] == quan:
        tong += 1
        h += buoc_hang
        c += buoc_cot

    h, c = hang - buoc_hang, cot - buoc_cot
    while trong_ban_co(ban_co, h, c) and ban_co[h][c] == quan:
        tong += 1
        h -= buoc_hang
        c -= buoc_cot

    return tong


def _diem_nuoc_di_so_bo(ban_co: BanCo, hang: int, cot: int) -> int:
    """
    Chấm nhanh một nước đi để sắp xếp thứ tự mở rộng.
    Hàm này chỉ nhìn các chuỗi đi qua ô đang xét nên nhanh hơn đánh giá toàn bàn.
    """
    if ban_co[hang][cot] != TRONG:
        return -DIEM_THANG

    trong_so_tan_cong = {1: 10, 2: 300, 3: 20_000, 4: 5 * DIEM_THANG}
    trong_so_phong_thu = {1: 12, 2: 360, 3: 30_000, 4: 4 * DIEM_THANG}

    diem = 0
    for huong in CAC_HUONG:
        dai_may = min(_do_dai_chuoi_qua_o(ban_co, hang, cot, MAY, huong), 4)
        dai_nguoi = min(_do_dai_chuoi_qua_o(ban_co, hang, cot, NGUOI, huong), 4)
        diem += trong_so_tan_cong[dai_may]
        diem += trong_so_phong_thu[dai_nguoi]
    return diem


def sinh_nuoc_di_hop_le(
    ban_co: BanCo,
    ban_kinh: int = 2,
    gioi_han_so_nuoc: int = 12,
) -> List[OCo]:
    """
    Sinh nước đi hợp lệ gần các quân đã đánh để giảm không gian tìm kiếm.
    Nếu bàn cờ rỗng, AI chọn vùng trung tâm.

    Sau khi sinh ứng viên, chương trình sắp xếp theo điểm sơ bộ rồi giữ lại
    một số nước đi tốt nhất. Đây là move ordering + candidate limiting, giúp
    Minimax độ sâu 3 chạy được trong thời gian hợp lý trên bàn 9x9.
    """
    n = kich_thuoc_ban_co(ban_co)
    cac_o_da_danh = lay_cac_o_da_danh(ban_co)

    if not cac_o_da_danh:
        tam = n // 2
        return [(tam, tam)]

    tap_nuoc_di: set[OCo] = set()
    for hang, cot in cac_o_da_danh:
        for dh in range(-ban_kinh, ban_kinh + 1):
            for dc in range(-ban_kinh, ban_kinh + 1):
                h = hang + dh
                c = cot + dc
                if trong_ban_co(ban_co, h, c) and ban_co[h][c] == TRONG:
                    tap_nuoc_di.add((h, c))

    tam = (n - 1) / 2
    cac_nuoc_di = sorted(
        tap_nuoc_di,
        key=lambda o: (
            -_diem_nuoc_di_so_bo(ban_co, o[0], o[1]),
            (o[0] - tam) ** 2 + (o[1] - tam) ** 2,
            o[0],
            o[1],
        ),
    )

    if gioi_han_so_nuoc > 0:
        return cac_nuoc_di[:gioi_han_so_nuoc]
    return cac_nuoc_di


def diem_cua_cua_so(so_may: int, so_nguoi: int) -> int:
    """
    Chấm điểm một đoạn 4 ô.
    Đoạn có cả X và O thì không giúp trực tiếp bên nào nên cho 0.
    """
    if so_may > 0 and so_nguoi > 0:
        return 0

    # Trọng số phòng thủ cho chuỗi 3 của người lớn hơn một chút để AI ưu tiên chặn.
    diem_may = {0: 0, 1: 10, 2: 200, 3: 6_000, 4: DIEM_THANG}
    diem_nguoi = {0: 0, 1: 12, 2: 240, 3: 8_000, 4: DIEM_THANG}

    if so_may > 0:
        return diem_may[so_may]
    if so_nguoi > 0:
        return -diem_nguoi[so_nguoi]
    return 0


def danh_gia_ban_co(ban_co: BanCo) -> int:
    """
    Hàm đánh giá trạng thái chưa kết thúc.
    Quét tất cả đoạn 4 ô theo 4 hướng và cộng điểm tấn công/phòng thủ.
    """
    if kiem_tra_thang(ban_co, MAY):
        return DIEM_THANG
    if kiem_tra_thang(ban_co, NGUOI):
        return -DIEM_THANG

    n = kich_thuoc_ban_co(ban_co)
    tong_diem = 0

    for hang in range(n):
        for cot in range(n):
            for buoc_hang, buoc_cot in CAC_HUONG:
                cua_so: List[Quan] = []
                hop_le = True
                for k in range(SO_QUAN_THANG):
                    h = hang + k * buoc_hang
                    c = cot + k * buoc_cot
                    if not trong_ban_co(ban_co, h, c):
                        hop_le = False
                        break
                    cua_so.append(ban_co[h][c])
                if not hop_le:
                    continue

                so_may = cua_so.count(MAY)
                so_nguoi = cua_so.count(NGUOI)
                tong_diem += diem_cua_cua_so(so_may, so_nguoi)

    return tong_diem


def _gia_tri_ket_thuc(ban_co: BanCo, do_sau_con_lai: int) -> Optional[int]:
    """Trả điểm nếu trạng thái đã kết thúc."""
    ket_thuc = trang_thai_ket_thuc(ban_co)
    if ket_thuc == MAY:
        return DIEM_THANG + do_sau_con_lai
    if ket_thuc == NGUOI:
        return -DIEM_THANG - do_sau_con_lai
    if ket_thuc == "hoa":
        return 0
    return None


def minimax(
    ban_co: BanCo,
    do_sau_con_lai: int,
    la_luot_may: bool,
    thong_ke: dict[str, int],
) -> Tuple[int, Optional[OCo]]:
    """Minimax có giới hạn độ sâu."""
    thong_ke["so_trang_thai_da_xet"] += 1

    diem_ket_thuc = _gia_tri_ket_thuc(ban_co, do_sau_con_lai)
    if diem_ket_thuc is not None:
        return diem_ket_thuc, None
    if do_sau_con_lai == 0:
        return danh_gia_ban_co(ban_co), None

    cac_nuoc_di = sinh_nuoc_di_hop_le(ban_co)
    if not cac_nuoc_di:
        return 0, None

    if la_luot_may:
        gia_tri_tot_nhat = -inf
        nuoc_di_tot_nhat: Optional[OCo] = None
        for hang, cot in cac_nuoc_di:
            ban_co[hang][cot] = MAY
            gia_tri, _ = minimax(ban_co, do_sau_con_lai - 1, False, thong_ke)
            xoa_quan(ban_co, hang, cot)
            if gia_tri > gia_tri_tot_nhat:
                gia_tri_tot_nhat = gia_tri
                nuoc_di_tot_nhat = (hang, cot)
        return int(gia_tri_tot_nhat), nuoc_di_tot_nhat

    gia_tri_tot_nhat = inf
    nuoc_di_tot_nhat = None
    for hang, cot in cac_nuoc_di:
        ban_co[hang][cot] = NGUOI
        gia_tri, _ = minimax(ban_co, do_sau_con_lai - 1, True, thong_ke)
        xoa_quan(ban_co, hang, cot)
        if gia_tri < gia_tri_tot_nhat:
            gia_tri_tot_nhat = gia_tri
            nuoc_di_tot_nhat = (hang, cot)
    return int(gia_tri_tot_nhat), nuoc_di_tot_nhat


def alpha_beta(
    ban_co: BanCo,
    do_sau_con_lai: int,
    alpha: float,
    beta: float,
    la_luot_may: bool,
    thong_ke: dict[str, int],
) -> Tuple[int, Optional[OCo]]:
    """Minimax cải tiến bằng cắt nhánh Alpha-Beta."""
    thong_ke["so_trang_thai_da_xet"] += 1

    diem_ket_thuc = _gia_tri_ket_thuc(ban_co, do_sau_con_lai)
    if diem_ket_thuc is not None:
        return diem_ket_thuc, None
    if do_sau_con_lai == 0:
        return danh_gia_ban_co(ban_co), None

    cac_nuoc_di = sinh_nuoc_di_hop_le(ban_co)
    if not cac_nuoc_di:
        return 0, None

    if la_luot_may:
        gia_tri_tot_nhat = -inf
        nuoc_di_tot_nhat: Optional[OCo] = None
        for hang, cot in cac_nuoc_di:
            ban_co[hang][cot] = MAY
            gia_tri, _ = alpha_beta(ban_co, do_sau_con_lai - 1, alpha, beta, False, thong_ke)
            xoa_quan(ban_co, hang, cot)

            if gia_tri > gia_tri_tot_nhat:
                gia_tri_tot_nhat = gia_tri
                nuoc_di_tot_nhat = (hang, cot)
            alpha = max(alpha, gia_tri_tot_nhat)
            if beta <= alpha:
                break
        return int(gia_tri_tot_nhat), nuoc_di_tot_nhat

    gia_tri_tot_nhat = inf
    nuoc_di_tot_nhat = None
    for hang, cot in cac_nuoc_di:
        ban_co[hang][cot] = NGUOI
        gia_tri, _ = alpha_beta(ban_co, do_sau_con_lai - 1, alpha, beta, True, thong_ke)
        xoa_quan(ban_co, hang, cot)

        if gia_tri < gia_tri_tot_nhat:
            gia_tri_tot_nhat = gia_tri
            nuoc_di_tot_nhat = (hang, cot)
        beta = min(beta, gia_tri_tot_nhat)
        if beta <= alpha:
            break
    return int(gia_tri_tot_nhat), nuoc_di_tot_nhat


def chon_nuoc_di(ban_co: BanCo, do_sau: int = 2, thuat_toan: str = "alpha-beta") -> KetQuaTimKiem:
    """Chọn nước đi cho máy và trả về thông tin đo đạc."""
    if do_sau < 1:
        raise ValueError("Độ sâu phải >= 1.")

    thuat_toan_chuan = thuat_toan.strip().lower().replace("_", "-")
    thong_ke = {"so_trang_thai_da_xet": 0}
    bat_dau = perf_counter()

    if thuat_toan_chuan in {"minimax", "mini-max"}:
        gia_tri, nuoc_di = minimax(ban_co, do_sau, True, thong_ke)
        ten_thuat_toan = "Minimax"
    elif thuat_toan_chuan in {"alpha-beta", "alphabeta", "alpha beta"}:
        gia_tri, nuoc_di = alpha_beta(ban_co, do_sau, -inf, inf, True, thong_ke)
        ten_thuat_toan = "Alpha-Beta"
    else:
        raise ValueError("Thuật toán phải là 'minimax' hoặc 'alpha-beta'.")

    thoi_gian = perf_counter() - bat_dau
    return KetQuaTimKiem(
        nuoc_di=nuoc_di,
        gia_tri=gia_tri,
        do_sau=do_sau,
        so_trang_thai_da_xet=thong_ke["so_trang_thai_da_xet"],
        thoi_gian_giay=thoi_gian,
        thuat_toan=ten_thuat_toan,
    )


def nguoi_nhap_nuoc_di(ban_co: BanCo) -> OCo:
    """Đọc nước đi người chơi từ console."""
    n = kich_thuoc_ban_co(ban_co)
    while True:
        du_lieu = input("Nhập nước đi của bạn dạng 'hàng cột' (ví dụ 5 5): ").strip()
        try:
            hang_text, cot_text = du_lieu.split()
            hang = int(hang_text) - 1
            cot = int(cot_text) - 1
        except ValueError:
            print("Dữ liệu không đúng. Hãy nhập 2 số, ví dụ: 5 5.")
            continue

        if not (0 <= hang < n and 0 <= cot < n):
            print(f"Hàng/cột phải nằm trong khoảng 1 đến {n}.")
            continue
        if ban_co[hang][cot] != TRONG:
            print("Ô này đã có quân. Hãy chọn ô khác.")
            continue
        return hang, cot


def chay_choi_console() -> None:
    """Chạy chế độ người chơi đấu với máy trên console."""
    print("=== CARO AI - Minimax / Alpha-Beta ===")
    print("Luật: ai có 4 quân liên tiếp trước thì thắng. Người: X, Máy: O")

    while True:
        try:
            kich_thuoc = int(input("Nhập kích thước bàn cờ, tối thiểu 9 (mặc định 9): ") or "9")
            ban_co = tao_ban_co(kich_thuoc)
            break
        except ValueError as loi:
            print(loi)

    while True:
        try:
            do_sau = int(input("Nhập độ sâu tìm kiếm, gợi ý 1-3 (mặc định 2): ") or "2")
            if do_sau < 1:
                raise ValueError
            break
        except ValueError:
            print("Độ sâu phải là số nguyên >= 1.")

    lua_chon = input("Chọn AI: 1 = Minimax, 2 = Alpha-Beta (mặc định 2): ").strip() or "2"
    thuat_toan = "minimax" if lua_chon == "1" else "alpha-beta"

    luot_nguoi = True
    while True:
        in_ban_co(ban_co)

        if luot_nguoi:
            hang, cot = nguoi_nhap_nuoc_di(ban_co)
            dat_quan(ban_co, hang, cot, NGUOI)
        else:
            print("Máy đang chọn nước đi...")
            ket_qua = chon_nuoc_di(ban_co, do_sau, thuat_toan)
            if ket_qua.nuoc_di is None:
                print("Máy không còn nước đi hợp lệ.")
                break
            hang, cot = ket_qua.nuoc_di
            dat_quan(ban_co, hang, cot, MAY)
            print(
                f"Máy đánh: hàng {hang + 1}, cột {cot + 1} | "
                f"thuật toán: {ket_qua.thuat_toan} | "
                f"giá trị: {ket_qua.gia_tri} | "
                f"độ sâu: {ket_qua.do_sau} | "
                f"trạng thái đã xét: {ket_qua.so_trang_thai_da_xet} | "
                f"thời gian: {ket_qua.thoi_gian_giay:.4f}s"
            )

        ket_thuc = trang_thai_ket_thuc(ban_co)
        if ket_thuc is not None:
            in_ban_co(ban_co)
            if ket_thuc == MAY:
                print("Kết quả: Máy thắng.")
            elif ket_thuc == NGUOI:
                print("Kết quả: Người chơi thắng.")
            else:
                print("Kết quả: Hòa.")
            break

        luot_nguoi = not luot_nguoi


if __name__ == "__main__":
    chay_choi_console()
