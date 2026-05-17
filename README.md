# Caro AI - Minimax và Alpha-Beta

Project cài đặt trò chơi Caro giữa người chơi và máy tính theo luật: bàn cờ tối thiểu 9x9, người chơi là `X`, máy là `O`, ô trống là `.`, thắng khi có 4 quân liên tiếp theo hàng ngang, hàng dọc hoặc đường chéo. Không xét luật chặn hai đầu.

## Cấu trúc thư mục

```text
mssv1_mssv2_mssv3_CaroAI/
├── source_code/
│   ├── main.py              # File chạy game console
│   ├── caro_ai.py           # Luật chơi, Minimax, Alpha-Beta, hàm đánh giá
│   ├── benchmark.py         # Chạy thực nghiệm so sánh thuật toán
│   └── trang_thai_mau.py    # 6 trạng thái kiểm thử mẫu
├── requirements.txt
├── ket_qua_thuc_nghiem.csv  # Sinh ra sau khi chạy benchmark
└── BAO_CAO_MAU.md           # Nội dung báo cáo mẫu để chuyển sang PDF
```

## Cách chạy game

Yêu cầu Python 3.10 trở lên.

```bash
cd mssv1_mssv2_mssv3_CaroAI/source_code
python main.py
```

Khi chạy, chương trình sẽ hỏi:

1. Kích thước bàn cờ, mặc định là 9.
2. Độ sâu tìm kiếm, gợi ý 1 đến 3.
3. Thuật toán AI: `1 = Minimax`, `2 = Alpha-Beta`.

Người chơi nhập nước đi theo dạng:

```text
hàng cột
```

Ví dụ:

```text
5 5
```

## Cách chạy benchmark

```bash
cd mssv1_mssv2_mssv3_CaroAI/source_code
python benchmark.py
```

Kết quả sẽ được lưu vào file:

```text
../ket_qua_thuc_nghiem.csv
```

Benchmark chạy cả Minimax và Alpha-Beta trên cùng các trạng thái bàn cờ, cùng độ sâu và cùng hàm đánh giá. Các độ sâu mặc định là 1, 2 và 3.

## Ghi chú về tên biến

Tên biến trong code được đặt bằng tiếng Việt không dấu, ví dụ:

- `ban_co`: bàn cờ.
- `do_sau`: độ sâu tìm kiếm.
- `nuoc_di`: nước đi.
- `so_trang_thai_da_xet`: số trạng thái thuật toán đã xét.
- `thuat_toan`: thuật toán đang dùng.
- `danh_gia_ban_co`: hàm đánh giá bàn cờ.

Không dùng dấu tiếng Việt trong định danh để tránh lỗi môi trường khi chạy Python.

## Nội dung đã cài đặt

- Biểu diễn trạng thái bàn cờ bằng mảng hai chiều.
- Sinh nước đi hợp lệ, có giới hạn trong vùng gần các quân đã đánh để giảm số nhánh.
- Kiểm tra thắng/thua/hòa.
- Thuật toán Minimax có giới hạn độ sâu.
- Thuật toán Alpha-Beta pruning.
- Hàm đánh giá trạng thái dựa trên các đoạn 4 ô.
- Đếm số trạng thái đã xét.
- Đo thời gian chạy bằng `perf_counter`.
- Bộ trạng thái kiểm thử mẫu và xuất kết quả thực nghiệm ra CSV.
