# HỆ THỐNG PHÁT HIỆN VÀ BẢO VỆ DỮ LIỆU NHẠY CẢM KHI SỬ DỤNG GENERATIVE AI



## 1. Giới thiệu đề tài



Đề tài nghiên cứu khoa học sinh viên:



**Nghiên cứu và xây dựng hệ thống phát hiện, cảnh báo và bảo vệ dữ liệu nhạy cảm khi sử dụng Generative AI trong môi trường đại học.**



Mục tiêu của dự án là xây dựng hệ thống hỗ trợ phát hiện dữ liệu nhạy cảm trong văn bản, phân tích mức độ rủi ro và che dữ liệu trước khi người dùng gửi nội dung đến các công cụ Generative AI.



Hiện tại, nhóm đã xây dựng được nguyên mẫu xử lý văn bản chạy trên Terminal.



## 2. Các chức năng đã xây dựng



\- Phát hiện dữ liệu nhạy cảm bằng Regex.

\- Nhận diện thực thể tiếng Việt bằng NER (Underthesea).

\- Kết hợp hai phương pháp bằng Hybrid.

\- Phân tích mức độ rủi ro của văn bản.

\- Che dữ liệu nhạy cảm.

\- Đánh giá hiệu quả các phương pháp phát hiện.

\- Kiểm thử các thành phần của hệ thống.



## 3. Danh sách 10 nhãn dữ liệu nhạy cảm



| STT | Nhãn | Ý nghĩa |

|---|---|---|

| 1 | PERSON\_NAME | Họ tên |

| 2 | STUDENT\_ID | Mã sinh viên |

| 3 | EMAIL | Địa chỉ email |

| 4 | NATIONAL\_ID | Số định danh cá nhân |

| 5 | BANK\_ACCOUNT | Số tài khoản ngân hàng |

| 6 | CREDENTIAL | Mật khẩu/thông tin xác thực |

| 7 | SECRET\_KEY | Khóa bí mật/API key |

| 8 | ACADEMIC\_RECORD | Thông tin học tập |

| 9 | ADDRESS | Địa chỉ |

| 10 | PHONE | Số điện thoại |



## 4. Công nghệ sử dụng



\- Python 3.12

\- Underthesea 9.5.0

\- Pytest 9.2.0

\- Regular Expression (Regex)

\- Named Entity Recognition (NER)



## 5. Cấu trúc dự án



```text

GENAI\_DATA\_PROTECTION/

├── data/

│   ├── raw/

│   ├── dataset\_nhay\_cam\_vi.csv

│   ├── dataset\_nhay\_cam\_vi.jsonl

│   ├── dataset\_stats.json

│   └── test\_cases.json

├── src/

│   ├── regex\_detector.py

│   ├── ner\_detector.py

│   ├── hybrid\_detector.py

│   ├── risk\_analyzer.py

│   └── masker.py

├── tests/

│   ├── test\_regex.py

│   ├── test\_ner.py

│   ├── test\_hybrid.py

│   ├── test\_risk\_analyzer.py

│   └── test\_masker.py

├── results/

├── main.py

├── build\_dataset.py

├── evaluate.py

├── inspect\_errors.py

├── inspect\_dev\_errors.py

├── run\_scenarios.py

├── requirements.txt

└── README.md

```



## 6. Cài đặt môi trường



Yêu cầu Python 3.12.



Clone repository:



```bash

git clone <URL\_REPOSITORY>

cd GENAI\_DATA\_PROTECTION

```



Tạo môi trường ảo:



```bash

python -m venv venv

```



Cài đặt thư viện trên Windows PowerShell:



```powershell

.\\venv\\Scripts\\python.exe -m pip install -r requirements.txt

```



## 7. Chạy chương trình



Trên Windows PowerShell:



```powershell

.\\venv\\Scripts\\python.exe main.py

```



Nhập văn bản cần kiểm tra. Hệ thống sẽ thực hiện:



1\. Phát hiện dữ liệu nhạy cảm.

2\. Phân tích mức độ rủi ro.

3\. Che dữ liệu nhạy cảm.

4\. Hiển thị kết quả xử lý.



## 8. Chạy kiểm thử



```powershell

.\\venv\\Scripts\\python.exe -m pytest -q

```



