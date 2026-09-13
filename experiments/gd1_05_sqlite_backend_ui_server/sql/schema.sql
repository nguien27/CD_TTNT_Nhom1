PRAGMA foreign_keys = ON;

-- Core schema đồng bộ GĐ1-04: không dùng bảng DON_VI riêng,
-- không lưu YES/NO trực tiếp trong NHAN_VIEN.
CREATE TABLE IF NOT EXISTS nhan_vien (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_nhan_vien    TEXT UNIQUE NOT NULL,
    ho_ten          TEXT NOT NULL,
    ho_ten_chuan    TEXT,
    don_vi          TEXT,
    chuc_vu         TEXT,
    email           TEXT
);

CREATE TABLE IF NOT EXISTS business_rule (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_quy_tac          TEXT UNIQUE NOT NULL,
    ten_quy_tac         TEXT,
    ten_don_vi          TEXT,
    loai_don_vi         TEXT,
    pham_vi             TEXT,
    ket_qua             TEXT NOT NULL CHECK (ket_qua IN ('YES', 'NO')),
    can_cu              TEXT NOT NULL,
    muc_uu_tien         INTEGER NOT NULL DEFAULT 0,
    ngay_hieu_luc       TEXT,
    ngay_het_hieu_luc   TEXT,
    dang_ap_dung        INTEGER NOT NULL DEFAULT 1 CHECK (dang_ap_dung IN (0,1)),
    la_mock             INTEGER NOT NULL DEFAULT 1 CHECK (la_mock IN (0,1)),
    ghi_chu             TEXT
);

CREATE TABLE IF NOT EXISTS ngoai_le_ca_nhan (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_nhan_vien        TEXT NOT NULL,
    ket_qua             TEXT NOT NULL CHECK (ket_qua IN ('YES', 'NO')),
    can_cu              TEXT NOT NULL,
    muc_uu_tien         INTEGER NOT NULL DEFAULT 100,
    ngay_hieu_luc       TEXT,
    ngay_het_hieu_luc   TEXT,
    dang_ap_dung        INTEGER NOT NULL DEFAULT 1 CHECK (dang_ap_dung IN (0,1)),
    la_mock             INTEGER NOT NULL DEFAULT 1 CHECK (la_mock IN (0,1)),
    ghi_chu             TEXT
);

CREATE INDEX IF NOT EXISTS idx_nhan_vien_msnv ON nhan_vien(ma_nhan_vien);
CREATE INDEX IF NOT EXISTS idx_nhan_vien_ho_ten ON nhan_vien(ho_ten);
CREATE INDEX IF NOT EXISTS idx_nhan_vien_don_vi ON nhan_vien(don_vi);
CREATE INDEX IF NOT EXISTS idx_rule_ten_don_vi ON business_rule(ten_don_vi);
CREATE INDEX IF NOT EXISTS idx_rule_loai_don_vi ON business_rule(loai_don_vi);
