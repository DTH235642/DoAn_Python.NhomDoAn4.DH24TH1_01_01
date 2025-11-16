CREATE DATABASE QuanLySach;
GO

USE QuanLySach;
GO

CREATE TABLE TaiKhoan (
    MaTK INT IDENTITY(1,1) PRIMARY KEY,
    TenDangNhap NVARCHAR(50) NOT NULL UNIQUE,
    MatKhau NVARCHAR(200) NOT NULL,
    HoTen NVARCHAR(100) NOT NULL,
    VaiTro NVARCHAR(20) NOT NULL DEFAULT N'NhanVien',
    TrangThai NVARCHAR(20) NOT NULL DEFAULT N'Hoạt động'
);

CREATE TABLE TheLoai (
    MaTheLoai INT IDENTITY(1,1) PRIMARY KEY,
    TenTheLoai NVARCHAR(100) NOT NULL
);

CREATE TABLE Sach (
    MaSach INT IDENTITY(1,1) PRIMARY KEY,
    TenSach NVARCHAR(200) NOT NULL,
    TacGia NVARCHAR(100),
    NhaXuatBan NVARCHAR(100),
    NamXuatBan INT,
    MaTheLoai INT NOT NULL,
    SoLuong INT NOT NULL DEFAULT 0,
    GiaTien DECIMAL(18,2) NOT NULL DEFAULT 0,

    FOREIGN KEY (MaTheLoai) REFERENCES TheLoai(MaTheLoai)
);

CREATE TABLE DocGia (
    MaDocGia INT IDENTITY(1,1) PRIMARY KEY,
    HoTen NVARCHAR(100) NOT NULL,
    SDT NVARCHAR(20),
    Email NVARCHAR(100),
    DiaChi NVARCHAR(200),
    LoaiDocGia NVARCHAR(50),
    NgayDangKy DATE NOT NULL DEFAULT GETDATE()
);

CREATE TABLE PhieuMuon (
    MaPhieuMuon INT IDENTITY(1,1) PRIMARY KEY,
    MaDocGia INT NOT NULL,
    NgayMuon DATE NOT NULL DEFAULT GETDATE(),
    HanTra DATE NOT NULL,
    TrangThai NVARCHAR(20) NOT NULL DEFAULT N'Đang mượn',

    FOREIGN KEY (MaDocGia) REFERENCES DocGia(MaDocGia)
);

CREATE TABLE ChiTietPhieuMuon (
    MaPhieuMuon INT NOT NULL,
    MaSach INT NOT NULL,
    SoLuong INT NOT NULL DEFAULT 1,

    PRIMARY KEY (MaPhieuMuon, MaSach),

    FOREIGN KEY (MaPhieuMuon) REFERENCES PhieuMuon(MaPhieuMuon),
    FOREIGN KEY (MaSach) REFERENCES Sach(MaSach)
);

CREATE TABLE PhieuTra (
    MaPhieuTra INT IDENTITY(1,1) PRIMARY KEY,
    MaPhieuMuon INT NOT NULL UNIQUE, -- 1 phiếu mượn chỉ trả 1 lần
    NgayTra DATE NOT NULL DEFAULT GETDATE(),
    TienPhat DECIMAL(18,2) DEFAULT 0,

    FOREIGN KEY (MaPhieuMuon) REFERENCES PhieuMuon(MaPhieuMuon)
);

CREATE TABLE NhanVien (
    MaNV INT IDENTITY(1,1) PRIMARY KEY,
    MaTK INT NOT NULL UNIQUE,      -- mỗi nhân viên 1 tài khoản
    HoTen NVARCHAR(100) NOT NULL,
    SDT NVARCHAR(20),
    DiaChi NVARCHAR(200),

    FOREIGN KEY (MaTK) REFERENCES TaiKhoan(MaTK)
);

INSERT INTO TheLoai (TenTheLoai)
VALUES
(N'Khoa học'),
(N'Lập trình'),
(N'Tiểu thuyết'),
(N'Kinh tế'),
(N'Tâm lý'),
(N'Thể thao');

INSERT INTO Sach (TenSach, TacGia, NhaXuatBan, NamXuatBan, MaTheLoai, SoLuong, GiaTien)
VALUES
(N'Sapiens: Lược sử loài người', N'Yuval Noah Harari', N'Trí Thức', 2014, 1, 10, 180000),
(N'Clean Code', N'Robert C. Martin', N'Pearson', 2008, 2, 7, 250000),
(N'Cuộc đời của Pi', N'Yann Martel', N'NXB Trẻ', 2001, 3, 12, 95000),
(N'Đắc Nhân Tâm', N'Dale Carnegie', N'NXB Tổng Hợp', 1936, 4, 20, 90000),
(N'Tâm lý học hành vi', N'John B. Watson', N'Oxford', 1924, 5, 6, 120000),
(N'Bóng đá – Tư duy chiến thuật', N'Pep Guardiola', N'SportBook', 2020, 6, 8, 150000);

INSERT INTO DocGia (HoTen, SDT, Email, DiaChi, LoaiDocGia)
VALUES
(N'Lê Hoàng Nam', '0901234567', 'nam@gmail.com', N'Quận 1, TP.HCM', N'Sinh viên'),
(N'Võ Thị Bích Ngọc', '0907654321', 'ngoc@gmail.com', N'Quận 5, TP.HCM', N'Giáo viên'),
(N'Nguyễn Minh Trí', '0912345678', 'tri@gmail.com', N'Bình Thạnh, TP.HCM', N'Sinh viên');

INSERT INTO PhieuMuon (MaDocGia, NgayMuon, HanTra, TrangThai)
VALUES
(1, '2024-10-01', '2024-10-15', N'Đang mượn'),
(2, '2024-10-05', '2024-10-20', N'Đang mượn'),
(3, '2024-10-10', '2024-10-25', N'Đang mượn');

INSERT INTO ChiTietPhieuMuon (MaPhieuMuon, MaSach, SoLuong)
VALUES
(1, 1, 1),
(1, 4, 1),

(2, 2, 1),

(3, 3, 1),
(3, 5, 1);

INSERT INTO PhieuTra (MaPhieuMuon, NgayTra, TienPhat)
VALUES
(1, '2024-10-14', 0),
(2, '2024-10-19', 5000),     -- phạt nhẹ cho vui hihi
(3, '2024-10-28', 20000);    -- trễ hạn 3 ngày

INSERT INTO NhanVien (MaTK, HoTen, SDT, DiaChi)
VALUES
(2, N'Teri', '0900000001', N'Phòng Điều Hành'),
(6, N'Aya', '0912345678', N'Quầy Thủ Thư 1');

SELECT * FROM TheLoai;

SELECT * FROM Sach;

SELECT * FROM DocGia;

SELECT * FROM PhieuMuon;

SELECT * FROM ChiTietPhieuMuon;

SELECT * FROM PhieuTra;

SELECT * FROM NhanVien;
