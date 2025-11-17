import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db import fetch_all, fetch_one, execute
import datetime

def run_app():
    # Tạo một cửa sổ gốc ẩn và hiển thị form đăng nhập dưới dạng Toplevel
    root = tk.Tk()
    root.withdraw()

    def after_login(user_obj):
        root.destroy()
        app = App()
        app.on_login_success(user_obj)
        app.mainloop()

    login = LoginWindow(None, after_login)
    login.mainloop()

# ---------- form dang nhap ----------
class LoginWindow(tk.Toplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.title("Đăng nhập - Quản lý sách")
        self.on_success = on_success
        self.geometry("320x160")
        self.resizable(False, False)

        tk.Label(self, text="Tên đăng nhập").pack(pady=(10, 0))
        self.user_entry = tk.Entry(self)
        self.user_entry.pack(fill="x", padx=20)

        tk.Label(self, text="Mật khẩu").pack(pady=(8, 0))
        self.pw_entry = tk.Entry(self, show="*")
        self.pw_entry.pack(fill="x", padx=20)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        btn_login = tk.Button(btn_frame, text="Đăng nhập", width=12, command=self.try_login)
        btn_login.pack(side="left", padx=5)

        btn_exit = tk.Button(btn_frame, text="Thoát", width=12, command=self.on_exit)
        btn_exit.pack(side="right", padx=5)

    def on_exit(self):
        self.destroy()  # đóng cửa sổ login
        self.master.destroy()  # đóng luôn main Tk chính (thoát chương trình)

    def try_login(self):
        user = self.user_entry.get().strip()
        pw = self.pw_entry.get().strip()
        if not user or not pw:
            messagebox.showwarning("Thiếu thông tin", "Nhập tên đăng nhập và mật khẩu")
            return

        row = fetch_one("SELECT MaTK, TenDangNhap, MatKhau, HoTen, VaiTro, TrangThai FROM TaiKhoan WHERE TenDangNhap = ?", (user,))
        if not row:
            messagebox.showerror("Lỗi", "Không tìm thấy tài khoản")
            return
        db_pw = row[2]
        # DB mẫu lưu mật khẩu dạng văn bản thuần (plain text). Thực tế cần dùng hash để bảo mật.
        if pw != db_pw:
            messagebox.showerror("Lỗi", "Mật khẩu không đúng")
            return
        user_obj = {
            "MaTK": row[0],
            "TenDangNhap": row[1],
            "HoTen": row[3],
            "VaiTro": row[4],
            "TrangThai": row[5]
        }

        self.destroy()
        self.on_success(user_obj)
# ---------- form app ----------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quản lý sách")
        self.state("normal")
        self.geometry("1100x650")

        self.current_user = None
        self.current_table = "Sach"

        self.create_widgets()

    def on_login_success(self, user_obj):
        self.current_user = user_obj
        self.lbl_user.config(text=f"Xin chào, {user_obj['HoTen']} ({user_obj['VaiTro']})")
        self.apply_permissions()
        self.load_table(self.current_table)

    def create_widgets(self):
        left_frame = tk.Frame(self, width=200, bg="#efefef")
        left_frame.pack(side="left", fill="y")

        top_frame = tk.Frame(self)
        top_frame.pack(side="top", fill="x")
        self.lbl_user = tk.Label(top_frame, text="Xin chào,", anchor="w", font=("Arial", 10, "bold"))
        self.lbl_user.pack(side="left", padx=10, pady=8)

        search_frame = tk.Frame(top_frame)
        search_frame.pack(side="right", padx=10)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=(0, 6))
        tk.Button(search_frame, text="Tìm", command=self.search).pack(side="left")
        tk.Button(search_frame, text="Làm mới", command=lambda: self.load_table(self.current_table)).pack(side="left", padx=6)

        # menu buttons
        btns = [
            ("Quản Lý Sách", "Sach"),
            ("Thể Loại", "TheLoai"),
            ("Quản Lý Độc Giả", "DocGia"),
            ("Phiếu Mượn", "PhieuMuon"),
            ("Chi Tiết Phiếu Mượn", "ChiTietPhieuMuon"),
            ("Phiếu Trả", "PhieuTra"),
            ("Tài Khoản", "TaiKhoan"),
            ("Nhân Viên", "NhanVien"),
        ]
        self.menu_buttons = {}
        for (text, tbl) in btns:
            b = tk.Button(left_frame, text=text, width=18, anchor="w", command=lambda t=tbl: self.load_table(t))
            b.pack(pady=6, padx=10)
            self.menu_buttons[tbl] = b

        tk.Button(left_frame, text="Đăng xuất", width=18, command=self.logout).pack(side="bottom", pady=6)
        tk.Button(left_frame, text="Thoát", width=18, command=self.quit).pack(side="bottom", pady=(0, 20))

        # center
        center = tk.Frame(self)
        center.pack(side="right", expand=True, fill="both")

        tool_frame = tk.Frame(center)
        tool_frame.pack(fill="x", padx=6, pady=(6, 0))
        tk.Button(tool_frame, text="Xóa", command=self.delete_row).pack(side="right", padx=6)
        tk.Button(tool_frame, text="Sửa", command=self.edit_row).pack(side="right", padx=6)
        tk.Button(tool_frame, text="Thêm", command=self.add_row).pack(side="right", padx=6)

        # Treeview + scrollbars
        tv_frame = tk.Frame(center)
        tv_frame.pack(expand=True, fill="both", padx=6, pady=6)

        self.tree = ttk.Treeview(tv_frame, show="headings")
        self.vsb = ttk.Scrollbar(tv_frame, orient="vertical", command=self.tree.yview)
        self.hsb = ttk.Scrollbar(tv_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.vsb.pack(side="right", fill="y")
        self.hsb.pack(side="bottom", fill="x")
        self.tree.pack(expand=True, fill="both", side="left")

        # Khi người dùng click vào 1 dòng, đảm bảo rằng dòng đó được chọn
        self.tree.bind("<ButtonRelease-1>", lambda e: None)
        self.tree.bind("<Double-1>", lambda e: self.edit_row())

    def apply_permissions(self):
        role = (self.current_user["VaiTro"] if self.current_user else "NhanVien").lower()
        # admin/qtv có thẩm quyền
        if role in ("admin", "qtv"):
            for b in self.menu_buttons.values():
                b.config(state="normal")
        else:
            # nhân viên chỉ được: DocGia, PhieuMuon, ChiTietPhieuMuon, PhieuTra, Sach
            allowed = {"docgia", "phieumuon", "chitietphieumuon", "phieutra", "sach"}
            for name, btn in self.menu_buttons.items():
                btn.config(state="normal" if name.lower() in allowed else "disabled")

    def search(self):
        q = self.search_entry.get().strip()
        if not q:
            self.load_table(self.current_table)
            return
        # Tìm kiếm đơn giản: chỉ tìm trong các cột dạng văn bản của bảng hiện tại
        try:
            if self.current_table == "Sach":
                sql = "SELECT MaSach, TenSach, TacGia, NhaXuatBan, NamXuatBan, MaTheLoai, SoLuong, GiaTien FROM Sach WHERE TenSach LIKE ?"
                cols, rows = fetch_all(sql, (f"%{q}%",))
                self.display_result(cols, rows)
            elif self.current_table == "TheLoai":
                sql = "SELECT MaTheLoai, TenTheLoai FROM TheLoai WHERE TenTheLoai LIKE ?"
                cols, rows = fetch_all(sql, (f"%{q}%",))
                self.display_result(cols, rows)
            else:
                cols, rows = fetch_all(f"SELECT * FROM {self.current_table}")
                filtered = [r for r in rows if any(q.lower() in str(x).lower() for x in r)]
                self.display_result(cols, filtered)
        except Exception as e:
            messagebox.showerror("Lỗi tìm kiếm", str(e))

    def load_table(self, table_name):
        self.current_table = table_name
        try:
            if table_name == "Sach":
                sql = "SELECT MaSach, TenSach, TacGia, NhaXuatBan, NamXuatBan, MaTheLoai, SoLuong, GiaTien FROM Sach"
                cols, rows = fetch_all(sql)
            elif table_name == "TheLoai":
                sql = "SELECT MaTheLoai, TenTheLoai FROM TheLoai"
                cols, rows = fetch_all(sql)
            elif table_name == "DocGia":
                sql = "SELECT MaDocGia, HoTen, SDT, Email, DiaChi, LoaiDocGia, NgayDangKy FROM DocGia"
                cols, rows = fetch_all(sql)
            elif table_name == "PhieuMuon":
                sql = "SELECT MaPhieuMuon, MaDocGia, NgayMuon, HanTra, TrangThai FROM PhieuMuon"
                cols, rows = fetch_all(sql)
            elif table_name == "ChiTietPhieuMuon":
                sql = "SELECT MaPhieuMuon, MaSach, SoLuong FROM ChiTietPhieuMuon"
                cols, rows = fetch_all(sql)
            elif table_name == "PhieuTra":
                sql = "SELECT MaPhieuTra, MaPhieuMuon, NgayTra, TienPhat FROM PhieuTra"
                cols, rows = fetch_all(sql)
            elif table_name == "TaiKhoan":
                sql = "SELECT MaTK, TenDangNhap, MatKhau, HoTen, VaiTro, TrangThai FROM TaiKhoan"
                cols, rows = fetch_all(sql)
            elif table_name == "NhanVien":
                sql = "SELECT MaNV, MaTK, HoTen, SDT, DiaChi FROM NhanVien"
                cols, rows = fetch_all(sql)
            else:
                cols, rows = fetch_all(f"SELECT * FROM {table_name}")
        except Exception as e:
            messagebox.showerror("Lỗi load", str(e))
            return
        self.display_result(cols, rows)

    def display_result(self, cols, rows):
        # Xóa toàn bộ dữ liệu cũ trong Treeview trước khi hiển thị dữ liệu mới
        for c in self.tree.get_children():
            self.tree.delete(c)
        self.tree["columns"] = cols
        # Thiết lập tiêu đề cột
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="w")
        # insert rows
        for r in rows:
            # Chuyển các giá trị ngày/thời gian thành chuỗi để hiển thị
            vals = []
            for v in r:
                if isinstance(v, (datetime.date, datetime.datetime)):
                    vals.append(str(v))
                else:
                    vals.append("" if v is None else str(v))
            self.tree.insert("", "end", values=vals)

    def add_row(self):
        t = self.current_table
        if t == "TheLoai":
            name = simpledialog.askstring("Thêm Thể loại", "Tên thể loại:")
            if name:
                execute("INSERT INTO TheLoai (TenTheLoai) VALUES (?)", (name.strip(),))
                self.load_table(t)
        elif t == "Sach":
            dlg = SmallBookDialog(self)
            self.wait_window(dlg)
            if dlg.result:
                TenSach, TacGia, NhaXB, NamXB, MaTheLoai, SoLuong, GiaTien = dlg.result
                execute("INSERT INTO Sach (TenSach, TacGia, NhaXuatBan, NamXuatBan, MaTheLoai, SoLuong, GiaTien) VALUES (?,?,?,?,?,?,?)",
                        (TenSach, TacGia, NhaXB, NamXB, MaTheLoai, SoLuong, GiaTien))
                self.load_table(t)
        elif t == "DocGia":
            dlg = SmallDocGiaDialog(self)
            self.wait_window(dlg)
            if dlg.result:
                HoTen, SDT, Email, DiaChi, LoaiDocGia = dlg.result
                execute("INSERT INTO DocGia (HoTen, SDT, Email, DiaChi, LoaiDocGia) VALUES (?,?,?,?,?)",
                        (HoTen, SDT, Email, DiaChi, LoaiDocGia))
                self.load_table(t)
        elif t == "PhieuMuon":
            dlg = SmallPhieuMuonDialog(self)
            self.wait_window(dlg)
            if dlg.result:
                MaDocGia, NgayMuon, HanTra, TrangThai = dlg.result
                # Giả sử MaPhieuMuon tự tăng, chèn các thông tin còn lại
                execute("INSERT INTO PhieuMuon (MaDocGia, NgayMuon, HanTra, TrangThai) VALUES (?,?,?,?)",
                        (MaDocGia, NgayMuon or None, HanTra or None, TrangThai or None))
                self.load_table(t)
        elif t == "ChiTietPhieuMuon":
            dlg = SmallChiTietPMDialog(self)
            self.wait_window(dlg)
            if dlg.result:
                MaPhieuMuon, MaSach, SoLuong = dlg.result
                execute("INSERT INTO ChiTietPhieuMuon (MaPhieuMuon, MaSach, SoLuong) VALUES (?,?,?)",
                        (MaPhieuMuon, MaSach, SoLuong))
                self.load_table(t)
        elif t == "PhieuTra":
            dlg = SmallPhieuTraDialog(self)
            self.wait_window(dlg)
            if dlg.result:
                MaPhieuMuon, NgayTra, TienPhat = dlg.result
                # assume MaPhieuTra auto-increment
                execute("INSERT INTO PhieuTra (MaPhieuMuon, NgayTra, TienPhat) VALUES (?,?,?)",
                        (MaPhieuMuon, NgayTra or None, TienPhat or 0))
                self.load_table(t)
        elif t == "TaiKhoan":
            if self.current_user["VaiTro"].lower() not in ("admin", "qtv"):
                messagebox.showwarning("Quyền", "Chỉ admin/qtv mới thêm tài khoản")
                return
            dlg = SmallTaiKhoanDialog(self)
            self.wait_window(dlg)
            if dlg.result:
                TenDangNhap, MatKhau, HoTen, VaiTro = dlg.result
                execute("INSERT INTO TaiKhoan (TenDangNhap, MatKhau, HoTen, VaiTro) VALUES (?,?,?,?)",
                        (TenDangNhap, MatKhau, HoTen, VaiTro))
                self.load_table(t)
        elif t == "NhanVien":
            if self.current_user["VaiTro"].lower() not in ("admin", "qtv"):
                messagebox.showwarning("Quyền", "Chỉ admin/qtv mới thêm nhân viên")
                return
            dlg = SmallNhanVienDialog(self)
            self.wait_window(dlg)
            if dlg.result:
                MaTK, HoTen, SDT, DiaChi = dlg.result
                execute("INSERT INTO NhanVien (MaTK, HoTen, SDT, DiaChi) VALUES (?,?,?,?)",
                        (MaTK, HoTen, SDT, DiaChi))
                self.load_table(t)
        else:
            messagebox.showinfo("TODO", f"Thêm cho bảng {t} chưa được hiện thực đầy đủ. Mình có thể mở rộng theo yêu cầu :)")

    def get_selected_values(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Chọn bản ghi", "Chọn 1 bản ghi trước")
            return None
        vals = self.tree.item(sel[0])["values"]
        return vals

    def edit_row(self):
        t = self.current_table
        vals = self.get_selected_values()
        if not vals:
            return
        try:
            if t == "TheLoai":
                id_ = vals[0]
                old = vals[1]
                new = simpledialog.askstring("Sửa Thể loại", "Tên thể loại:", initialvalue=old)
                if new:
                    execute("UPDATE TheLoai SET TenTheLoai=? WHERE MaTheLoai=?", (new.strip(), id_))
                    self.load_table(t)

            elif t == "Sach":
                id_ = vals[0]
                dlg = SmallBookDialog(self, initial=vals)
                self.wait_window(dlg)
                if dlg.result:
                    TenSach, TacGia, NhaXB, NamXB, MaTheLoai, SoLuong, GiaTien = dlg.result
                    execute("UPDATE Sach SET TenSach=?, TacGia=?, NhaXuatBan=?, NamXuatBan=?, MaTheLoai=?, SoLuong=?, GiaTien=? WHERE MaSach=?",
                            (TenSach, TacGia, NhaXB, NamXB, MaTheLoai, SoLuong, GiaTien, id_))
                    self.load_table(t)

            elif t == "DocGia":
                id_ = vals[0]
                dlg = SmallDocGiaDialog(self, initial=vals)
                self.wait_window(dlg)
                if dlg.result:
                    HoTen, SDT, Email, DiaChi, LoaiDocGia = dlg.result
                    execute("UPDATE DocGia SET HoTen=?, SDT=?, Email=?, DiaChi=?, LoaiDocGia=? WHERE MaDocGia=?",
                            (HoTen, SDT, Email, DiaChi, LoaiDocGia, id_))
                    self.load_table(t)

            elif t == "PhieuMuon":
                # vals: MaPhieuMuon, MaDocGia, NgayMuon, HanTra, TrangThai
                original_mapm = vals[0]
                dlg = SmallPhieuMuonDialog(self, initial=vals)
                self.wait_window(dlg)
                if dlg.result:
                    MaDocGia, NgayMuon, HanTra, TrangThai = dlg.result
                    execute("UPDATE PhieuMuon SET MaDocGia=?, NgayMuon=?, HanTra=?, TrangThai=? WHERE MaPhieuMuon=?",
                            (MaDocGia, NgayMuon or None, HanTra or None, TrangThai or None, original_mapm))
                    self.load_table(t)

            elif t == "ChiTietPhieuMuon":
                # vals: MaPhieuMuon, MaSach, SoLuong
                orig_mapm = vals[0]
                orig_masach = vals[1]
                dlg = SmallChiTietPMDialog(self, initial=vals)
                self.wait_window(dlg)
                if dlg.result:
                    MaPhieuMuon_new, MaSach_new, SoLuong_new = dlg.result
                    execute("UPDATE ChiTietPhieuMuon SET MaPhieuMuon=?, MaSach=?, SoLuong=? WHERE MaPhieuMuon=? AND MaSach=?",
                            (MaPhieuMuon_new, MaSach_new, SoLuong_new, orig_mapm, orig_masach))
                    self.load_table(t)

            elif t == "PhieuTra":
                # vals: MaPhieuTra, MaPhieuMuon, NgayTra, TienPhat
                original_mapt = vals[0]
                dlg = SmallPhieuTraDialog(self, initial=vals)
                self.wait_window(dlg)
                if dlg.result:
                    MaPhieuMuon_new, NgayTra, TienPhat = dlg.result
                    execute("UPDATE PhieuTra SET MaPhieuMuon=?, NgayTra=?, TienPhat=? WHERE MaPhieuTra=?",
                            (MaPhieuMuon_new, NgayTra or None, TienPhat or 0, original_mapt))
                    self.load_table(t)

            elif t == "TaiKhoan":
                if self.current_user["VaiTro"].lower() not in ("admin", "qtv"):
                    messagebox.showwarning("Quyền", "Chỉ admin/qtv mới sửa tài khoản")
                    return
                id_ = vals[0]
                dlg = SmallTaiKhoanDialog(self, initial=vals)
                self.wait_window(dlg)
                if dlg.result:
                    TenDangNhap, MatKhau, HoTen, VaiTro = dlg.result
                    execute("UPDATE TaiKhoan SET TenDangNhap=?, MatKhau=?, HoTen=?, VaiTro=? WHERE MaTK=?",
                            (TenDangNhap, MatKhau, HoTen, VaiTro, id_))
                    self.load_table(t)

            elif t == "NhanVien":
                if self.current_user["VaiTro"].lower() not in ("admin", "qtv"):
                    messagebox.showwarning("Quyền", "Chỉ admin/qtv mới sửa nhân viên")
                    return
                id_ = vals[0]
                dlg = SmallNhanVienDialog(self, initial=vals)
                self.wait_window(dlg)
                if dlg.result:
                    MaTK, HoTen, SDT, DiaChi = dlg.result
                    execute("UPDATE NhanVien SET MaTK=?, HoTen=?, SDT=?, DiaChi=? WHERE MaNV=?",
                            (MaTK, HoTen, SDT, DiaChi, id_))
                    self.load_table(t)

            else:
                messagebox.showinfo("TODO", f"Sửa cho bảng {t} chưa được hiện thực đầy đủ.")
        except Exception as e:
            messagebox.showerror("Lỗi sửa", str(e))

    def delete_row(self):
        t = self.current_table
        vals = self.get_selected_values()
        if not vals:
            return
        id_ = vals[0]
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa bản ghi {id_} ở bảng {t}?"):
            try:
                pk_map = {
                    "TheLoai": ("MaTheLoai",),
                    "Sach": ("MaSach",),
                    "DocGia": ("MaDocGia",),
                    "PhieuMuon": ("MaPhieuMuon",),
                    "ChiTietPhieuMuon": ("MaPhieuMuon", "MaSach"),
                    "PhieuTra": ("MaPhieuTra",),
                    "TaiKhoan": ("MaTK",),
                    "NhanVien": ("MaNV",)
                }
                if t not in pk_map:
                    messagebox.showerror("Không hỗ trợ", "Xóa cho bảng này chưa hỗ trợ tự động")
                    return
                pks = pk_map[t]
                if len(pks) == 1:
                    sql = f"DELETE FROM {t} WHERE {pks[0]} = ?"
                    execute(sql, (id_,))
                else:
                    keyvals = tuple(vals[:len(pks)])
                    where = " AND ".join([f"{k} = ?" for k in pks])
                    sql = f"DELETE FROM {t} WHERE {where}"
                    execute(sql, keyvals)
                self.load_table(t)
            except Exception as e:
                messagebox.showerror("Lỗi xóa", str(e))

    def logout(self):
        self.destroy()
        import main
        main.run_app()

class SmallBookDialog(tk.Toplevel):
    def __init__(self, parent, initial=None):
        super().__init__(parent)
        self.title("Book")
        self.result = None
        self.geometry("420x300")
        labels = ["TenSach", "TacGia", "NhaXuatBan", "NamXuatBan", "MaTheLoai", "SoLuong", "GiaTien"]
        labels_vn = ["Tên Sách", "Tác Giả", "Nhà Xuất Bản", "Năm Xuất Bản", "Mã Thể Loại", "Số Lượng", "Giá Tiền"]
        self.vars = {}
        for i, lab in enumerate(labels):
            tk.Label(self, text=labels_vn[i]).place(x=10, y=10 + i * 34)
            e = tk.Entry(self, width=40)
            e.place(x=140, y=10 + i * 34)
            self.vars[lab] = e
        if initial:
            # Thứ tự ban đầu: MaSach, TenSach, TacGia, NhaXuatBan, NamXuatBan, MaTheLoai, SoLuong, GiaTien
            try:
                _, ten, tacgia, nhaxb, nam, matl, sl, gia = initial
            except Exception:
                ten = tacgia = nhaxb = nam = matl = sl = gia = ""
            self.vars["TenSach"].insert(0, ten)
            self.vars["TacGia"].insert(0, tacgia)
            self.vars["NhaXuatBan"].insert(0, nhaxb)
            self.vars["NamXuatBan"].insert(0, nam)
            self.vars["MaTheLoai"].insert(0, matl)
            self.vars["SoLuong"].insert(0, sl)
            self.vars["GiaTien"].insert(0, gia)
        tk.Button(self, text="OK", command=self.on_ok).place(x=200, y=260)

    def on_ok(self):
        try:
            TenSach = self.vars["TenSach"].get().strip()
            TacGia = self.vars["TacGia"].get().strip()
            NhaXB = self.vars["NhaXuatBan"].get().strip()
            NamXB = int(self.vars["NamXuatBan"].get() or 0)
            MaTheLoai = int(self.vars["MaTheLoai"].get() or 1)
            SoLuong = int(self.vars["SoLuong"].get() or 0)
            GiaTien = float(self.vars["GiaTien"].get() or 0)
        except Exception as e:
            messagebox.showerror("Lỗi dữ liệu", "Kiểm tra lại dữ liệu nhập: " + str(e))
            return
        self.result = (TenSach, TacGia, NhaXB, NamXB, MaTheLoai, SoLuong, GiaTien)
        self.destroy()

class SmallDocGiaDialog(tk.Toplevel):
    def __init__(self, parent, initial=None):
        super().__init__(parent)
        self.title("DocGia")
        self.geometry("420x260")
        self.result = None
        labs = [("HoTen", "Họ Tên"), ("SDT", "SĐT"), ("Email", "Email"), ("DiaChi", "Địa Chỉ"), ("LoaiDocGia", "Loại Độc Giả")]
        self.entries = {}
        for i, (key, label_text) in enumerate(labs):
            tk.Label(self, text=label_text).place(x=10, y=10 + i * 40)
            e = tk.Entry(self, width=45)
            e.place(x=120, y=10 + i * 40)
            self.entries[key] = e
        if initial:
            # Kết quả SELECT ban đầu: MaDocGia, HoTen, SDT, Email, DiaChi, LoaiDocGia, NgayDangKy
            try:
                _, Hoten, sdt, email, diachi, loai, _ = initial
            except Exception:
                Hoten = sdt = email = diachi = loai = ""
            self.entries["HoTen"].insert(0, Hoten)
            self.entries["SDT"].insert(0, sdt)
            self.entries["Email"].insert(0, email)
            self.entries["DiaChi"].insert(0, diachi)
            self.entries["LoaiDocGia"].insert(0, loai)
        tk.Button(self, text="OK", command=self.on_ok).place(x=200, y=230)

    def on_ok(self):
        HoTen = self.entries["HoTen"].get().strip()
        SDT = self.entries["SDT"].get().strip()
        Email = self.entries["Email"].get().strip()
        DiaChi = self.entries["DiaChi"].get().strip()
        Loai = self.entries["LoaiDocGia"].get().strip()
        if not HoTen:
            messagebox.showerror("Lỗi", "Tên không được bỏ trống")
            return
        self.result = (HoTen, SDT, Email, DiaChi, Loai)
        self.destroy()

class SmallTaiKhoanDialog(tk.Toplevel):
    def __init__(self, parent, initial=None):
        super().__init__(parent)
        self.title("TaiKhoan")
        self.geometry("420x220")
        self.result = None
        labels = [("TenDangNhap", "Tên Đăng Nhập"), ("MatKhau", "Mật Khẩu"), ("HoTen", "Họ Tên"), ("VaiTro", "Vai Trò")]
        self.entries = {}
        for i, (key, label_text) in enumerate(labels):
            tk.Label(self, text=label_text).place(x=10, y=10 + i * 40)
            e = tk.Entry(self, width=40)
            e.place(x=140, y=10 + i * 40)
            self.entries[key] = e
        if initial:
            # Kết quả SELECT ban đầu: MaTK, TenDangNhap, MatKhau, HoTen, VaiTro, TrangThai
            try:
                _, ten, pw, hoten, vai, _ = initial
            except Exception:
                ten = pw = hoten = vai = ""
            self.entries["TenDangNhap"].insert(0, ten)
            self.entries["MatKhau"].insert(0, pw)
            self.entries["HoTen"].insert(0, hoten)
            self.entries["VaiTro"].insert(0, vai)
        tk.Button(self, text="OK", command=self.on_ok).place(x=200, y=180)

    def on_ok(self):
        TenDangNhap = self.entries["TenDangNhap"].get().strip()
        MatKhau = self.entries["MatKhau"].get().strip()
        HoTen = self.entries["HoTen"].get().strip()
        VaiTro = self.entries["VaiTro"].get().strip() or "NhanVien"
        if not (TenDangNhap and MatKhau and HoTen):
            messagebox.showerror("Lỗi", "Điền đầy đủ thông tin")
            return
        self.result = (TenDangNhap, MatKhau, HoTen, VaiTro)
        self.destroy()

class SmallNhanVienDialog(tk.Toplevel):
    def __init__(self, parent, initial=None):
        super().__init__(parent)
        self.title("NhanVien")
        self.geometry("420x220")
        self.result = None
        labels = [("MaTK", "Mã Tài Khoản"), ("HoTen", "Họ Tên"), ("SDT", "SĐT"), ("DiaChi", "Địa Chỉ")]
        self.entries = {}
        for i, (key, label_text) in enumerate(labels):
            tk.Label(self, text=label_text).place(x=10, y=10 + i * 40)
            e = tk.Entry(self, width=40)
            e.place(x=140, y=10 + i * 40)
            self.entries[key] = e
        if initial:
            # Kết quả SELECT: MaNV, MaTK, HoTen, SDT, DiaChi
            try:
                _, matk, hoten, sdt, diachi = initial
            except Exception:
                matk = hoten = sdt = diachi = ""
            self.entries["MaTK"].insert(0, matk)
            self.entries["HoTen"].insert(0, hoten)
            self.entries["SDT"].insert(0, sdt)
            self.entries["DiaChi"].insert(0, diachi)
        tk.Button(self, text="OK", command=self.on_ok).place(x=200, y=180)

    def on_ok(self):
        try:
            MaTK = int(self.entries["MaTK"].get())
        except Exception:
            messagebox.showerror("Lỗi", "Mã Tài Khoản phải là số (Mã Tài Khoản phải tồn tại trong Tài Khoản)")
            return
        HoTen = self.entries["HoTen"].get().strip()
        SDT = self.entries["SDT"].get().strip()
        DiaChi = self.entries["DiaChi"].get().strip()
        if not HoTen:
            messagebox.showerror("Lỗi", "Họ Tên không được rỗng")
            return
        self.result = (MaTK, HoTen, SDT, DiaChi)
        self.destroy()

# ---------- Các dialog MỚI cho PhieuMuon / ChiTietPhieuMuon / PhieuTra ----------
class SmallPhieuMuonDialog(tk.Toplevel):
    def __init__(self, parent, initial=None):
        super().__init__(parent)
        self.title("Phiếu Mượn")
        self.geometry("360x220")
        self.result = None
        labels = [("MaDocGia", "Mã Độc Giả"), ("NgayMuon", "Ngày Mượn (YYYY-MM-DD)"),
                  ("HanTra", "Hạn Trả (YYYY-MM-DD)"), ("TrangThai", "Trạng Thái")]
        self.entries = {}
        for i, (key, lbl) in enumerate(labels):
            tk.Label(self, text=lbl).place(x=10, y=10 + i*40)
            e = tk.Entry(self, width=30)
            e.place(x=140, y=10 + i*40)
            self.entries[key] = e

        if initial:
            # Giá trị ban đầu: MaPhieuMuon, MaDocGia, NgayMuon, HanTra, TrangThai
            try:
                _, madg, ngaymuon, hantra, trangthai = initial
            except Exception:
                madg = ngaymuon = hantra = trangthai = ""
            self.entries["MaDocGia"].insert(0, madg)
            self.entries["NgayMuon"].insert(0, ngaymuon)
            self.entries["HanTra"].insert(0, hantra)
            self.entries["TrangThai"].insert(0, trangthai)

        tk.Button(self, text="OK", command=self.on_ok).place(x=150, y=180)

    def on_ok(self):
        MaDocGia = self.entries["MaDocGia"].get().strip()
        NgayMuon = self.entries["NgayMuon"].get().strip()
        HanTra = self.entries["HanTra"].get().strip()
        TrangThai = self.entries["TrangThai"].get().strip()
        # Kiểm tra tối thiểu: Mã độc giả bắt buộc phải có
        if not MaDocGia:
            messagebox.showerror("Lỗi", "Mã độc giả không được bỏ trống")
            return
        self.result = (MaDocGia, NgayMuon, HanTra, TrangThai)
        self.destroy()

class SmallChiTietPMDialog(tk.Toplevel):
    def __init__(self, parent, initial=None):
        super().__init__(parent)
        self.title("Chi Tiết Phiếu Mượn")
        self.geometry("360x180")
        self.result = None
        # Các trường dữ liệu: MaPhieuMuon, MaSach, SoLuong
        labels = [("MaPhieuMuon", "Mã Phiếu Mượn"), ("MaSach", "Mã Sách"), ("SoLuong", "Số Lượng")]
        self.entries = {}
        for i, (key, lbl) in enumerate(labels):
            tk.Label(self, text=lbl).place(x=10, y=10 + i*40)
            e = tk.Entry(self, width=30)
            e.place(x=140, y=10 + i*40)
            self.entries[key] = e

        if initial:
            try:
                mapm, masach, soluong = initial
            except Exception:
                mapm = masach = soluong = ""
            self.entries["MaPhieuMuon"].insert(0, mapm)
            self.entries["MaSach"].insert(0, masach)
            self.entries["SoLuong"].insert(0, soluong)

        tk.Button(self, text="OK", command=self.on_ok).place(x=150, y=140)

    def on_ok(self):
        MaPhieuMuon = self.entries["MaPhieuMuon"].get().strip()
        MaSach = self.entries["MaSach"].get().strip()
        SoLuong = self.entries["SoLuong"].get().strip()
        if not (MaPhieuMuon and MaSach):
            messagebox.showerror("Lỗi", "Mã Phiếu Mượn và Mã Sách không được bỏ trống")
            return
        # Thử chuyển Số Lượng thành kiểu số
        try:
            SoLuong_int = int(SoLuong or 0)
        except:
            messagebox.showerror("Lỗi", "Số lượng phải là số")
            return
        self.result = (MaPhieuMuon, MaSach, SoLuong_int)
        self.destroy()

class SmallPhieuTraDialog(tk.Toplevel):
    def __init__(self, parent, initial=None):
        super().__init__(parent)
        self.title("Phiếu Trả")
        self.geometry("360x200")
        self.result = None
        # Các trường dữ liệu: MaPhieuMuon, NgayTra, TienPhat
        labels = [("MaPhieuMuon", "Mã Phiếu Mượn"), ("NgayTra", "Ngày Trả (YYYY-MM-DD)"), ("TienPhat", "Tiền Phạt")]
        self.entries = {}
        for i, (key, lbl) in enumerate(labels):
            tk.Label(self, text=lbl).place(x=10, y=10 + i*40)
            e = tk.Entry(self, width=30)
            e.place(x=140, y=10 + i*40)
            self.entries[key] = e

        if initial:
            try:
                _, mapm, ngaytra, tienphat = initial
            except Exception:
                mapm = ngaytra = tienphat = ""
            self.entries["MaPhieuMuon"].insert(0, mapm)
            self.entries["NgayTra"].insert(0, ngaytra)
            self.entries["TienPhat"].insert(0, tienphat)

        tk.Button(self, text="OK", command=self.on_ok).place(x=150, y=160)

    def on_ok(self):
        MaPhieuMuon = self.entries["MaPhieuMuon"].get().strip()
        NgayTra = self.entries["NgayTra"].get().strip()
        TienPhat = self.entries["TienPhat"].get().strip() or "0"
        try:
            TienPhat_f = float(TienPhat)
        except:
            messagebox.showerror("Lỗi", "Tiền phạt không hợp lệ")
            return
        if not MaPhieuMuon:
            messagebox.showerror("Lỗi", "Mã Phiếu Mượn không được bỏ trống")
            return
        self.result = (MaPhieuMuon, NgayTra, TienPhat_f)
        self.destroy()

if __name__ == "__main__":
    run_app()
