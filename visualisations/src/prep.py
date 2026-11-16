"""Compute every number of the 20 charts into .build/data.json.

    python -X utf8 prep.py <.build folder>        (run by make.py; env REPO = the clone, HEAD_SHA = the commit read)

Inputs: .build/commits.json (git log with trailers and raw changes), .build/repo/ (data/ and REPRODUCE.md),
.build/head-tree.txt (git ls-tree of the acts), and the texts, read with `git cat-file --batch` from the clone.
Every rule that classifies something (instrument of an amendment, field of an act, penalty of a crime, the
constitution a preamble cites, the word swaps) is written out below; whatever no rule recognises counts as "other".
"""
import collections, csv, datetime as dt, difflib, json, os, re, statistics, subprocess, sys, unicodedata

B = sys.argv[1]
REPO = os.environ.get('REPO') or os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
HEAD = os.environ.get('HEAD_SHA', '')
D = dt.date.fromisoformat
NFC = lambda s: unicodedata.normalize('NFC', s)
OLDTONE = {'oá': 'óa', 'oà': 'òa', 'oả': 'ỏa', 'oã': 'õa', 'oạ': 'ọa', 'oé': 'óe', 'oè': 'òe', 'oẻ': 'ỏe', 'oẽ': 'õe', 'oẹ': 'ọe',
           'uý': 'úy', 'uỳ': 'ùy', 'uỷ': 'ủy', 'uỹ': 'ũy', 'uỵ': 'ụy'}


def norm(s):
    """lower case, NFC, tone marks placed the new way (hoá -> hóa), sỹ -> sĩ: for matching names only"""
    s = NFC(s).lower()
    for a, b in OLDTONE.items(): s = s.replace(a, b)
    return s.replace('sỹ', 'sĩ').replace('quí', 'quý')


# ------------------------------------------------------------------ inputs
commits = json.load(open(os.path.join(B, 'commits.json'), encoding='utf-8'))[::-1]   # oldest first, git order
R = os.path.join(B, 'repo')
paths = json.load(open(os.path.join(R, 'data', 'paths.json'), encoding='utf-8'))['paths']
folder2slug = {v: k for k, v in paths.items()}
laws = {r['key']: r for r in csv.DictReader(open(os.path.join(R, 'data', 'laws.csv'), encoding='utf-8'))}
versions = {a['slug']: a for a in json.load(open(os.path.join(R, 'data', 'versions.json'), encoding='utf-8'))['acts']}
repro = open(os.path.join(R, 'REPRODUCE.md'), encoding='utf-8').read()
RETRIEVED = re.search(r'written by the build on (\d{4}-\d\d-\d\d)', repro).group(1)


