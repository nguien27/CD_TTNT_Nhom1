const resultsEl = document.getElementById('results');
const detailEl = document.getElementById('detail');
const searchInput = document.getElementById('search-input');
const searchButton = document.getElementById('search-button');
const uploadForm = document.getElementById('upload-form');
const fileInput = document.getElementById('file-input');
const messageEl = document.getElementById('message');

let currentResults = [];

function statusHtml(status) {
    const value = status || 'CHUA_XAC_DINH';
    return `<span class="status ${value}">${value}</span>`;
}

function renderDetail(item) {
    const d = item?.doi_tuong || {};
    detailEl.innerHTML = `
        <h3>${item?.ten_hien_thi || d.ho_ten || d.ten_don_vi || 'Chi tiết'}</h3>
        ${statusHtml(item?.trang_thai_tra_luong)}
        <dl>
            <dt>Loại đối tượng</dt><dd>${item?.loai_doi_tuong || d.loai_doi_tuong || ''}</dd>
            <dt>MSNV</dt><dd>${d.ma_nhan_vien || ''}</dd>
            <dt>Họ tên</dt><dd>${d.ho_ten || ''}</dd>
            <dt>Đơn vị</dt><dd>${d.don_vi || d.ten_don_vi || ''}</dd>
            <dt>Độ khớp</dt><dd>${item?.do_khop ?? ''}</dd>
            <dt>Căn cứ</dt><dd>${item?.can_cu || ''}</dd>
            <dt>Mã quy tắc</dt><dd>${item?.ma_quy_tac || ''}</dd>
            <dt>Ghi chú</dt><dd>${item?.ghi_chu || ''}</dd>
        </dl>`;
}

function renderResults(items) {
    currentResults = items || [];
    if (!currentResults.length) {
        resultsEl.innerHTML = '<p>Không có kết quả.</p>';
        detailEl.innerHTML = '<p>Không có chi tiết.</p>';
        return;
    }
    resultsEl.innerHTML = currentResults.map((item, i) => `
        <div class="result-item" data-index="${i}">
            <strong>${item.ten_hien_thi || item.id_doi_tuong}</strong><br>
            <small>${item.loai_doi_tuong} • ${item.loai_khop || ''} • ${item.do_khop ?? ''}</small><br>
            ${statusHtml(item.trang_thai_tra_luong)}
        </div>`).join('');

    document.querySelectorAll('.result-item').forEach(el => {
        el.addEventListener('click', () => {
            document.querySelectorAll('.result-item').forEach(x => x.classList.remove('active'));
            el.classList.add('active');
            renderDetail(currentResults[Number(el.dataset.index)]);
        });
    });
    document.querySelector('.result-item')?.classList.add('active');
    renderDetail(currentResults[0]);
}

async function doSearch() {
    const q = searchInput.value.trim();
    if (!q) return;
    const res = await fetch(`/search?q=${encodeURIComponent(q)}`);
    const data = await res.json();
    if (!res.ok) {
        messageEl.textContent = data.detail || 'Lỗi tìm kiếm';
        return;
    }
    messageEl.textContent = `Tìm thấy ${data.so_ket_qua} kết quả.`;
    renderResults(data.ket_qua);
}

searchButton.addEventListener('click', doSearch);
searchInput.addEventListener('keydown', e => { if (e.key === 'Enter') doSearch(); });

uploadForm.addEventListener('submit', async e => {
    e.preventDefault();
    const file = fileInput.files[0];
    if (!file) return;
    const body = new FormData();
    body.append('file', file);
    const res = await fetch('/upload', { method: 'POST', body });
    const data = await res.json();
    messageEl.textContent = res.ok ? data.message : (data.detail?.message || data.detail || 'Upload lỗi');
});

searchInput.value = 'NV000001';
doSearch();
