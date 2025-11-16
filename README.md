# 📚 Quản Lý Sách

## 🎯 Mục tiêu đồ án

1. **Quản lý sách hiệu quả** 📚  
   - Giúp quản lý sách, độc giả, phiếu mượn/phiếu trả một cách có hệ thống.  
   - Hạn chế nhầm lẫn, mất mát sách và dữ liệu.

2. **Thực hành lập trình GUI với Python** 🖥️  
   - Sử dụng **Tkinter** để xây dựng giao diện thân thiện, dễ sử dụng.  
   - Thực hành các kỹ thuật: TreeView, Dialog, Scrollbar, Button, Entry.

3. **Thực hành quản lý cơ sở dữ liệu SQL** 💾  
   - Kết nối PyCharm với **SQL Server**.  
   - Thực hành CRUD: **Thêm – Sửa – Xóa** dữ liệu trong các bảng.  
   - Áp dụng **quan hệ giữa các bảng** (Sách ↔ Thể loại, Phiếu Mượn ↔ Chi Tiết Phiếu Mượn).

4. **Áp dụng phân quyền người dùng** 🔐  
   - Tạo hệ thống **Admin / Nhân viên**.  
   - Học cách kiểm soát quyền truy cập vào các chức năng khác nhau.

5. **Tích hợp tìm kiếm & thao tác dữ liệu nhanh chóng** 🔎  
   - Giúp người dùng tìm sách, độc giả hoặc phiếu mượn dễ dàng.  
   - Thực hành lập trình thao tác dữ liệu trên TreeView và Dialog.

---

## 🔹 Tính năng

### 1️⃣ Đăng nhập 🔐
- Xác thực người dùng theo `Tên đăng nhập` và `Mật khẩu`.
- Phân quyền:
  - **Admin / Quản trị viên**: Toàn quyền CRUD tất cả các bảng 🏆.
  - **Nhân viên**: Chỉ CRUD các bảng liên quan sách, độc giả, phiếu mượn, chi tiết phiếu mượn, phiếu trả 🛠️.

### 2️⃣ Quản lý Sách 📖
- Thêm, sửa, xóa sách.
- Hiển thị thông tin: Tên sách, Tác giả, Nhà xuất bản, Năm xuất bản, Mã thể loại, Số lượng, Giá tiền 💰.

### 3️⃣ Quản lý Thể loại 🎨
- Thêm, sửa, xóa thể loại sách.

### 4️⃣ Quản lý Độc giả 🧑‍💻
- Thêm, sửa, xóa thông tin độc giả.
- Thông tin: Họ tên, SĐT, Email, Địa chỉ, Loại độc giả 📝.

### 5️⃣ Phiếu Mượn & Chi tiết Phiếu Mượn 📝🔹
- Thêm, sửa, xóa phiếu mượn.
- Quản lý chi tiết phiếu mượn: Mã phiếu mượn, mã sách, số lượng mượn.

### 6️⃣ Phiếu Trả 🎁
- Thêm, sửa, xóa phiếu trả.
- Tính toán tiền phạt nếu cần 💸.

### 7️⃣ Quản lý Tài khoản & Nhân viên 🔑👷
- Admin/Quản trị viên mới có quyền CRUD tài khoản và nhân viên.
- Thông tin tài khoản: Tên đăng nhập, mật khẩu, họ tên, vai trò.

### 8️⃣ Tìm kiếm & Làm mới 🔍✨
- Tìm kiếm sách, thể loại hoặc các bảng khác theo từ khóa.
- Nút "Làm mới" để load lại dữ liệu mới nhất 🔄.

### 9️⃣ Giao diện 🖥️
- **TreeView** hiển thị dữ liệu.
- Dialog riêng cho từng bảng:  
  📖 Book, 🧑‍💻 DocGia, 🔑 TaiKhoan, 👷 NhanVien, 📝 PhieuMuon, 🔹 ChiTietPhieuMuon, 🎁 PhieuTra.
- Scrollbar dọc & ngang tự động.
- Nút thao tác: Thêm ➕, Sửa ✏️, Xóa ❌.

---

## 🗂 Các bảng trong Database (SQL) ✨

| 📌 Tên bảng |
|------------|
| 📖 Sach       |
| 🎨 TheLoai    |
| 🧑‍💻 DocGia     |
| 📝 PhieuMuon  |
| 🔹 ChiTietPhieuMuon |
| 🎁 PhieuTra   |
| 🔑 TaiKhoan   |
| 👷 NhanVien   |

---

## ⚙️ Công nghệ sử dụng
- PyCharm 2025.2.4
- Tkinter 🖥️
- SQL Server Management 20(DB siêu gọn nhẹ) 🗄️

---

## 🚀 Hướng dẫn chạy
1. Tải SQL về máy và download file SQL_QLS.sql của mình nè<3.
2. Tải PyCharm, download hai file main.py và db.py nha.
**3. Kết nối PyCharm với SQL Server:**
   **-Cài thư viện Python trong PyCharm, mở Terminal gõ: pip install pyodbc(import pyodbc trong db.py)**
   **-Hãy tải OBDC Driver ... for SQL Server(sử dụng trong db.py)**
   **-SERVER: nếu server khác, đổi → tên server của cậu(cụ thể là SQL để copy tên server)**
   ***Lưu ý: Qua SQL chạy các bảng trước sau đó qua PyCharm chạy db.py rồi mới qua main.py chạy code, thế là xong nhé.***
# **---THANK YOU FOR READING---**