class Blobs:
    def __init__(self):
        self.p = subprocess.Popen(['git', '-C', REPO, 'cat-file', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  env=dict(os.environ, GIT_NO_LAZY_FETCH='1'))
        self.cache = collections.OrderedDict()

    def get(self, oid):
        if oid in self.cache:
            self.cache.move_to_end(oid); return self.cache[oid]
        self.p.stdin.write((oid + '\n').encode()); self.p.stdin.flush()
        hdr = self.p.stdout.readline().decode().split()
        if len(hdr) < 3 or hdr[1] != 'blob': raise SystemExit('blob not in the clone: ' + oid + ' (run make.py, which downloads it)')
        t = NFC(self.p.stdout.read(int(hdr[2])).decode('utf-8')); self.p.stdout.read(1)
        self.cache[oid] = t
        if len(self.cache) > 3000: self.cache.popitem(last=False)
        return t


BL = Blobs()


def act_of(path):
    p = path.split('/')
    if p[0] in paths: return p[0], p[-1]
    if p[0] in ('bo-luat', 'luat') and len(p) >= 4: return folder2slug.get('/'.join(p[:3])), p[-1]
    if p[0] == 'constitution' and len(p) >= 3: return folder2slug.get('/'.join(p[:2])), p[-1]
    return None, None


# events: one per (law commit, act it touches), in in-force order (git order breaks ties: an act built twice on one day)
events = []
for i, c in enumerate(commits):
    kind = c['t'].get('Kind', [''])[0]
    if kind not in ('law', 'correction'): continue
    lawkey = c['ae'].split('@')[0] if c['ae'].endswith('@vbpl.invalid') else None
    if kind == 'correction':   # the appended correction names its law in Law: (Luật Giáo dục nghề nghiệp 124/2025/QH15)
        m = re.search(r'(\d+)/(\d{4})/(QH\d+)', c['t']['Law'][0]); lawkey = f'luat-{int(m.group(1))}-{m.group(2)}-{m.group(3).lower()}'
    by = collections.defaultdict(list)
    for st, path, old, new in c['ch']:
        a, f = act_of(path)
        if a: by[a].append((st, f, old, new))
    for a, ch in by.items():
        events.append({'i': i, 'inf': c['t']['In-force'][0], 'law': lawkey, 'start': 'Act' in c['t'], 'act': a, 'ch': ch, 'kind': kind})
events.sort(key=lambda e: (e['inf'], e['i']))
assert all(e['law'] in laws for e in events), 'a commit credits a law laws.csv does not list'
RECORD_TO = max(e['inf'] for e in events)
starts = {e['act']: e for e in events if e['start']}
assert len(starts) == 162, len(starts)
AM = [e for e in events if not e['start']]
isart = lambda f: f.startswith('art-')
nart = lambda e: sum(1 for st, f, o, n in e['ch'] if isart(f))

# ------------------------------------------------------------------ the acts: names, fields
# slug -> [Vietnamese name as shown, English name, field]
FIELDS = ['state', 'justice', 'security', 'economy', 'tax', 'build', 'env', 'social', 'culture', 'tech']
ACTS = {
 'hien-phap': ['Hiến pháp năm 2013', 'Constitution of 2013', 'state'],
 'bo-luat-dan-su': ['Bộ luật Dân sự', 'Civil Code', 'justice'],
 'bo-luat-hinh-su': ['Bộ luật Hình sự', 'Penal Code', 'justice'],
 'bo-luat-to-tung-dan-su': ['Bộ luật Tố tụng dân sự', 'Civil Procedure Code', 'justice'],
 'bo-luat-to-tung-hinh-su': ['Bộ luật Tố tụng hình sự', 'Criminal Procedure Code', 'justice'],
 'bo-luat-lao-dong': ['Bộ luật Lao động', 'Labour Code', 'social'],
 'bo-luat-hang-hai-95-2015-qh13': ['Bộ luật Hàng hải', 'Maritime Code', 'build'],
 'luat-doanh-nghiep': ['Luật Doanh nghiệp', 'Law on Enterprises', 'economy'],
 'luat-sy-quan-quan-doi-nhan-dan-viet-nam-16-1999-qh10': ['Luật Sỹ quan Quân đội nhân dân Việt Nam', 'Law on Officers of the Vietnam People’s Army', 'security'],
 'luat-kinh-doanh-bao-hiem-24-2000-qh10': ['Luật Kinh doanh bảo hiểm (2000)', 'Law on Insurance Business (2000)', 'economy'],
 'luat-bien-gioi-quoc-gia-06-2003-qh11': ['Luật Biên giới quốc gia', 'Law on National Borders', 'security'],
 'luat-an-ninh-quoc-gia-32-2004-qh11': ['Luật An ninh quốc gia', 'Law on National Security', 'security'],
 'luat-thuong-mai-36-2005-qh11': ['Luật Thương mại', 'Commercial Law', 'economy'],
 'luat-so-huu-tri-tue-50-2005-qh11': ['Luật Sở hữu trí tuệ', 'Law on Intellectual Property', 'economy'],
 'luat-hang-khong-dan-dung-viet-nam-66-2006-qh11': ['Luật Hàng không dân dụng Việt Nam', 'Law on Civil Aviation', 'build'],
 'luat-tieu-chuan-va-quy-chuan-ky-thuat-68-2006-qh11': ['Luật Tiêu chuẩn và quy chuẩn kỹ thuật', 'Law on Standards and Technical Regulations', 'tech'],
 'luat-chung-khoan-70-2006-qh11': ['Luật Chứng khoán (2006)', 'Law on Securities (2006)', 'economy'],
 'luat-phong-chong-nhiem-vi-rut-gay-ra-hoi-chung-suy-giam-mien-dich-mac-phai-o-nguoi-hiv-aids-64-2006-qh11': ['Luật Phòng, chống HIV/AIDS', 'Law on HIV/AIDS Prevention and Control', 'social'],
 'luat-the-duc-the-thao-77-2006-qh11': ['Luật Thể dục, thể thao', 'Law on Physical Training and Sports', 'culture'],
 'luat-thue-thu-nhap-doanh-nghiep-14-2008-qh12': ['Luật Thuế thu nhập doanh nghiệp (2008)', 'Law on Corporate Income Tax (2008)', 'tax'],
 'luat-trung-mua-trung-dung-tai-san-15-2008-qh12': ['Luật Trưng mua, trưng dụng tài sản', 'Law on Requisition of Property', 'state'],
 'luat-cong-nghe-cao-21-2008-qh12': ['Luật Công nghệ cao', 'Law on High Technologies', 'tech'],
 'luat-da-dang-sinh-hoc-20-2008-qh12': ['Luật Đa dạng sinh học', 'Law on Biodiversity', 'env'],
 'luat-quoc-tich-viet-nam-24-2008-qh12': ['Luật Quốc tịch Việt Nam', 'Law on Vietnamese Nationality', 'state'],
 'luat-bao-hiem-y-te-25-2008-qh12': ['Luật Bảo hiểm y tế', 'Law on Health Insurance', 'social'],
 'luat-ly-lich-tu-phap-28-2009-qh12': ['Luật Lý lịch tư pháp', 'Law on Judicial Records', 'justice'],
 'luat-nguoi-cao-tuoi-39-2009-qh12': ['Luật Người cao tuổi', 'Law on the Elderly', 'social'],
 'luat-tan-so-vo-tuyen-dien-42-2009-qh12': ['Luật Tần số vô tuyến điện', 'Law on Radio Frequencies', 'tech'],
 'luat-thue-tai-nguyen-45-2009-qh12': ['Luật Thuế tài nguyên', 'Law on Natural Resource Tax', 'tax'],
 'luat-ngan-hang-nha-nuoc-viet-nam-46-2010-qh12': ['Luật Ngân hàng Nhà nước Việt Nam', 'Law on the State Bank of Vietnam', 'economy'],
 'luat-nguoi-khuyet-tat-51-2010-qh12': ['Luật Người khuyết tật', 'Law on Persons with Disabilities', 'social'],
 'luat-su-dung-nang-luong-tiet-kiem-va-hieu-qua-50-2010-qh12': ['Luật Sử dụng năng lượng tiết kiệm và hiệu quả', 'Law on Energy Efficiency', 'env'],
 'luat-buu-chinh-49-2010-qh12': ['Luật Bưu chính', 'Law on Postal Services', 'tech'],
 'luat-trong-tai-thuong-mai-54-2010-qh12': ['Luật Trọng tài thương mại', 'Law on Commercial Arbitration', 'justice'],
 'luat-thue-su-dung-dat-phi-nong-nghiep-48-2010-qh12': ['Luật Thuế sử dụng đất phi nông nghiệp', 'Law on Non-agricultural Land Use Tax', 'tax'],
 'luat-vien-chuc-58-2010-qh12': ['Luật Viên chức', 'Law on Public Employees', 'state'],
 'luat-kiem-toan-doc-lap-67-2011-qh12': ['Luật Kiểm toán độc lập', 'Law on Independent Audit', 'economy'],
 'luat-do-luong-04-2011-qh13': ['Luật Đo lường', 'Law on Metrology', 'tech'],
 'luat-khieu-nai-02-2011-qh13': ['Luật Khiếu nại', 'Law on Complaints', 'state'],
 'luat-phong-chong-tac-hai-cua-thuoc-la-09-2012-qh13': ['Luật Phòng, chống tác hại của thuốc lá', 'Law on Tobacco Harm Prevention', 'social'],
 'luat-bien-viet-nam-18-2012-qh13': ['Luật Biển Việt Nam', 'Law of the Sea of Vietnam', 'security'],
 'luat-quang-cao-16-2012-qh13': ['Luật Quảng cáo', 'Law on Advertising', 'culture'],
 'luat-xuat-ban-19-2012-qh13': ['Luật Xuất bản', 'Law on Publishing', 'culture'],
 'luat-phong-chong-khung-bo-28-2013-qh13': ['Luật Phòng, chống khủng bố', 'Law on Counter-terrorism', 'security'],
 'luat-khoa-hoc-va-cong-nghe-29-2013-qh13': ['Luật Khoa học và công nghệ', 'Law on Science and Technology', 'tech'],
 'luat-giao-duc-quoc-phong-va-an-ninh-30-2013-qh13': ['Luật Giáo dục quốc phòng và an ninh', 'Law on Defence and Security Education', 'security'],
 'luat-phong-chong-thien-tai-33-2013-qh13': ['Luật Phòng, chống thiên tai', 'Law on Natural Disaster Prevention and Control', 'env'],
 'luat-bao-ve-va-kiem-dich-thuc-vat-41-2013-qh13': ['Luật Bảo vệ và kiểm dịch thực vật', 'Law on Plant Protection and Quarantine', 'env'],
 'luat-nhap-canh-xuat-canh-qua-canh-cu-tru-cua-nguoi-nuoc-ngoai-tai-viet-nam-47-2014-qh13': ['Luật Nhập cảnh, xuất cảnh, quá cảnh, cư trú của người nước ngoài tại Việt Nam', 'Law on Entry, Exit, Transit and Residence of Foreigners', 'security'],
 'luat-hai-quan-so-54-2014-qh13-54-2014-qh13': ['Luật Hải quan', 'Customs Law', 'tax'],
 'luat-to-chuc-quoc-hoi-57-2014-qh13': ['Luật Tổ chức Quốc hội', 'Law on the Organisation of the National Assembly', 'state'],
 'luat-to-chuc-vien-kiem-sat-nhan-dan-63-2014-qh13': ['Luật Tổ chức Viện kiểm sát nhân dân', 'Law on the Organisation of People’s Procuracies', 'justice'],
 'luat-giao-duc-nghe-nghiep-74-2014-qh13': ['Luật Giáo dục nghề nghiệp', 'Law on Vocational Education', 'social'],
 'luat-mat-tran-to-quoc-viet-nam-75-2015-qh13': ['Luật Mặt trận Tổ quốc Việt Nam', 'Law on the Vietnam Fatherland Front', 'state'],
 'luat-kiem-toan-nha-nuoc-81-2015-qh13': ['Luật Kiểm toán nhà nước', 'Law on State Audit', 'state'],
 'luat-bau-cu-dai-bieu-quoc-hoi-va-dai-bieu-hoi-dong-nhan-dan-85-2015-qh13': ['Luật Bầu cử đại biểu Quốc hội và đại biểu Hội đồng nhân dân', 'Law on Elections to the National Assembly and People’s Councils', 'state'],
 'luat-an-toan-ve-sinh-lao-dong-84-2015-qh13': ['Luật An toàn, vệ sinh lao động', 'Law on Occupational Safety and Health', 'social'],
 'luat-tai-nguyen-moi-truong-bien-va-hai-dao-82-2015-qh13': ['Luật Tài nguyên, môi trường biển và hải đảo', 'Law on Marine and Island Resources and Environment', 'env'],
 'luat-an-toan-thong-tin-mang-86-2015-qh13': ['Luật An toàn thông tin mạng', 'Law on Network Information Security', 'security'],
 'luat-hoat-dong-giam-sat-cua-quoc-hoi-va-hoi-dong-nhan-dan-87-2015-qh13': ['Luật Hoạt động giám sát của Quốc hội và Hội đồng nhân dân', 'Law on Supervision by the National Assembly and People’s Councils', 'state'],
 'luat-ke-toan-88-2015-qh13': ['Luật Kế toán', 'Law on Accounting', 'economy'],
 'luat-thong-ke-89-2015-qh13': ['Luật Thống kê', 'Law on Statistics', 'state'],
 'luat-to-tung-hanh-chinh-93-2015-qh13': ['Luật Tố tụng hành chính', 'Law on Administrative Procedure', 'justice'],
 'luat-quan-nhan-chuyen-nghiep-cong-nhan-va-vien-chuc-quoc-phong-98-2015-qh13': ['Luật Quân nhân chuyên nghiệp, công nhân và viên chức quốc phòng', 'Law on Professional Servicemen and Defence Workers', 'security'],
 'luat-to-chuc-co-quan-dieu-tra-hinh-su-99-2015-qh13': ['Luật Tổ chức cơ quan điều tra hình sự', 'Law on the Organisation of Criminal Investigation Bodies', 'justice'],
 'luat-bao-chi-103-2016-qh13': ['Luật Báo chí', 'Press Law', 'culture'],
 'luat-tre-em-102-2016-qh13': ['Luật Trẻ em', 'Law on Children', 'social'],
 'luat-thue-xuat-khau-thue-nhap-khau-107-2016-qh13': ['Luật Thuế xuất khẩu, thuế nhập khẩu', 'Law on Export and Import Duties', 'tax'],
 'luat-duoc-105-2016-qh13': ['Luật Dược', 'Law on Pharmacy', 'social'],
 'luat-dieu-uoc-quoc-te-108-2016-qh13': ['Luật Điều ước quốc tế', 'Law on Treaties', 'state'],
 'luat-dau-gia-tai-san-01-2016-qh14': ['Luật Đấu giá tài sản', 'Law on Property Auction', 'justice'],
 'luat-tin-nguong-ton-giao-02-2016-qh14': ['Luật Tín ngưỡng, tôn giáo', 'Law on Belief and Religion', 'culture'],
 'luat-ho-tro-doanh-nghiep-nho-va-vua-04-2017-qh14': ['Luật Hỗ trợ doanh nghiệp nhỏ và vừa', 'Law on Support for Small and Medium Enterprises', 'economy'],
 'luat-chuyen-giao-cong-nghe-07-2017-qh14': ['Luật Chuyển giao công nghệ', 'Law on Technology Transfer', 'tech'],
 'luat-tro-giup-phap-ly-11-2017-qh14': ['Luật Trợ giúp pháp lý', 'Law on Legal Aid', 'justice'],
 'luat-canh-ve-13-2017-qh14': ['Luật Cảnh vệ', 'Law on Close Protection', 'security'],
 'luat-trach-nhiem-boi-thuong-cua-nha-nuoc-10-2017-qh14': ['Luật Trách nhiệm bồi thường của Nhà nước', 'Law on State Compensation Liability', 'justice'],
 'luat-quan-ly-su-dung-tai-san-cong-15-2017-qh14': ['Luật Quản lý, sử dụng tài sản công', 'Law on Public Property', 'economy'],
 'luat-lam-nghiep-16-2017-qh14': ['Luật Lâm nghiệp', 'Law on Forestry', 'env'],
 'luat-thuy-san-18-2017-qh14': ['Luật Thủy sản', 'Law on Fisheries', 'env'],
 'luat-quy-hoach-21-2017-qh14': ['Luật Quy hoạch', 'Law on Planning', 'build'],
 'luat-quoc-phong-22-2018-qh14': ['Luật Quốc phòng', 'Law on National Defence', 'security'],
 'luat-to-cao-25-2018-qh14': ['Luật Tố cáo', 'Law on Denunciations', 'state'],
 'luat-do-dac-va-ban-do-27-2018-qh14': ['Luật Đo đạc và bản đồ', 'Law on Surveying and Mapping', 'env'],
 'luat-bao-ve-bi-mat-nha-nuoc-29-2018-qh14': ['Luật Bảo vệ bí mật nhà nước (2018)', 'Law on Protecting State Secrets (2018)', 'security'],
 'luat-dac-xa-30-2018-qh14': ['Luật Đặc xá', 'Law on Special Amnesty', 'justice'],
 'luat-chan-nuoi-32-2018-qh14': ['Luật Chăn nuôi', 'Law on Animal Husbandry', 'env'],
 'luat-trong-trot-31-2018-qh14': ['Luật Trồng trọt', 'Law on Crop Production', 'env'],
 'luat-cong-an-nhan-dan-37-2018-qh14': ['Luật Công an nhân dân', 'Law on the People’s Public Security', 'security'],
 'luat-phong-chong-tham-nhung-36-2018-qh14': ['Luật Phòng, chống tham nhũng', 'Law on Anti-corruption', 'state'],
 'luat-quan-ly-thue-38-2019-qh14': ['Luật Quản lý thuế (2019)', 'Law on Tax Administration (2019)', 'tax'],
 'luat-dau-tu-cong-39-2019-qh14': ['Luật Đầu tư công', 'Law on Public Investment', 'economy'],
 'luat-kien-truc-40-2019-qh14': ['Luật Kiến trúc', 'Law on Architecture', 'build'],
 'luat-thi-hanh-an-hinh-su-41-2019-qh14': ['Luật Thi hành án hình sự', 'Law on Enforcement of Criminal Judgments', 'justice'],
 'luat-giao-duc-43-2019-qh14': ['Luật Giáo dục', 'Law on Education', 'social'],
 'luat-thu-vien-46-2019-qh14': ['Luật Thư viện', 'Law on Libraries', 'culture'],
 'luat-dan-quan-tu-ve-48-2019-qh14': ['Luật Dân quân tự vệ', 'Law on Militia and Self-defence Forces', 'security'],
 'luat-luc-luong-du-bi-dong-vien-53-2019-qh14': ['Luật Lực lượng dự bị động viên', 'Law on Reserve Forces', 'security'],
 'luat-chung-khoan-54-2019-qh14': ['Luật Chứng khoán (2019)', 'Law on Securities (2019)', 'economy'],
 'luat-hoa-giai-doi-thoai-tai-toa-an-58-2020-qh14': ['Luật Hòa giải, đối thoại tại Tòa án', 'Law on Mediation and Dialogue at Court', 'justice'],
 'luat-thanh-nien-57-2020-qh14': ['Luật Thanh niên', 'Law on Youth', 'social'],
 'luat-dau-tu-theo-phuong-thuc-doi-tac-cong-tu-64-2020-qh14': ['Luật Đầu tư theo phương thức đối tác công tư', 'Law on Public-Private Partnership Investment', 'economy'],
 'luat-bien-phong-viet-nam-66-2020-qh14': ['Luật Biên phòng Việt Nam', 'Law on the Border Guard', 'security'],
 'luat-cu-tru-68-2020-qh14': ['Luật Cư trú', 'Law on Residence', 'security'],
 'luat-nguoi-lao-dong-viet-nam-di-lam-viec-o-nuoc-ngoai-theo-hop-dong-69-2020-qh14': ['Luật Người lao động Việt Nam đi làm việc ở nước ngoài theo hợp đồng', 'Law on Vietnamese Workers Abroad under Contract', 'social'],
 'luat-bao-ve-moi-truong-72-2020-qh14': ['Luật Bảo vệ môi trường', 'Law on Environmental Protection', 'env'],
 'luat-phong-chong-ma-tuy-73-2021-qh14': ['Luật Phòng, chống ma túy', 'Law on Drug Prevention and Control', 'security'],
 'luat-thi-dua-khen-thuong-06-2022-qh15': ['Luật Thi đua, khen thưởng', 'Law on Emulation and Commendation', 'state'],
 'luat-kinh-doanh-bao-hiem-08-2022-qh15': ['Luật Kinh doanh bảo hiểm (2022)', 'Law on Insurance Business (2022)', 'economy'],
 'luat-thuc-hien-dan-chu-o-co-so-10-2022-qh15': ['Luật Thực hiện dân chủ ở cơ sở', 'Law on Grassroots Democracy', 'state'],
 'luat-phong-chong-rua-tien-14-2022-qh15': ['Luật Phòng, chống rửa tiền', 'Law on Anti-money Laundering', 'economy'],
 'luat-kham-benh-chua-benh-2023-15-2023-qh15': ['Luật Khám bệnh, chữa bệnh', 'Law on Medical Examination and Treatment', 'social'],
 'luat-gia-16-2023-qh15': ['Luật Giá', 'Law on Prices', 'economy'],
 'luat-phong-thu-dan-su-18-2023-qh15': ['Luật Phòng thủ dân sự', 'Law on Civil Defence', 'security'],
 'luat-bao-ve-quyen-loi-nguoi-tieu-dung-19-2023-qh15': ['Luật Bảo vệ quyền lợi người tiêu dùng', 'Law on Consumer Protection', 'economy'],
 'luat-hop-tac-xa-17-2023-qh15': ['Luật Hợp tác xã', 'Law on Cooperatives', 'economy'],
 'luat-giao-dich-dien-tu-20-2023-qh15': ['Luật Giao dịch điện tử', 'Law on Electronic Transactions', 'tech'],
 'luat-dau-thau-22-2023-qh15': ['Luật Đấu thầu', 'Law on Bidding', 'economy'],
 'luat-vien-thong-24-2023-qh15': ['Luật Viễn thông', 'Law on Telecommunications', 'tech'],
 'luat-quan-ly-bao-ve-cong-trinh-quoc-phong-va-khu-quan-su-25-2023-qh15': ['Luật Quản lý, bảo vệ công trình quốc phòng và khu quân sự', 'Law on Defence Works and Military Zones', 'security'],
 'luat-tai-nguyen-nuoc-2023-28-2023-qh15': ['Luật Tài nguyên nước', 'Law on Water Resources', 'env'],
 'luat-can-cuoc-26-2023-qh15': ['Luật Căn cước', 'Law on Identification', 'security'],
 'luat-nha-o-27-2023-qh15': ['Luật Nhà ở', 'Law on Housing', 'build'],
 'luat-luc-luong-tham-gia-bao-ve-an-ninh-trat-tu-o-co-so-30-2023-qh15': ['Luật Lực lượng tham gia bảo vệ an ninh, trật tự ở cơ sở', 'Law on Grassroots Security and Order Forces', 'security'],
 'luat-kinh-doanh-bat-dong-san-29-2023-qh15': ['Luật Kinh doanh bất động sản', 'Law on Real Estate Business', 'build'],
 'luat-cac-to-chuc-tin-dung-32-2024-qh15': ['Luật Các tổ chức tín dụng', 'Law on Credit Institutions', 'economy'],
 'luat-luu-tru-33-2024-qh15': ['Luật Lưu trữ', 'Law on Archives', 'state'],
 'luat-to-chuc-toa-an-nhan-dan-so-34-2024-qh15-34-2024-qh15': ['Luật Tổ chức Tòa án nhân dân', 'Law on the Organisation of People’s Courts', 'justice'],
 'luat-duong-bo-35-2024-qh15': ['Luật Đường bộ', 'Law on Roads', 'build'],
 'luat-trat-tu-an-toan-giao-thong-duong-bo-36-2024-qh15': ['Luật Trật tự, an toàn giao thông đường bộ', 'Law on Road Traffic Order and Safety', 'build'],
 'luat-cong-nghiep-quoc-phong-an-ninh-va-dong-vien-cong-nghiep-38-2024-qh15': ['Luật Công nghiệp quốc phòng, an ninh và động viên công nghiệp', 'Law on the Defence and Security Industry', 'security'],
 'luat-quan-ly-su-dung-vu-khi-vat-lieu-no-va-cong-cu-ho-tro-42-2024-qh15': ['Luật Quản lý, sử dụng vũ khí, vật liệu nổ và công cụ hỗ trợ', 'Law on Weapons, Explosives and Support Tools', 'security'],
 'luat-bao-hiem-xa-hoi-41-2024-qh15': ['Luật Bảo hiểm xã hội', 'Law on Social Insurance', 'social'],
 'luat-di-san-van-hoa-45-2024-qh15': ['Luật Di sản văn hóa', 'Law on Cultural Heritage', 'culture'],
 'luat-cong-chung-46-2024-qh15': ['Luật Công chứng', 'Law on Notarisation', 'justice'],
 'luat-thue-gia-tri-gia-tang-48-2024-qh15': ['Luật Thuế giá trị gia tăng', 'Law on Value-added Tax', 'tax'],
 'luat-phong-khong-nhan-dan-49-2024-qh15': ['Luật Phòng không nhân dân', 'Law on People’s Air Defence', 'security'],
 'luat-cong-doan-50-2024-qh15': ['Luật Công đoàn', 'Law on Trade Unions', 'social'],
 'luat-phong-chong-mua-ban-nguoi-so-53-2024-qh15-53-2024-qh15': ['Luật Phòng, chống mua bán người', 'Law on Combating Human Trafficking', 'security'],
 'luat-dia-chat-va-khoang-san-54-2024-qh15': ['Luật Địa chất và khoáng sản', 'Law on Geology and Minerals', 'env'],
 'luat-phong-chay-chua-chay-va-cuu-nan-cuu-ho-55-2024-qh15': ['Luật Phòng cháy, chữa cháy và cứu nạn, cứu hộ', 'Law on Fire Prevention and Rescue', 'security'],
 'luat-du-lieu-60-2024-qh15': ['Luật Dữ liệu', 'Law on Data', 'tech'],
 'luat-to-chuc-chinh-phu-63-2025-qh15': ['Luật Tổ chức Chính phủ', 'Law on the Organisation of the Government', 'state'],
 'luat-ban-hanh-van-ban-quy-pham-phap-luat-64-2025-qh15': ['Luật Ban hành văn bản quy phạm pháp luật', 'Law on the Promulgation of Legal Documents', 'state'],
 'luat-quan-ly-va-dau-tu-von-nha-nuoc-tai-doanh-nghiep-68-2025-qh15': ['Luật Quản lý và đầu tư vốn nhà nước tại doanh nghiệp', 'Law on State Capital in Enterprises', 'economy'],
 'luat-thue-thu-nhap-doanh-nghiep-67-2025-qh15': ['Luật Thuế thu nhập doanh nghiệp (2025)', 'Law on Corporate Income Tax (2025)', 'tax'],
 'luat-cong-nghiep-cong-nghe-so-71-2025-qh15': ['Luật Công nghiệp công nghệ số', 'Law on the Digital Technology Industry', 'tech'],
 'luat-hoa-chat-69-2025-qh15': ['Luật Hóa chất', 'Law on Chemicals', 'env'],
 'luat-thue-tieu-thu-dac-biet-66-2025-qh15': ['Luật Thuế tiêu thụ đặc biệt', 'Law on Special Consumption Tax', 'tax'],
 'luat-nha-giao-73-2025-qh15': ['Luật Nhà giáo', 'Law on Teachers', 'social'],
 'luat-sua-doi-bo-sung-mot-so-dieu-cua-luat-to-chuc-toa-an-nhan-dan-81-2025-qh15': ['Luật sửa đổi Luật Tổ chức Tòa án nhân dân (2025)', 'Law amending the Law on People’s Courts (2025)', 'justice'],
 'luat-sua-doi-bo-sung-mot-so-dieu-cua-bo-luat-hinh-su-86-2025-qh15': ['Luật sửa đổi Bộ luật Hình sự (2025)', 'Law amending the Penal Code (2025)', 'justice'],
 'luat-khoa-hoc-cong-nghe-va-doi-moi-sang-tao-93-2025-qh15': ['Luật Khoa học, công nghệ và đổi mới sáng tạo', 'Law on Science, Technology and Innovation', 'tech'],
 'luat-nang-luong-nguyen-tu-94-2025-qh15': ['Luật Năng lượng nguyên tử', 'Law on Atomic Energy', 'tech'],
 'luat-duong-sat-95-2025-qh15': ['Luật Đường sắt', 'Law on Railways', 'build'],
 'luat-bao-ve-bi-mat-nha-nuoc-so-117-2025-qh15-117-2025-qh15': ['Luật Bảo vệ bí mật nhà nước (2025)', 'Law on Protecting State Secrets (2025)', 'security'],
 'luat-dan-so-so-113-2025-qh15-113-2025-qh15': ['Luật Dân số', 'Law on Population', 'social'],
 'luat-quan-ly-thue-108-2025-qh15': ['Luật Quản lý thuế (2025)', 'Law on Tax Administration (2025)', 'tax'],
 'luat-sua-doi-bo-sung-mot-so-dieu-cua-luat-tiep-cong-dan-luat-khieu-nai-luat-to-cao-136-2025-qh15': ['Luật sửa đổi các luật về tiếp công dân, khiếu nại, tố cáo (2025)', 'Law amending the laws on citizen reception, complaints and denunciations (2025)', 'state'],
 'luat-xay-dung-135-2025-qh15': ['Luật Xây dựng', 'Law on Construction', 'build'],
 'luat-dau-tu-143-2025-qh15': ['Luật Đầu tư', 'Law on Investment', 'economy'],
 'luat-du-tru-quoc-gia-so-145-2025-qh15-145-2025-qh15': ['Luật Dự trữ quốc gia', 'Law on National Reserves', 'economy'],
}
assert set(ACTS) == set(starts), set(starts) ^ set(ACTS)
# acts the record holds with a wrong text (vulnerabilities/README): left out of the measures of wording
WRONG_TEXT = {'luat-tre-em-102-2016-qh13', 'luat-dan-quan-tu-ve-48-2019-qh14'}
# acts that are themselves amending laws: their articles are amendments to other acts, so they are left out of length
AMENDING_ACTS = {a for a in ACTS if a.startswith('luat-sua-doi-bo-sung')}

TERMS = ['QH10', 'QH11', 'QH12', 'QH13', 'QH14', 'QH15', 'QH16']
ROMAN = {'QH10': 'X', 'QH11': 'XI', 'QH12': 'XII', 'QH13': 'XIII', 'QH14': 'XIV', 'QH15': 'XV', 'QH16': 'XVI'}
lawnum = lambda k: re.search(r'(\d+)/(\d{4})/(QH\d+)', laws[k]['label'])
term_of_law = lambda k: (lawnum(k).group(3) if lawnum(k) else ('QH13' if k == 'hien-phap-2013' else None))


def first_inforce(k):
    v = laws[k]['in_force_days'].split()
    return min(v) if v else None


acts = {}
for a, e in starts.items():
    k = e['law']
    m = lawnum(k)
    folder = paths[a]
    acts[a] = {'id': a, 'law': k, 'num': m.group(0) if m else None, 'term': term_of_law(k), 'enacted': laws[k]['enacted'], 'inforce': e['inf'],
               'kind': 'constitution' if folder.startswith('constitution') else 'code' if folder.startswith('bo-luat') else 'law',
               'vi': ACTS[a][0], 'en': ACTS[a][1], 'field': ACTS[a][2]}
ORDER = sorted(acts, key=lambda a: (acts[a]['enacted'], a))
AIX = {a: i for i, a in enumerate(ORDER)}

# ------------------------------------------------------------------ one pass over the history
PH = {'huyen': r'cấp huyện', 'xa': r'cấp xã', 'kv': r'Tòa án nhân dân khu vực',
      'MONRE': r'Bộ Tài nguyên và Môi trường', 'MARD': r'Bộ Nông nghiệp và Phát triển nông thôn', 'MPI': r'Bộ Kế hoạch và Đầu tư',
      'MOLISA': r'Bộ Lao động\s*[-–,]\s*Thương binh và Xã hội', 'MIC': r'Bộ Thông tin và Truyền thông', 'MOT': r'Bộ Giao thông vận tải',
      'MAE': r'Bộ Nông nghiệp và Môi trường'}
PHX = {k: re.compile(v, re.I) for k, v in PH.items()}
# the edits counted in chart 20: a word swap of the amendment (old words -> new words), read with difflib on the words
SWAPS = [  # key, theme, old pattern, new pattern (matched on the changed words with up to 5 words of context on each side)
    ('MONRE', 'ministry', r'Bộ Tài nguyên và Môi trường', r'Bộ Nông nghiệp và Môi trường'),
    ('MARD', 'ministry', r'Bộ Nông nghiệp và Phát triển nông thôn', r'Bộ Nông nghiệp và Môi trường'),
    ('MOT', 'ministry', r'Bộ Giao thông vận tải', r'Bộ Xây dựng'),
    ('MPI', 'ministry', r'Bộ Kế hoạch và Đầu tư', r'Bộ Tài chính'),
    ('MOLISA', 'ministry', r'Bộ Lao động\s*[-–,]\s*Thương binh và Xã hội', r'Bộ Nội vụ|Bộ Y tế'),
    ('MIC', 'ministry', r'Bộ Thông tin và Truyền thông', r'Bộ Khoa học và Công nghệ|Bộ Văn hóa, Thể thao và Du lịch'),
    ('huyen-xa', 'local', r'cấp huyện', r'cấp xã'),
    ('huyen-tinh', 'local', r'cấp huyện', r'cấp tỉnh'),
    ('court-kv', 'local', r'(Tòa án|Viện kiểm sát) nhân dân cấp huyện', r'(Tòa án|Viện kiểm sát) nhân dân khu vực'),
    ('court-cao', 'local', r'(Tòa án|Viện kiểm sát) nhân dân cấp cao', r'(Tòa án|Viện kiểm sát) nhân dân cấp tỉnh|(Tòa án|Viện kiểm sát) nhân dân tối cao'),
    ('thitran', 'local', r'thị trấn', r'đặc khu'),
    ('tone', 'spelling', r'\w*(oá|oà|oả|oã|oạ|uỷ|uý|uỳ|uỹ|uỵ)\w*', r'\w*(óa|òa|ỏa|õa|ọa|ủy|úy|ùy|ũy|ụy)\w*'),
    ('money', 'amount', r'\b\d{1,3}(\.\d{3})+ đồng', r'\b\d{1,3}(\.\d{3})+ đồng'),
]
SWX = [(k, th, re.compile(o, re.I), re.compile(n, re.I)) for k, th, o, n in SWAPS]

state = {}          # act -> {file: blob}
flags = {}          # (act, file) -> {phrase: count}
blame = {}          # (act, file) -> [(line, law)]
ph_delta = collections.defaultdict(collections.Counter)   # day -> phrase -> change in the number of articles holding it
chg = []            # per amendment event and article: year, law, act, field, status, share of words changed, words
swap_hits = collections.defaultdict(set)   # swap key -> {(event index, act, file)}
swap_ex = collections.defaultdict(collections.Counter)   # swap key -> Counter of (old, new) forms
money_ratio = collections.Counter()   # new amount / old amount, for every amount an amendment raised
first_files = {}    # act -> {file: blob} as enacted (after its start event; the Penal Code's same-day amendment comes after)


def phflags(t):
    return {k: len(r.findall(t)) for k, r in PHX.items()}


for ei, e in enumerate(events):
    a = e['act']; cur = dict(state.get(a, {}))
    d = ph_delta[e['inf']]
    for st, f, old, new in e['ch']:
        if st == 'D': cur.pop(f, None)
        else: cur[f] = new
        if not isart(f): continue
        key = (a, f)
        fo = flags.get(key)
        fn = None if st == 'D' else phflags(BL.get(new))
        for k in PH:
            d[k] += (1 if (fn or {}).get(k) else 0) - (1 if (fo or {}).get(k) else 0)
            d[k + '#'] += (fn or {}).get(k, 0) - (fo or {}).get(k, 0)
        if fn is None: flags.pop(key, None)
        else: flags[key] = fn
        # blame by line: lines kept from the earlier text keep their author
        if st == 'D': blame.pop(key, None)
        else:
            nl = BL.get(new).split('\n')
            ol = blame.get(key)
            if ol is None or st == 'A': blame[key] = [(l, e['law']) for l in nl]
            else:
                sm = difflib.SequenceMatcher(None, [l for l, _ in ol], nl, autojunk=False)
                out = []
                for tag, i1, i2, j1, j2 in sm.get_opcodes():
                    out += ol[i1:i2] if tag == 'equal' else [(l, e['law']) for l in nl[j1:j2]]
                blame[key] = out
        if e['start']: continue
        rec = {'y': e['inf'][:4], 'inf': e['inf'], 'law': e['law'], 'act': a, 'st': st, 'ei': ei}
        if st == 'M':
            ta, tb = BL.get(old), BL.get(new)
            wa = ta.split('\n', 1)[1].split() if '\n' in ta else []
            wb = tb.split('\n', 1)[1].split() if '\n' in tb else []
            sm = difflib.SequenceMatcher(None, wa, wb, autojunk=False)
            same = sum(b.size for b in sm.get_matching_blocks())
            rec['share'] = 1 - same / max(1, len(wa), len(wb))
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag == 'equal': continue
                ctx_o = ' '.join(wa[max(0, i1 - 5):i2 + 5]); ctx_n = ' '.join(wb[max(0, j1 - 5):j2 + 5])
                chg_o = ' '.join(wa[i1:i2]); chg_n = ' '.join(wb[j1:j2])
                for k, th, ro, rn in SWX:
                    if k == 'tone':
                        pairs_ = [(w, v) for w, v in zip(wa[i1:i2], wb[j1:j2]) if ro.fullmatch(w) and w != v and norm(w) == norm(v)]
                        if pairs_ and i2 - i1 == j2 - j1:
                            swap_hits[k].add((ei, a, f)); swap_ex[k][pairs_[0]] += 1
                        continue
                    if k == 'money':
                        mo = re.findall(r'\d{1,3}(?:\.\d{3})+', chg_o); mn = re.findall(r'\d{1,3}(?:\.\d{3})+', chg_n)
                        if mo and mn and len(mo) == len(mn) and all(int(y.replace('.', '')) > int(x.replace('.', '')) for x, y in zip(mo, mn)) and 'đồng' in ctx_n:
                            swap_hits[k].add((ei, a, f)); swap_ex[k][(chg_o, chg_n)] += 1
                            for x_, y_ in zip(mo, mn): money_ratio[round(int(y_.replace('.', '')) / int(x_.replace('.', '')), 2)] += 1
                        continue
                    mo, mn = ro.search(ctx_o), rn.search(ctx_n)
                    if mo and mn and not rn.search(ctx_o) and not ro.search(ctx_n):
                        # the old phrase must lie in the changed words or straddle them
                        so, eo = mo.span(); pre = len(' '.join(wa[max(0, i1 - 5):i1])) + (1 if i1 > 0 else 0)
                        if eo > pre - 1 and so < pre + len(chg_o) + 1:
                            swap_hits[k].add((ei, a, f)); swap_ex[k][(mo.group(0), mn.group(0))] += 1
        chg.append(rec)
    state[a] = cur
    if e['start'] and a not in first_files: first_files[a] = dict(cur)

head = state
assert sum(1 for a in head for f in head[a] if isart(f)) == sum(1 for l in open(os.path.join(B, 'head-tree.txt'), encoding='utf-8') if '/art-' in l)

# ------------------------------------------------------------------ per act measures (text in force, and as enacted)
DEL_GOV = re.compile(r'Chính phủ quy định|theo quy định của Chính phủ|Thủ tướng Chính phủ quy định', re.I)
DEL_MIN = re.compile(r'Bộ trưởng[^.;:]{0,90}?quy định(?! tại| của)|theo quy định của Bộ trưởng', re.I)
words_now = {}
for a in ACTS:
    words_now[a] = sum(len(BL.get(o).split()) for f, o in head[a].items() if isart(f))
arts_now = {a: sum(1 for f in head[a] if isart(f)) for a in ACTS}
TOTAL_WORDS = sum(words_now.values()); TOTAL_ARTS = sum(arts_now.values())


def enacted_stats(a):
    fl = first_files[a]
    lens, dg, dm = [], 0, 0
    for f, o in fl.items():
        if not isart(f): continue
        t = BL.get(o); body = t.split('\n', 1)[1] if '\n' in t else ''
        lens.append(len(body.split()))
        if DEL_GOV.search(body): dg += 1
        if DEL_MIN.search(body): dm += 1
    return lens, dg, dm


ENA = {a: enacted_stats(a) for a in ACTS}

# ------------------------------------------------------------------ helpers
cnt = collections.Counter
tl = collections.defaultdict(list)
for e in events: tl[e['act']].append(e)
lawsN = {k: r for k, r in laws.items()}


def law_label(k):
    m = lawnum(k)
    return m.group(0) if m else k


# amending law titles: which acts of the record does a title name?
def title_acts(k):
    t = norm(laws[k]['title'])
    hits = set()
    for a, (vi, en, fld) in ACTS.items():
        n = norm(re.sub(r'\s*\((19|20)\d\d\)$', '', vi))
        if a == 'hien-phap': n = 'hiến pháp'
        n = n.replace('luật sửa đổi luật tổ chức tòa án nhân dân', '@').replace('luật sửa đổi bộ luật hình sự', '@')
        if '@' in n or len(n) < 9: continue
        core = re.sub(r'^(bộ luật|luật) ', '', n)
        if re.search(r'(?<!\w)' + re.escape(core) + r'(?!\w)', t) and re.search(r'(bộ luật|luật)\s+' + re.escape(core), t): hits.add(a)
    return hits


def law_kind(k):
    """the kind of an amending law, from its title"""
    t = norm(laws[k]['title'])
    if k.startswith('nq-'): return 'resolution'
    if re.search(r'sửa đổi|bổ sung', t):
        if re.search(r'của\s+(\d+|các)\s+(bộ\s+)?luật', t): return 'omnibus'
        after = t.split(' của ', 1)[1] if ' của ' in t else t
        if len(re.findall(r'(?<!\w)(bộ luật|luật)(?!\w)', after)) >= 2: return 'omnibus'
        return 'amending'
    return 'other'


def named_count(k):
    t = NFC(laws[k]['title'])
    m = re.search(r'của\s+(\d+)\s+(?:bộ\s+)?luật', norm(t))
    if m: return int(m.group(1))
    t = norm(t)
    after = t.split(' của ', 1)[1] if ' của ' in t else ''
    return len(re.findall(r'(?<!\w)(?:bộ luật|luật)(?!\w)', after)) or None


def instrument(e):
    """how an amendment reached the act: its own amending law, an omnibus amending law, another law, a resolution"""
    k = e['law']
    if k.startswith('nq-'): return 'resolution'
    kind = law_kind(k)
    named = title_acts(k)
    if kind == 'amending' and e['act'] in named: return 'own'
    if kind in ('amending', 'omnibus') and re.search(r'(?<!\w)(dược|bảo hiểm y tế)\s+sửa đổi', norm(laws[k]['title'])): return 'own'
    if kind == 'omnibus': return 'omnibus'
    if re.search(r'sửa đổi \d{4}', norm(laws[k]['title'])) and e['act'] in named: return 'own'
    return 'other'


INSTR = {}
for e in AM: INSTR[id(e)] = instrument(e)

# ------------------------------------------------------------------ replacements inside the record (a later act's own repeal clause)
nkey = lambda s: (lambda m: f'{int(m.group(1))}/{m.group(2)}/{m.group(3).upper()}')(re.match(r'(\d+)/(\d{4})/(QH\d+)', s, re.I))
num2act = {nkey(acts[a]['num']): a for a in acts if acts[a]['num']}
replaced = {}   # act -> (successor, day): the successor's own text says the act "hết hiệu lực" from its day
for b in ACTS:
    for f, o in head[b].items():
        if not isart(f): continue
        t = BL.get(o)
        if 'hết hiệu lực' not in t: continue
        for sent in re.split(r'(?<=[.;])\s+|\n', t):
            if 'hết hiệu lực' not in sent: continue
            pre = sent.split('hết hiệu lực')[0]
            if re.search(r'(khoản|điểm|Điều|điều|Chương|chương)\s+[\dIVX]+[^.;]*của (Bộ luật|Luật)', pre): continue   # a partial repeal
            # the subject: the first act named with its number ("Luật Chứng khoán số 70/2006/QH11 ... hết hiệu lực")
            m = re.search(r'((?:Bộ luật|Luật)\s+[^,;]*?)\s+số\s+(\d+/\d{4}/QH\d+)', pre)
            if not m: continue
            a = num2act.get(nkey(m.group(2)))
            if not a or a == b or acts[a]['enacted'] >= acts[b]['enacted']: continue
            if norm(re.sub(r'\s*\((19|20)\d\d\)$', '', acts[a]['vi'])) != norm(m.group(1)).strip(): continue
            if re.search(r'kể từ ngày (Bộ luật|Luật) này có hiệu lực', sent): replaced[a] = (b, acts[b]['inforce'])
print('replaced inside the record:', {a: v for a, v in replaced.items()})

# ------------------------------------------------------------------ data for the charts
C = {}
TERMSPAN = {}
for k, r in laws.items():
    t = term_of_law(k)
    if t: TERMSPAN.setdefault(t, [r['enacted'][:4], r['enacted'][:4]]); TERMSPAN[t] = [min(TERMSPAN[t][0], r['enacted'][:4]), max(TERMSPAN[t][1], r['enacted'][:4])]

# c01: the record at a glance: every act sized by its words, by the term that adopted it
C['c01'] = {'acts': [[AIX[a], acts[a]['term'], acts[a]['kind'], words_now[a], arts_now[a]] for a in ORDER],
            'by_term': {t: sum(words_now[a] for a in ACTS if acts[a]['term'] == t) for t in TERMS}, 'total': TOTAL_WORDS}

# c02: sessions, from the laws' adoption days and numbers
closing = {}
for a in ACTS:
    o = head[a].get('ket-thuc.md')
    if not o: continue
    m = re.search(r'kh(?:óa|oá|oa)\s+([IVXLC]+)\s*,?\s*[Kk]ỳ họp\s+(bất thường\s+)?(?:lần\s+)?thứ\s+(\d+)', BL.get(o), re.I)
    if m: closing[acts[a]['enacted']] = (m.group(1), bool(m.group(2)), int(m.group(3)))
L = sorted((r for r in laws.values()), key=lambda r: r['enacted'])
clusters = []
for r in L:
    if clusters and (D(r['enacted']) - D(clusters[-1][-1]['enacted'])).days <= 40: clusters[-1].append(r)
    else: clusters.append([r])
actlaws = {acts[a]['law'] for a in acts}
sess = []
for c in clusters:
    term = collections.Counter(term_of_law(r['key']) for r in c if term_of_law(r['key'])).most_common(1)[0][0]
    nums = sorted(int(lawnum(r['key']).group(1)) for r in c if lawnum(r['key']) and not r['key'].startswith('nq-'))
    lab = collections.Counter(closing[r['enacted']] for r in c if r['enacted'] in closing).most_common(1)
    sess.append({'term': term, 'd0': c[0]['enacted'], 'd1': c[-1]['enacted'], 'nums': nums,
                 'acts': sum(1 for r in c if r['key'] in actlaws), 'amend': sum(1 for r in c if r['key'] not in actlaws and not r['key'].startswith('nq-')),
                 'res': sum(1 for r in c if r['key'].startswith('nq-')),
                 'label': [lab[0][0][1], lab[0][0][2]] if lab else None})
for t in TERMS:
    ss = [s for s in sess if s['term'] == t and s['nums']]
    prev_max = 0
    for s in ss:
        lo, hi = min(s['nums']), max(s['nums'])
        s['definite'] = hi - lo + 1           # numbers between the first and last law the record holds: adopted in this session
        s['unsure'] = lo - prev_max - 1        # numbers between the previous session's last and this one's first: either session
        s['lo'], s['hi'], s['prev'] = lo, hi, prev_max
        prev_max = hi
C['c02'] = {'sessions': [s for s in sess if s['term'] in ('QH13', 'QH14', 'QH15', 'QH16') and s['nums']],
            'termmax': {t: max([max(s['nums']) for s in sess if s['term'] == t and s['nums']] or [0]) for t in TERMS}, 'span': TERMSPAN}

# c03: the calendar of adoption and of entry into force
adopt = cnt((int(r['enacted'][5:7]), int(r['enacted'][8:10])) for r in laws.values())
vin = [(a, v['from']) for a, x in versions.items() for v in x['versions'] if v['from'] <= RECORD_TO]
inf = cnt((int(d[5:7]), int(d[8:10])) for a, d in vin)
C['c03'] = {'adopt': [[m, d, n] for (m, d), n in sorted(adopt.items())], 'inforce': [[m, d, n] for (m, d), n in sorted(inf.items())],
            'n_adopt': len(laws), 'n_inforce': len(vin), 'jan1': inf[(1, 1)], 'jul1': inf[(7, 1)],
            'adopt_months': {m: sum(n for (mm, d), n in adopt.items() if mm == m) for m in range(1, 13)}}

# c04: days from adoption to the first day in force
lag = []
for k, r in laws.items():
    fi = first_inforce(k)
    if not fi: continue
    lag.append([k, r['enacted'], fi, (D(fi) - D(r['enacted'])).days, 1 if k in actlaws else 0])
C['c04'] = {'laws': [[law_label(k), en, fi, d, isact, laws[k]['title'][:160]] for k, en, fi, d, isact in sorted(lag, key=lambda x: x[1])],
            'no_day': sum(1 for r in laws.values() if not first_inforce(r['key']))}

# c05: article changes by year and instrument
c05 = collections.defaultdict(cnt)
for e in AM:
    c05[e['inf'][:4]][INSTR[id(e)]] += nart(e)
C['c05'] = {'years': [[y, c05[y]['own'], c05[y]['omnibus'], c05[y]['other'], c05[y]['resolution']] for y in [str(x) for x in range(int(min(c05)), int(max(c05)) + 1)]],
            'events': {k: sum(1 for e in AM if INSTR[id(e)] == k) for k in ('own', 'omnibus', 'other', 'resolution')}}

# c06: the laws that changed the most acts of the record
pl = collections.defaultdict(lambda: {'acts': set(), 'arts': 0, 'days': set()})
for e in AM:
    p = pl[e['law']]; p['acts'].add(e['act']); p['arts'] += nart(e); p['days'].add(e['inf'])
top6 = sorted(pl, key=lambda k: (-len(pl[k]['acts']), -pl[k]['arts']))
C['c06'] = {'laws': [[law_label(k), laws[k]['enacted'], law_kind(k), named_count(k) if law_kind(k) == 'omnibus' else None, len(pl[k]['acts']), pl[k]['arts'],
                      sorted(AIX[a] for a in pl[k]['acts']), laws[k]['title'][:200], k] for k in top6[:16]],
            'n_laws': len(pl), 'multi': sum(1 for k in pl if len(pl[k]['acts']) > 1)}

# c07: time to the first amendment, by term (Kaplan-Meier: an act not yet amended counts until the record's date)
CENSOR = RETRIEVED
first_am = {}
for e in AM:
    first_am.setdefault(e['act'], e)
km = {}
GROUPS = {'g12': ['QH10', 'QH11', 'QH12'], 'QH13': ['QH13'], 'QH14': ['QH14'], 'QH15': ['QH15']}
for g, ts in GROUPS.items():
    obs = []
    for a in ACTS:
        if acts[a]['term'] not in ts: continue
        f = first_am.get(a)
        if f: obs.append(((D(f['inf']) - D(acts[a]['inforce'])).days, 1, a))
        else: obs.append(((D(CENSOR) - D(acts[a]['inforce'])).days, 0, a))
    obs.sort()
    n = len(obs); s = 1.0; steps = [[0, 1.0]]; i = 0
    while i < len(obs):
        t = obs[i][0]; dd = sum(1 for o in obs if o[0] == t and o[1]); cc = sum(1 for o in obs if o[0] == t)
        if dd: s *= (1 - dd / n); steps.append([t, s])
        n -= cc; i += cc
    med = next((t for t, v in steps if v <= 0.5), None)
    km[g] = {'n': len(obs), 'events': sum(o[1] for o in obs), 'steps': steps, 'median': med, 'maxt': max(o[0] for o in obs),
             'day0': [AIX[o[2]] for o in obs if o[1] and o[0] == 0]}
C['c07'] = {'km': km, 'censor': CENSOR,
            'day0': [[AIX[a], first_am[a]['law'] and law_label(first_am[a]['law']), first_am[a]['inf']] for a in ORDER if a in first_am and first_am[a]['inf'] == acts[a]['inforce']]}

# c08: article changes by field and year
c08 = collections.defaultdict(cnt)
for e in AM: c08[acts[e['act']]['field']][e['inf'][:4]] += nart(e)
YEARS = [str(y) for y in range(int(min(e['inf'] for e in AM)[:4]), int(max(e['inf'] for e in AM)[:4]) + 1)]
C['c08'] = {'years': YEARS, 'rows': {f: [c08[f][y] for y in YEARS] for f in FIELDS},
            'acts': {f: sum(1 for a in ACTS if acts[a]['field'] == f) for f in FIELDS}}

# c09: who wrote the text in force (by line)
auth = collections.defaultdict(cnt)
for (a, f), lines in blame.items():
    for l, k in lines: auth[a][k] += len(l.split())
def period(k):
    y = (first_inforce(k) or laws[k]['enacted'])[:4]
    return 'p1' if y < '2021' else 'p2' if y < '2025' else 'p3'
c09 = []
for a in ACTS:
    tot = sum(auth[a].values()); orig = auth[a][acts[a]['law']]
    per = cnt()
    for k, v in auth[a].items():
        if k != acts[a]['law']: per[period(k)] += v
    c09.append([AIX[a], tot, orig, per['p1'], per['p2'], per['p3'], [[law_label(k), v] for k, v in auth[a].most_common() if k != acts[a]['law']][:4]])
amended_words = sum(r[1] - r[2] for r in c09)
C['c09'] = {'acts': sorted([r for r in c09 if ORDER[r[0]] not in WRONG_TEXT], key=lambda r: -(r[1] - r[2]) / r[1])[:16],
            'codes': [r for r in c09 if acts[ORDER[r[0]]]['kind'] != 'law'], 'total': TOTAL_WORDS, 'amended': amended_words,
            'over_half': sum(1 for r in c09 if (r[1] - r[2]) / r[1] > .5 and ORDER[r[0]] not in WRONG_TEXT),
            'none': sum(1 for r in c09 if r[1] == r[2])}

# c10: the Constitution, article by article
HP_CH = [(1, 'I', 'Nước Cộng hòa xã hội chủ nghĩa Việt Nam là'), (14, 'II', 'Ở nước Cộng hòa xã hội chủ nghĩa Việt Nam, các quyền con người'),
         (50, 'III', 'Nước Cộng hòa xã hội chủ nghĩa Việt Nam xây dựng nền kinh tế'), (64, 'IV', 'Bảo vệ Tổ quốc'), (69, 'V', 'Quốc hội là cơ quan đại biểu cao nhất'),
         (86, 'VI', 'Chủ tịch nước là người đứng đầu Nhà nước'), (94, 'VII', 'Chính phủ là cơ quan hành chính nhà nước cao nhất'),
         (102, 'VIII', 'Tòa án nhân dân là cơ quan xét xử'), (110, 'IX', 'Các đơn vị hành chính'), (117, 'X', 'Hội đồng bầu cử quốc gia'),
         (119, 'XI', 'Hiến pháp là luật cơ bản')]
hp = head['hien-phap']; hp_am = {f for e in AM if e['act'] == 'hien-phap' for st, f, o, n in e['ch']}
hp_struct = BL.get(hp['cau-truc.md'])
ch_names = re.findall(r'(?m)^Chương\s+([IVX]+)\s+(.+)$', hp_struct)
rows10 = []
for f in sorted(f for f in hp if isart(f)):
    n = int(re.match(r'art-(\d+)', f).group(1)); t = hp[f]
    ch = [c for c in HP_CH if c[0] <= n][-1][1]
    rows10.append([n, ch, len(BL.get(t).split('\n', 1)[1].split()), 1 if f in hp_am else 0, BL.get(t).split('\n', 1)[1][:150]])
for n0, ch, start in HP_CH:   # the first article of each chapter begins as written here
    body = next(r for r in rows10 if r[0] == n0)[4]
    assert norm(start) in norm(body), (n0, body[:80])
nq203 = next(e for e in AM if e['act'] == 'hien-phap')
C['c10'] = {'arts': [r[:4] for r in rows10], 'chapters': [[c, NFC(nm).strip()] for c, nm in ch_names], 'law': law_label(nq203['law']), 'day': nq203['inf'],
            'enacted': laws[nq203['law']]['enacted'], 'words': sum(r[2] for r in rows10)}

# c11: the constitution each act's preamble cites
def basis(a):
    p = norm(BL.get(head[a]['loi-mo-dau.md'])) if 'loi-mo-dau.md' in head[a] else ''
    if a == 'hien-phap': return 'self'
    if '203/2025' in p: return 'c2025'
    if '1992' in p and '51/2001' in p: return 'c2001'
    if '1992' in p: return 'c1992'
    if 'hiến pháp' in p: return 'c2013'
    return 'none'
C['c11'] = {'acts': [[AIX[a], acts[a]['enacted'], basis(a)] for a in ORDER]}

# c12: the Constitution and the six codes
c12 = []
for a in ORDER:
    if acts[a]['kind'] == 'law': continue
    ev = [e for e in AM if e['act'] == a]
    vs = [v['from'] for v in versions[a]['versions']]
    changed = {f for e in ev for st, f, o, n in e['ch'] if isart(f)}
    tot = sum(auth[a].values())
    c12.append({'i': AIX[a], 'arts': arts_now[a], 'arts0': sum(1 for f in first_files[a] if isart(f)), 'words': words_now[a], 'versions': len([v for v in vs if v <= RECORD_TO]),
                'future': len([v for v in vs if v > RECORD_TO]), 'laws': len({e['law'] for e in ev}), 'amended_share': (tot - auth[a][acts[a]['law']]) / tot,
                'changed': len(changed), 'modified': len({f for e in ev for st, f, o, n in e['ch'] if isart(f) and st == 'M'}), 'inserted': sum(1 for e in ev for st, f, o, n in e['ch'] if isart(f) and st == 'A'),
                'removed': sum(1 for e in ev for st, f, o, n in e['ch'] if isart(f) and st == 'D'),
                'steps': [[e['inf'], law_label(e['law']), nart(e)] for e in ev], 'inforce': acts[a]['inforce'], 'enacted': acts[a]['enacted']})
C['c12'] = c12

# c13 + c14: the Penal Code, crime by crime
PEN_CH = [(108, 'XIII', 'Tội phản bội Tổ quốc'), (123, 'XIV', 'Tội giết người'), (157, 'XV', 'Tội bắt, giữ hoặc giam người trái pháp luật'),
          (168, 'XVI', 'Tội cướp tài sản'), (181, 'XVII', 'Tội cưỡng ép kết hôn'), (188, 'XVIII', 'Tội buôn lậu'), (235, 'XIX', 'Tội gây ô nhiễm môi trường'),
          (247, 'XX', 'Tội trồng cây thuốc phiện'), (260, 'XXI', 'Tội vi phạm quy định về tham gia giao thông đường bộ'), (330, 'XXII', 'Tội chống người thi hành công vụ'),
          (352, 'XXIII', None), (367, 'XXIV', None), (392, 'XXV', None), (421, 'XXVI', 'Tội phá hoại hòa bình')]
YRS = re.compile(r'phạt tù(?: từ \d+ (?:năm|tháng))? đến (\d+) năm|phạt tù (\d+) năm')


def maxpen(body):
    best, yrs = -1, 0
    for l in body.split('\n'):
        if 'pháp nhân thương mại' in l and 'người' not in l: continue
        if re.search(r'hoặc tử hình|, tử hình', l): best = max(best, 7)
        elif 'tù chung thân' in l: best = max(best, 6)
        for m in YRS.finditer(l): yrs = max(yrs, int(m.group(1) or m.group(2)))
        if re.search(r'phạt tù (?:từ \d+ tháng )?đến \d+ tháng', l): yrs = max(yrs, .5)
        if re.search(r'cải tạo không giam giữ|phạt tiền|cảnh cáo', l): best = max(best, 0)
    if best >= 6: return best
    if yrs: return 1 if yrs <= 3 else 2 if yrs <= 7 else 3 if yrs <= 15 else 4 if yrs <= 20 else 5
    return 0 if best == 0 else None


def crimes(files):
    out = []
    for f, o in files.items():
        if not isart(f): continue
        t = BL.get(o); m = re.match(r'#\s*Điều\s+(\d+)([a-z]?)\.\s*(.*)', t)
        if not m: continue
        n = int(m.group(1))
        if n < 108 or n > 425 or not m.group(3).startswith('Tội'): continue
        ch = [c for c in PEN_CH if c[0] <= n][-1][1]
        out.append([n, m.group(2), ch, maxpen(t.split('\n', 1)[1]), m.group(3)])
    return sorted(out)


blhs_tl = [e for e in events if e['act'] == 'bo-luat-hinh-su']
def blhs_on(day):
    st = {}
    for e in blhs_tl:
        if e['inf'] > day: break
        for s_, f, o, n in e['ch']:
            if s_ == 'D': st.pop(f, None)
            else: st[f] = n
    return st
for n0, ch, title in PEN_CH:   # each chapter begins with the crime written here
    if title: assert any(c[0] == n0 and c[4].startswith(title) for c in crimes(head['bo-luat-hinh-su'])), (n0, title)
now_cr = crimes(head['bo-luat-hinh-su'])
assert all(c[3] is not None for c in now_cr)
pen_ch = re.findall(r'(?m)^Chương\s+([IVX]+)\s+(.+)$', BL.get(head['bo-luat-hinh-su']['cau-truc.md']))
C['c13'] = {'rows': [[ch, [sum(1 for c in now_cr if c[2] == ch and c[3] == k) for k in range(8)]] for n0, ch, t in PEN_CH],
            'chapters': {c: NFC(nm).strip() for c, nm in pen_ch}, 'n': len(now_cr), 'day': max(e['inf'] for e in blhs_tl)}
before = blhs_on(acts['bo-luat-hinh-su']['inforce'])
cr0 = {c[0]: c for c in crimes(before)}
cap0 = [c for c in cr0.values() if c[3] == 7]
cap_now = {c[0] for c in now_cr if c[3] == 7}
first25 = next(e for e in blhs_tl if e['inf'] >= '2025-01-01')
C['c14'] = {'crimes': [[c[0], c[2], c[4], 1 if c[0] in cap_now else 0, next((x[3] for x in now_cr if x[0] == c[0]), None)] for c in sorted(cap0)],
            'day': first25['inf'], 'law': law_label(first25['law']), 'enacted': laws[first25['law']]['enacted'], 'n_crimes': len(now_cr),
            'life_now': sum(1 for c in now_cr if c[3] == 6), 'life_before': sum(1 for c in cr0.values() if c[3] == 6)}

# c15: the days that changed most of the record
DAYS = ['2025-07-01', '2026-01-01', '2026-07-01']
c15 = {}
for day in DAYS:
    st = []
    for a in ORDER:
        if acts[a]['inforce'] > day: s = 'later'
        elif a in replaced and replaced[a][1] <= day: s = 'replaced'
        elif acts[a]['inforce'] == day: s = 'new'
        elif any(e['inf'] == day for e in AM if e['act'] == a): s = 'amended'
        else: s = 'same'
        st.append(s)
    c15[day] = {'status': st, 'laws': len({e['law'] for e in AM if e['inf'] == day}), 'arts': sum(nart(e) for e in AM if e['inf'] == day)}
C['c15'] = {'days': DAYS, 'by_day': c15, 'fields': [acts[a]['field'] for a in ORDER]}

# c16 + c17: phrases in the articles in force, at each day something changed (acts replaced inside the record leave the count
# on the day their successor takes effect)
series = []; acc = cnt()
for day in sorted(set(ph_delta) | {d for b, d in replaced.values()}):
    acc.update(ph_delta.get(day, {}))
    series.append([day, dict(acc)])
# subtract the replaced acts' articles from their successor's day on, with the flags they held then
for a, (b, day) in replaced.items():
    held = cnt()
    # the act's flags on that day (replaced acts change no more after their successor; checked)
    assert all(e['inf'] < day for e in tl[a]), a
    for f, o in head[a].items():
        if not isart(f): continue
        fl = phflags(BL.get(o))
        for k in PH:
            if fl[k]: held[k] += 1
            held[k + '#'] += fl[k]
    for row in series:
        if row[0] >= day:
            for k, v in held.items(): row[1][k] = row[1].get(k, 0) - v
keys = list(PH)
C['c16'] = {'series': [[d, s.get('huyen', 0), s.get('xa', 0), s.get('kv', 0), s.get('huyen#', 0)] for d, s in series if d >= '2014-01-01'],
            'acts_huyen_now': sum(1 for a in ACTS if a not in replaced and any(isart(f) and PHX['huyen'].search(BL.get(o)) for f, o in head[a].items())),
            'amend_day': C['c10']['day']}
C['c17'] = {'keys': ['MONRE', 'MARD', 'MOT', 'MPI', 'MOLISA', 'MIC', 'MAE'],
            'series': [[d] + [s.get(k, 0) for k in ['MONRE', 'MARD', 'MOT', 'MPI', 'MOLISA', 'MIC', 'MAE']] for d, s in series if d >= '2014-01-01']}

# c18 + c19: length and delegation of articles as enacted, by term
c18 = {}
for t in TERMS:
    A = [a for a in ACTS if acts[a]['term'] == t and a not in WRONG_TEXT and a not in AMENDING_ACTS]
    if not A: continue
    lens = [x for a in A for x in ENA[a][0]]
    c18[t] = {'acts': len(A), 'arts': len(lens), 'median': statistics.median(lens), 'mean': sum(lens) / len(lens),
              'bins': [sum(1 for x in lens if lo <= x < hi) for lo, hi in [(0, 100), (100, 200), (200, 400), (400, 800), (800, 10 ** 9)]],
              'gov': sum(ENA[a][1] for a in A), 'min': sum(ENA[a][2] for a in A),
              'acts_list': [[AIX[a], len(ENA[a][0]), ENA[a][1], ENA[a][2], statistics.median(ENA[a][0])] for a in A]}
C['c18'] = c18

# c20: the edits amendments make
shares = [r['share'] for r in chg if 'share' in r]
C['c20'] = {'swaps': [[k, th, len(swap_hits[k]), len({(x[1]) for x in swap_hits[k]}), swap_ex[k].most_common(4), len({(x[1], x[2]) for x in swap_hits[k]})] for k, th, o, n in SWAPS],
            'bins': [sum(1 for x in shares if lo <= x < hi) for lo, hi in [(0, .02), (.02, .05), (.05, .1), (.1, .25), (.25, .5), (.5, .75), (.75, 1.01)]],
            'n': len(shares), 'median': statistics.median(shares), 'money_ratio': sorted(money_ratio.items()),
            'money_acts': sorted({AIX[x[1]] for x in swap_hits['money']}),
            'by_period': {p: statistics.median([r['share'] for r in chg if 'share' in r and (r['y'] >= '2025') == (p == 'late')]) for p in ('early', 'late')},
            'n_period': {p: sum(1 for r in chg if 'share' in r and (r['y'] >= '2025') == (p == 'late')) for p in ('early', 'late')}}

# ------------------------------------------------------------------ profile and the acts table
nver = sum(1 for a in versions for v in versions[a]['versions'] if v['from'] <= RECORD_TO)
nfut = sum(1 for a in versions for v in versions[a]['versions'] if v['from'] > RECORD_TO)
PF = {'built': (commits[-1]['ad'][:10] if commits else ''), 'head': HEAD, 'retrieved': RETRIEVED, 'record_to': RECORD_TO,
      'record_from': min(e['inf'] for e in events), 'acts': len(ACTS), 'codes': sum(1 for a in ACTS if acts[a]['kind'] == 'code'),
      'laws_only': sum(1 for a in ACTS if acts[a]['kind'] == 'law'), 'articles': TOTAL_ARTS, 'words': TOTAL_WORDS, 'versions': nver, 'future': nfut,
      'law_commits': sum(1 for c in commits if c['t'].get('Kind', [''])[0] == 'law'), 'commits': len(commits), 'laws': len(laws),
      'amending_laws': len(pl), 'art_changes': len([r for r in chg]), 'modified': sum(1 for r in chg if r['st'] == 'M'),
      'inserted': sum(1 for r in chg if r['st'] == 'A'), 'removed': sum(1 for r in chg if r['st'] == 'D'), 'am_events': len(AM),
      'replaced': [[AIX[a], AIX[b], d] for a, (b, d) in sorted(replaced.items(), key=lambda x: x[1][1])],
      'wrong': sorted(AIX[a] for a in WRONG_TEXT), 'amending_acts': sorted(AIX[a] for a in AMENDING_ACTS),
      'by_kind': cnt(acts[a]['kind'] for a in ACTS), 'never_amended': sum(1 for a in ACTS if a not in first_am)}
A_TABLE = [[acts[a]['vi'], acts[a]['en'], acts[a]['num'], acts[a]['term'], acts[a]['enacted'], acts[a]['inforce'], acts[a]['field'], acts[a]['kind'],
            words_now[a], arts_now[a], len([v for v in versions[a]['versions'] if v['from'] <= RECORD_TO]), paths[a]] for a in ORDER]
# display names of the laws: an act of the record keeps its name; an amending law of one act is "the law amending <act>";
# an omnibus law "the law amending N laws"; the others named here by hand, or by their number
LAWN = {
 '116/2025/QH15': ['Luật An ninh mạng (2025)', 'Cybersecurity Law (2025)'],
 '35/2018/QH14': ['Luật sửa đổi 37 luật liên quan đến quy hoạch', 'Law amending 37 laws on planning'],
 '28/2018/QH14': ['Luật sửa đổi 11 luật liên quan đến quy hoạch', 'Law amending 11 laws on planning'],
 '112/2025/QH15': ['Luật Quy hoạch (2025)', 'Planning Law (2025)'],
 '84/2025/QH15': ['Luật Thanh tra (2025)', 'Inspection Law (2025)'],
 '146/2025/QH15': ['Luật sửa đổi 15 luật về nông nghiệp và môi trường', 'Law amending 15 laws on agriculture and the environment'],
 '98/2025/QH15': ['Luật sửa đổi 11 luật về quân sự, quốc phòng', 'Law amending 11 laws on the military and defence'],
 '14/2026/QH16': ['Luật sửa đổi 9 luật về quân sự, quốc phòng', 'Law amending 9 laws on the military and defence'],
 '142/2025/QH15': ['Luật Phục hồi, phá sản (2025)', 'Law on Rehabilitation and Bankruptcy (2025)'],
 '118/2025/QH15': ['Luật sửa đổi 10 luật về an ninh, trật tự', 'Law amending 10 laws on security and order'],
 '47/2024/QH15': ['Luật Quy hoạch đô thị và nông thôn (2024)', 'Law on Urban and Rural Planning (2024)'],
 '133/2025/QH15': ['Luật Công nghệ cao (2025)', 'Law on High Technologies (2025)'],
 '90/2025/QH15': ['Luật sửa đổi 8 luật về đấu thầu, đầu tư, hải quan và thuế', 'Law amending 8 laws on bidding, investment, customs and tax'],
 '56/2024/QH15': ['Luật sửa đổi 9 luật về chứng khoán, kế toán, ngân sách và thuế', 'Law amending 9 laws on securities, accounting, the budget and tax'],
 '59/2024/QH15': ['Luật Tư pháp người chưa thành niên (2024)', 'Law on Juvenile Justice (2024)'],
 '85/2025/QH15': ['Luật sửa đổi 5 luật về tố tụng và hòa giải tại Tòa án', 'Law amending 5 laws on court procedure and mediation'],
 '97/2025/QH15': ['Luật sửa đổi các luật về Mặt trận, Công đoàn, Thanh niên và dân chủ ở cơ sở', 'Law amending the laws on the Fatherland Front, trade unions, youth and grassroots democracy'],
 '43/2024/QH15': ['Luật sửa đổi Luật Đất đai, Luật Nhà ở, Luật Kinh doanh bất động sản và Luật Các tổ chức tín dụng', 'Law amending the Land, Housing, Real Estate Business and Credit Institutions Laws'],
 '31/2024/QH15': ['Luật Đất đai (2024)', 'Land Law (2024)'], '61/2020/QH14': ['Luật Đầu tư (2020)', 'Law on Investment (2020)'],
 '67/2014/QH13': ['Luật Đầu tư (2014)', 'Law on Investment (2014)'], '97/2015/QH13': ['Luật Phí và lệ phí (2015)', 'Law on Fees and Charges (2015)'],
 '71/2014/QH13': ['Luật sửa đổi các luật về thuế (2014)', 'Law amending the tax laws (2014)'],
 '42/2019/QH14': ['Luật sửa đổi Luật Kinh doanh bảo hiểm và Luật Sở hữu trí tuệ (2019)', 'Law amending the Insurance Business and Intellectual Property Laws (2019)'],
 '03/2022/QH15': ['Luật sửa đổi 9 luật về đầu tư và kinh doanh (2022)', 'Law amending 9 laws on investment and business (2022)'],
 '09/2026/QH16': ['Luật sửa đổi 4 luật thuế (2026)', 'Law amending 4 tax laws (2026)'],
 '124/2025/QH15': ['Luật Giáo dục nghề nghiệp (2025)', 'Law on Vocational Education (2025)'],
 '113/2025/QH15': ['Luật Dân số (2025)', 'Law on Population (2025)'], '71/2025/QH15': ['Luật Công nghiệp công nghệ số (2025)', 'Law on the Digital Technology Industry (2025)'],
 '103/2025/QH15': ['Luật Tương trợ tư pháp về hình sự (2025)', 'Law on Mutual Legal Assistance in Criminal Matters (2025)'],
 '105/2025/QH15': ['Luật Giám định tư pháp (2025)', 'Law on Judicial Expertise (2025)'], '106/2025/QH15': ['Luật Thi hành án dân sự (2025)', 'Law on Civil Judgment Enforcement (2025)'],
 '128/2025/QH15': ['Luật Thi hành tạm giữ, tạm giam và cấm đi khỏi nơi cư trú (2025)', 'Law on Custody, Temporary Detention and Travel Bans (2025)'],
 '34/2024/QH15': ['Luật Tổ chức Tòa án nhân dân (2024)', 'Law on the Organisation of People’s Courts (2024)'],
 '02/2021/QH15': ['Luật sửa đổi Bộ luật Tố tụng hình sự (2021)', 'Law amending the Criminal Procedure Code (2021)'],
 '13/2022/QH15': ['Luật Phòng, chống bạo lực gia đình (2022)', 'Law on Domestic Violence Prevention (2022)'],
 '19/2023/QH15': ['Luật Bảo vệ quyền lợi người tiêu dùng (2023)', 'Law on Consumer Protection (2023)'],
 '46/2024/QH15': ['Luật Công chứng (2024)', 'Law on Notarisation (2024)'], '16/2023/QH15': ['Luật Giá (2023)', 'Law on Prices (2023)'],
 '203/2025/QH15': ['Nghị quyết 203/2025/QH15 sửa đổi Hiến pháp', 'Resolution 203/2025/QH15 amending the Constitution'],
 '45/2013/QH13': ['Nghị quyết 45/2013/QH13', 'Resolution 45/2013/QH13'],
}
strip_year = lambda s: re.sub(r'\s*\((19|20)\d\d\)$', '', s)
lawn = {}
act_by_law = {acts[a]['law']: a for a in acts}
for k in laws:
    lab = law_label(k); y = laws[k]['enacted'][:4]
    if lab in LAWN: lawn[lab] = LAWN[lab]; continue
    if k in act_by_law:
        a = act_by_law[k]; lawn[lab] = [acts[a]['vi'], acts[a]['en']]; continue
    kind = law_kind(k); named = title_acts(k)
    if kind == 'amending' and len(named) == 1:
        a = next(iter(named)); lawn[lab] = [f"Luật sửa đổi {strip_year(acts[a]['vi'])} ({y})", f"Law amending the {strip_year(acts[a]['en'])} ({y})"]
    elif kind == 'omnibus' and named_count(k):
        lawn[lab] = [f'Luật sửa đổi {named_count(k)} luật ({y})', f'Law amending {named_count(k)} laws ({y})']
    elif k.startswith('nq-'):
        lawn[lab] = [f'Nghị quyết {lab}', f'Resolution {lab}']
    else:
        lawn[lab] = [f'Luật {lab}', f'Law No. {lab}']
LAWS_T = {law_label(k): [laws[k]['title'][:200], laws[k]['enacted'], first_inforce(k)] + lawn[law_label(k)] for k in laws}
out = {'profile': PF, 'charts': C, 'acts': A_TABLE, 'fields': FIELDS, 'terms': TERMS, 'laws': LAWS_T}
json.dump(out, open(os.path.join(B, 'data.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('data.json', os.path.getsize(os.path.join(B, 'data.json')), 'bytes; words', TOTAL_WORDS, 'articles', TOTAL_ARTS)