Kết quả gần nhất: **30 bài kiểm thử đạt**.



## 9. Kết quả đánh giá mô hình



Chạy đánh giá bằng lệnh:



```powershell

.\\venv312\\Scripts\\python.exe .\\evaluate.py

```



Kết quả trên tập test tổng hợp gồm 200 mẫu:



| Phương pháp | Precision | Recall | F1-score | Miss rate |

|---|---:|---:|---:|---:|

| Regex | 1.0000 | 0.8000 | 0.8889 | 0.2000 |

| NER | 0.6312 | 0.1978 | 0.3012 | 0.8022 |

| Hybrid | 0.9956 | 0.9978 | 0.9967 | 0.0022 |



Hybrid đạt F1-score cao nhất trong lần đánh giá này.



Lưu ý: Đây là kết quả trên bộ dữ liệu tổng hợp của nhóm, chưa đại diện cho hiệu quả trên dữ liệu thực tế.



Các kết quả được lưu trong thư mục `results/`.



## 10. Dữ liệu nghiên cứu



Bộ dữ liệu hiện tại gồm 1.000 mẫu, được chia thành:



\- Train: 700 mẫu.

\- Dev: 100 mẫu.

\- Test: 200 mẫu.



Dữ liệu được tổng hợp tự động phục vụ nghiên cứu. Nhóm chỉ sử dụng dữ liệu giả lập hoặc đã ẩn danh, không đưa thông tin cá nhân thật của sinh viên và giảng viên lên GitHub.



Lưu ý: Số lượng thực thể trong thống kê dữ liệu hiện tại cần được đối chiếu với báo cáo các tuần trước trước khi chốt số liệu chính thức.



## 11. Phân công công việc tiếp theo



### Thành viên 2: Khảo sát và thử nghiệm mô hình NER tiếng Việt



\- Tìm hiểu và lựa chọn 1–2 mô hình NER tiếng Việt.

\- Thử nghiệm trên tập dữ liệu dev của nhóm.

\- So sánh với Underthesea hiện tại bằng Precision, Recall, F1-score và thời gian xử lý.

\- Bàn giao báo cáo, code thử nghiệm và bảng kết quả.

\- Không tự ý thay đổi code NER chính khi chưa trao đổi.



### Thành viên 3: Tạo bộ kiểm thử độc lập và rà soát nhãn



\- Tự viết bộ câu kiểm thử mới, không sao chép dữ liệu cũ.

\- Gán nhãn theo 10 nhãn hiện tại.

\- Kiểm tra vị trí bắt đầu, kết thúc và tính chính xác của nhãn.

\- Ghi lại các trường hợp khó phân loại hoặc chưa thống nhất.

\- Trao đổi với giảng viên hướng dẫn để xác nhận định dạng mã sinh viên và danh sách 10 nhãn.

\- Bàn giao file dữ liệu và báo cáo rà soát.



### Phần phụ trách của trưởng nhóm



\- Hoàn thiện và quản lý code chính.

\- Kiểm tra kết quả do hai thành viên bàn giao.

\- Tích hợp các mô hình và dữ liệu kiểm thử mới.

\- Kiểm thử tổng thể hệ thống.

\- Tiếp tục hoàn thiện cơ chế cảnh báo và bảo vệ dữ liệu.



## 12. Giới hạn hiện tại và hướng phát triển



Hiện tại:



\- Hệ thống chạy trên Terminal.

\- Chưa tích hợp trực tiếp với dịch vụ Generative AI.

\- Chưa có giao diện Web/API hoàn chỉnh.

\- NER sử dụng Underthesea còn hạn chế về khả năng nhận diện một số thực thể.



Hướng phát triển:



\- Khảo sát thêm các mô hình NER tiếng Việt.

\- Rà soát và mở rộng bộ dữ liệu kiểm thử.

\- Hoàn thiện cơ chế cảnh báo rủi ro.

\- Tích hợp các thành phần thành quy trình thống nhất.

\- Nghiên cứu phát triển giao diện Web/API.



## 13. Nhóm thực hiện



Giảng viên hướng dẫn: ThS. Bùi Văn Tâm.



Sinh viên thực hiện:



\- Nguyễn Viết Trường

\- Keodalavinh Maymalar

\- Taochanxay Souksan


