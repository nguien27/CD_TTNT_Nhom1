PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS don_vi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_don_vi TEXT UNIQUE,
    ten_don_vi TEXT NOT NULL,
    ten_don_vi_chuan TEXT NOT NULL,
    loai_don_vi TEXT,
    thong_tin_mo_rong TEXT NOT NULL DEFAULT '{}',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS nhan_vien (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_nhan_vien TEXT UNIQUE,
    ho_ten TEXT NOT NULL,
    ho_ten_chuan TEXT NOT NULL,
    ma_don_vi TEXT,
    ten_don_vi TEXT,
    thong_tin_mo_rong TEXT NOT NULL DEFAULT '{}',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ma_don_vi) REFERENCES don_vi(ma_don_vi)
);

CREATE TABLE IF NOT EXISTS quy_tac_tra_luong (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_quy_tac TEXT NOT NULL UNIQUE,
    ten_quy_tac TEXT,
    pham_vi TEXT NOT NULL CHECK (pham_vi IN ('DON_VI', 'LOAI_DON_VI')),
    ma_don_vi TEXT,
    loai_don_vi TEXT,
    ket_qua TEXT NOT NULL CHECK (ket_qua IN ('YES', 'NO')),
    can_cu TEXT,
    muc_uu_tien INTEGER NOT NULL DEFAULT 0,
    ngay_hieu_luc TEXT,
    ngay_het_hieu_luc TEXT,
    dang_ap_dung INTEGER NOT NULL DEFAULT 1 CHECK (dang_ap_dung IN (0,1)),
    ghi_chu TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_nhan_vien_ho_ten_chuan ON nhan_vien(ho_ten_chuan);
CREATE INDEX IF NOT EXISTS idx_don_vi_ten_chuan ON don_vi(ten_don_vi_chuan);
CREATE INDEX IF NOT EXISTS idx_rule_ma_don_vi ON quy_tac_tra_luong(ma_don_vi);
CREATE INDEX IF NOT EXISTS idx_rule_loai_don_vi ON quy_tac_tra_luong(loai_don_vi);
