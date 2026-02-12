"""
처방일수 계산기 (Prescription Day Calculator)
- 다음 외래일 입력 → 처방일수 계산
- 처방일수 입력 → 약 소진일 계산
Windows에서 Python 3.x + tkinter로 실행 가능
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sys

# ---------------------------------------------------------------------------
# 날짜 파싱 유틸리티
# ---------------------------------------------------------------------------

def parse_korean_date(text: str) -> datetime:
    """다양한 한국식 날짜 포맷을 파싱한다.

    지원 형식:
        2026년 2월 15일 / 2026년2월15일
        2026.02.15 / 2026.2.15
        2026-02-15 / 2026-2-15
        2026/02/15 / 2026/2/15
        20260215 (숫자 8자리)
    """
    text = text.strip()

    # 숫자 8자리 (예: 20260315)
    if text.isdigit() and len(text) == 8:
        return datetime.strptime(text, "%Y%m%d")

    # "년", "월", "일" 포맷
    for fmt in ("%Y년 %m월 %d일", "%Y년%m월%d일",
                "%Y년 %m월%d일", "%Y년%m월 %d일"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    # 구분자 기반 포맷
    for fmt in ("%Y.%m.%d", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    raise ValueError(f"날짜를 인식할 수 없습니다: {text}")


def format_korean_date(dt: datetime) -> str:
    """datetime → '2026년 2월 15일 (일)' 형태 문자열"""
    weekday_kr = ["월", "화", "수", "목", "금", "토", "일"]
    wd = weekday_kr[dt.weekday()]
    return f"{dt.year}년 {dt.month}월 {dt.day}일 ({wd})"


# ---------------------------------------------------------------------------
# GUI 애플리케이션
# ---------------------------------------------------------------------------

class PrescriptionCalculator(tk.Tk):
    BG = "#F5F7FA"
    CARD_BG = "#FFFFFF"
    PRIMARY = "#2563EB"
    PRIMARY_HOVER = "#1D4ED8"
    SUCCESS = "#059669"
    TEXT = "#1E293B"
    TEXT_LIGHT = "#64748B"
    BORDER = "#E2E8F0"
    RESULT_BG = "#EFF6FF"
    RESULT_BG2 = "#ECFDF5"
    FONT_FAMILY = "맑은 고딕"
    WARN_COLOR = "#DC2626"

    def __init__(self):
        super().__init__()
        self.title("처방일수 계산기")
        self.configure(bg=self.BG)
        self.resizable(False, False)

        # 화면 중앙 배치
        w, h = 520, 700
        sx = self.winfo_screenwidth() // 2 - w // 2
        sy = self.winfo_screenheight() // 2 - h // 2
        self.geometry(f"{w}x{h}+{sx}+{sy}")

        self._build_styles()
        self._build_ui()

        # 키보드 바인딩
        self.bind("<Return>", lambda e: self._on_enter(e))

    # ----- 스타일 ---------------------------------------------------------

    def _build_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("Card.TFrame", background=self.CARD_BG)
        style.configure("BG.TFrame", background=self.BG)
        style.configure(
            "Title.TLabel",
            background=self.BG,
            foreground=self.TEXT,
            font=(self.FONT_FAMILY, 18, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.BG,
            foreground=self.TEXT_LIGHT,
            font=(self.FONT_FAMILY, 9),
        )
        style.configure(
            "Section.TLabel",
            background=self.CARD_BG,
            foreground=self.PRIMARY,
            font=(self.FONT_FAMILY, 11, "bold"),
        )
        style.configure(
            "Desc.TLabel",
            background=self.CARD_BG,
            foreground=self.TEXT_LIGHT,
            font=(self.FONT_FAMILY, 9),
        )
        style.configure(
            "Result.TLabel",
            background=self.RESULT_BG,
            foreground=self.TEXT,
            font=(self.FONT_FAMILY, 13, "bold"),
        )
        style.configure(
            "Result2.TLabel",
            background=self.RESULT_BG2,
            foreground=self.TEXT,
            font=(self.FONT_FAMILY, 13, "bold"),
        )
        style.configure(
            "ResultSub.TLabel",
            background=self.RESULT_BG,
            foreground=self.TEXT_LIGHT,
            font=(self.FONT_FAMILY, 9),
        )
        style.configure(
            "ResultSub2.TLabel",
            background=self.RESULT_BG2,
            foreground=self.TEXT_LIGHT,
            font=(self.FONT_FAMILY, 9),
        )
        style.configure(
            "Warn.TLabel",
            background=self.CARD_BG,
            foreground=self.WARN_COLOR,
            font=(self.FONT_FAMILY, 9),
        )

    # ----- UI 빌드 --------------------------------------------------------

    def _build_ui(self):
        container = ttk.Frame(self, style="BG.TFrame")
        container.pack(fill="both", expand=True, padx=20, pady=15)

        # 제목
        ttk.Label(container, text="처방일수 계산기", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            container,
            text="다음 외래일 또는 처방일수를 입력하여 계산합니다",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 12))

        # 오늘 날짜 표시
        today = datetime.today()
        today_str = format_korean_date(today)
        ttk.Label(
            container,
            text=f"오늘: {today_str}",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(0, 10))

        # ── 카드 1: 다음 외래일 → 처방일수 ──
        card1 = self._card(container)

        ttk.Label(card1, text="다음 외래일 → 처방일수", style="Section.TLabel").pack(
            anchor="w", padx=15, pady=(15, 2)
        )
        ttk.Label(
            card1,
            text="다음 외래 날짜를 입력하면 오늘부터 며칠치를 처방해야 하는지 계산합니다",
            style="Desc.TLabel",
        ).pack(anchor="w", padx=15, pady=(0, 8))

        row1 = ttk.Frame(card1, style="Card.TFrame")
        row1.pack(fill="x", padx=15, pady=(0, 5))

        ttk.Label(row1, text="다음 외래일:", background=self.CARD_BG,
                  font=(self.FONT_FAMILY, 10)).pack(side="left")

        self.entry_date = tk.Entry(
            row1, font=(self.FONT_FAMILY, 12), width=22,
            relief="solid", bd=1,
        )
        self.entry_date.pack(side="left", padx=(8, 0), ipady=4)
        self.entry_date.insert(0, "예: 2026.03.15")
        self.entry_date.config(fg="grey")
        self.entry_date.bind("<FocusIn>", lambda e: self._clear_placeholder(self.entry_date, "예: 2026.03.15"))
        self.entry_date.bind("<FocusOut>", lambda e: self._set_placeholder(self.entry_date, "예: 2026.03.15"))

        ttk.Label(
            card1,
            text="지원 형식: 2026년 3월 15일, 2026.03.15, 2026-03-15, 20260315",
            style="Desc.TLabel",
        ).pack(anchor="w", padx=15, pady=(0, 4))

        # 여유분 옵션
        margin_row = ttk.Frame(card1, style="Card.TFrame")
        margin_row.pack(fill="x", padx=15, pady=(0, 8))

        ttk.Label(margin_row, text="여유분:", background=self.CARD_BG,
                  font=(self.FONT_FAMILY, 10)).pack(side="left")
        self.margin_var = tk.IntVar(value=0)
        margin_spin = tk.Spinbox(
            margin_row, from_=0, to=30, width=5,
            textvariable=self.margin_var,
            font=(self.FONT_FAMILY, 11), relief="solid", bd=1,
        )
        margin_spin.pack(side="left", padx=(8, 4))
        ttk.Label(margin_row, text="일", background=self.CARD_BG,
                  font=(self.FONT_FAMILY, 10)).pack(side="left")

        btn1 = tk.Button(
            card1, text="처방일수 계산", bg=self.PRIMARY, fg="white",
            font=(self.FONT_FAMILY, 11, "bold"), relief="flat",
            activebackground=self.PRIMARY_HOVER, activeforeground="white",
            cursor="hand2", command=self._calc_days,
        )
        btn1.pack(fill="x", padx=15, pady=(0, 10), ipady=6)

        # 결과 영역 1
        self.result_frame1 = tk.Frame(card1, bg=self.RESULT_BG, highlightthickness=0)
        self.result_frame1.pack(fill="x", padx=15, pady=(0, 15))
        self.result_frame1.pack_forget()

        self.result_label1 = ttk.Label(self.result_frame1, text="", style="Result.TLabel")
        self.result_label1.pack(anchor="w", padx=12, pady=(10, 2))
        self.result_sub1 = ttk.Label(self.result_frame1, text="", style="ResultSub.TLabel")
        self.result_sub1.pack(anchor="w", padx=12, pady=(0, 10))

        # ── 카드 2: 처방일수 → 약 소진일 ──
        card2 = self._card(container)

        ttk.Label(card2, text="처방일수 → 약 소진일", style="Section.TLabel").pack(
            anchor="w", padx=15, pady=(15, 2)
        )
        ttk.Label(
            card2,
            text="처방일수를 입력하면 약이 소진되는 날짜를 계산합니다",
            style="Desc.TLabel",
        ).pack(anchor="w", padx=15, pady=(0, 8))

        row2 = ttk.Frame(card2, style="Card.TFrame")
        row2.pack(fill="x", padx=15, pady=(0, 8))

        ttk.Label(row2, text="처방일수:", background=self.CARD_BG,
                  font=(self.FONT_FAMILY, 10)).pack(side="left")

        self.entry_days = tk.Entry(
            row2, font=(self.FONT_FAMILY, 12), width=10,
            relief="solid", bd=1,
        )
        self.entry_days.pack(side="left", padx=(8, 4), ipady=4)

        ttk.Label(row2, text="일", background=self.CARD_BG,
                  font=(self.FONT_FAMILY, 10)).pack(side="left")

        btn2 = tk.Button(
            card2, text="소진일 계산", bg=self.SUCCESS, fg="white",
            font=(self.FONT_FAMILY, 11, "bold"), relief="flat",
            activebackground="#047857", activeforeground="white",
            cursor="hand2", command=self._calc_end_date,
        )
        btn2.pack(fill="x", padx=15, pady=(0, 10), ipady=6)

        # 결과 영역 2
        self.result_frame2 = tk.Frame(card2, bg=self.RESULT_BG2, highlightthickness=0)
        self.result_frame2.pack(fill="x", padx=15, pady=(0, 15))
        self.result_frame2.pack_forget()

        self.result_label2 = ttk.Label(self.result_frame2, text="", style="Result2.TLabel")
        self.result_label2.pack(anchor="w", padx=12, pady=(10, 2))
        self.result_sub2 = ttk.Label(self.result_frame2, text="", style="ResultSub2.TLabel")
        self.result_sub2.pack(anchor="w", padx=12, pady=(0, 10))

    def _card(self, parent) -> ttk.Frame:
        """둥근 느낌의 카드 프레임 생성"""
        wrapper = tk.Frame(parent, bg=self.BORDER, bd=0, highlightthickness=0)
        wrapper.pack(fill="x", pady=(0, 12))
        card = ttk.Frame(wrapper, style="Card.TFrame")
        card.pack(fill="x", padx=1, pady=1)
        return card

    # ----- Placeholder 처리 -----------------------------------------------

    def _clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, "end")
            entry.config(fg="black")

    def _set_placeholder(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg="grey")

    # ----- Enter 키 처리 --------------------------------------------------

    def _on_enter(self, event):
        focused = self.focus_get()
        if focused == self.entry_date:
            self._calc_days()
        elif focused == self.entry_days:
            self._calc_end_date()

    # ----- 계산 로직 ------------------------------------------------------

    def _calc_days(self):
        """다음 외래일 → 처방일수 계산"""
        raw = self.entry_date.get().strip()
        if not raw or raw == "예: 2026.03.15":
            messagebox.showwarning("입력 오류", "다음 외래일을 입력해 주세요.")
            return

        try:
            target = parse_korean_date(raw)
        except ValueError:
            messagebox.showerror(
                "날짜 형식 오류",
                "날짜를 인식할 수 없습니다.\n\n"
                "다음 형식 중 하나로 입력해 주세요:\n"
                "  • 2026년 3월 15일\n"
                "  • 2026.03.15\n"
                "  • 2026-03-15\n"
                "  • 2026/03/15\n"
                "  • 20260315 (숫자 8자리)",
            )
            return

        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        target = target.replace(hour=0, minute=0, second=0, microsecond=0)
        diff = (target - today).days

        if diff < 0:
            messagebox.showwarning("날짜 오류", "다음 외래일이 오늘보다 과거입니다.")
            return

        margin = self.margin_var.get()
        total_days = diff + margin

        # 결과 표시
        self.result_label1.config(text=f"처방일수: {total_days}일")
        detail = f"오늘({format_korean_date(today)}) → 외래일({format_korean_date(target)}): {diff}일"
        if margin > 0:
            detail += f" + 여유분 {margin}일"
        self.result_sub1.config(text=detail)
        self.result_frame1.pack(fill="x", padx=15, pady=(0, 15))

    def _calc_end_date(self):
        """처방일수 → 약 소진일 계산"""
        raw = self.entry_days.get().strip()
        if not raw:
            messagebox.showwarning("입력 오류", "처방일수를 입력해 주세요.")
            return

        try:
            days = int(raw)
        except ValueError:
            messagebox.showerror("입력 오류", "처방일수는 숫자로 입력해 주세요.")
            return

        if days <= 0:
            messagebox.showwarning("입력 오류", "처방일수는 1 이상이어야 합니다.")
            return

        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today + timedelta(days=days)

        self.result_label2.config(text=f"약 소진일: {format_korean_date(end_date)}")
        self.result_sub2.config(
            text=f"오늘({format_korean_date(today)})부터 {days}일 후"
        )
        self.result_frame2.pack(fill="x", padx=15, pady=(0, 15))


# ---------------------------------------------------------------------------
# 엔트리 포인트
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = PrescriptionCalculator()
    app.mainloop()
