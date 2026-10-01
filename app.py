import streamlit as st
from datetime import datetime
from io import BytesIO
import os

# ==============================
# CẤU HÌNH TRANG
# ==============================

st.set_page_config(
    page_title="Quản lý bán trà sữa",
    page_icon="🧋",
    layout="wide"
)

# ==============================
# DỮ LIỆU MENU
# ==============================

MENU = {
    "Trà sữa truyền thống": 25000,
    "Trà sữa trân châu": 30000,
    "Trà sữa matcha": 30000,
    "Trà sữa socola": 30000,
    "Trà sữa khoai môn": 32000,
    "Trà sữa dâu": 30000,
    "Trà đào": 28000,
    "Trà vải": 28000,
    "Trà chanh": 20000,
    "Trà tắc": 20000,
}

TOPPINGS = {
    "Trân châu đen": 5000,
    "Trân châu trắng": 5000,
    "Thạch dừa": 5000,
    "Thạch trái cây": 5000,
    "Pudding trứng": 7000,
    "Kem cheese": 8000,
    "Trân châu hoàng kim": 7000,
    "Hạt thủy tinh": 6000,
}

SUGAR_LEVELS = [
    "100%",
    "80%",
    "70%",
    "50%",
    "30%",
    "0%"
]

ICE_LEVELS = [
    "100%",
    "90%",
    "80%",
    "70%"
]

# ==============================
# KHỞI TẠO SESSION
# ==============================

if "cart" not in st.session_state:
    st.session_state.cart = []

if "bill_number" not in st.session_state:
    st.session_state.bill_number = 1

# ==============================
# HÀM TIỆN ÍCH
# ==============================

def format_money(number):
    return f"{number:,.0f} VNĐ".replace(",", ".")


def calculate_item_total(item):
    topping_total = sum(
        TOPPINGS[topping]
        for topping in item["toppings"]
    )

    return (
        item["price"] + topping_total
    ) * item["quantity"]


def calculate_total():
    return sum(
        calculate_item_total(item)
        for item in st.session_state.cart
    )


def create_bill_number():
    return f"HD{st.session_state.bill_number:04d}"


# ==============================
# TẠO HÓA ĐƠN PDF
# ==============================

def create_pdf():
    try:
        from reportlab.lib.pagesizes import thermal
    except Exception:
        pass

    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A5
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    buffer = BytesIO()

    # --------------------------------
    # Tìm font Unicode
    # --------------------------------

    font_regular = "Helvetica"
    font_bold = "Helvetica-Bold"

    font_paths = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    ]

    regular_path = None
    bold_path = None

    for path in font_paths:
        if os.path.exists(path):
            if "Bold" in path:
                bold_path = path
            elif regular_path is None:
                regular_path = path

    if regular_path:
        try:
pdfmetrics.registerFont(
                TTFont("AppFont", regular_path)
            
            font_regular = "AppFont"
        except:
            pass

    if bold_path:
        try:
            pdfmetrics.registerFont(
                TTFont("AppFontBold", bold_path)
            )
            font_bold = "AppFontBold"
        except:
            pass

    # --------------------------------
    # Khổ giấy A5
    # --------------------------------

    c = canvas.Canvas(buffer, pagesize=A5)

    width, height = A5

    y = height - 35

    # --------------------------------
    # TIÊU ĐỀ
    # --------------------------------

    c.setFont(font_bold, 16)
    c.drawCentredString(
        width / 2,
        y,
        "HÓA ĐƠN BÁN HÀNG"
    )

    y -= 25

    c.setFont(font_regular, 9)

    bill_number = create_bill_number()

    now = datetime.now().strftime(
        "%d/%m/%Y %H:%M"
    )

    c.drawString(
        30,
        y,
        f"Số bill: {bill_number}"
    )

    y -= 15

    c.drawString(
        30,
        y,
        f"Thời gian: {now}"
    )

    y -= 20

    # --------------------------------
    # ĐƯỜNG KẺ
    # --------------------------------

    c.line(
        30,
        y,
        width - 30,
        y
    )

    y -= 18

    # --------------------------------
    # DANH SÁCH MÓN
    # --------------------------------

    for index, item in enumerate(
        st.session_state.cart,
        start=1
    ):

        item_total = calculate_item_total(item)

        c.setFont(font_bold, 9)

        c.drawString(
            30,
            y,
            f"{index}. {item['name']}"
        )

        y -= 14

        c.setFont(font_regular, 8)

        c.drawString(
            42,
            y,
            f"SL: {item['quantity']} x {format_money(item['price'])}"
        )

        y -= 13

        c.drawString(
            42,
            y,
            f"Đường: {item['sugar']} | Đá: {item['ice']}"
        )

        y -= 13

        if item["toppings"]:
            topping_text = ", ".join(
                item["toppings"]
            )

            c.drawString(
                42,
                y,
                f"Topping: {topping_text}"
            )

            y -= 13

        c.drawRightString(
            width - 30,
            y,
            format_money(item_total)
        )

        y -= 18

    # --------------------------------
    # TỔNG TIỀN
    # --------------------------------

    c.line(
        30,
        y,
        width - 30,
        y
    )

    y -= 22

    total = calculate_total()

    c.setFont(font_bold, 12)

    c.drawString(
        30,
        y,
        "TỔNG THANH TOÁN"
    )

    c.drawRightString(
        width - 30,
        y,
        format_money(total)
    )

    y -= 30

    c.setFont(font_regular, 9)

    c.drawCentredString(
        width / 2,
        y,
        "Cảm ơn quý khách!"
)

    c.save()

    buffer.seek(0)

    return buffer


# ==============================
# HEADER
# ==============================

st.title("🧋 QUẢN LÝ BÁN TRÀ SỮA")

st.caption(
    "Tạo đơn hàng • Tính tiền • Xuất hóa đơn"
)

st.divider()

# ==============================
# KHU VỰC NHẬP ĐƠN
# ==============================

col1, col2 = st.columns([1, 1])

with col1:

    st.subheader("🧋 Chọn món")

    drink = st.selectbox(
        "Loại trà sữa / thức uống",
        list(MENU.keys())
    )

    price = MENU[drink]

    st.info(
        f"Giá: **{format_money(price)}**"
    )

    quantity = st.number_input(
        "Số lượng",
        min_value=1,
        max_value=50,
        value=1,
        step=1
    )

with col2:

    st.subheader("⚙️ Tùy chọn")

    sugar = st.select_slider(
        "Mức độ đường",
        options=SUGAR_LEVELS,
        value="70%"
    )

    ice = st.select_slider(
        "Mức độ đá",
        options=ICE_LEVELS,
        value="100%"
    )

    toppings = st.multiselect(
        "Thêm topping",
        list(TOPPINGS.keys())
    )

# ==============================
# HIỂN THỊ GIÁ TOPPING
# ==============================

if toppings:

    topping_price = sum(
        TOPPINGS[topping]
        for topping in toppings
    )

    st.info(
        "Topping: "
        + ", ".join(toppings)
        + f" — +{format_money(topping_price)}"
    )

# ==============================
# THÊM VÀO BILL
# ==============================

if st.button(
    "➕ THÊM VÀO HÓA ĐƠN",
    use_container_width=True
):

    item = {
        "name": drink,
        "price": price,
        "quantity": quantity,
        "toppings": toppings,
        "sugar": sugar,
        "ice": ice
    }

    st.session_state.cart.append(item)

    st.success(
        f"Đã thêm {quantity} ly {drink} vào hóa đơn!"
    )

# ==============================
# HÓA ĐƠN HIỆN TẠI
# ==============================

st.divider()

st.subheader(
    f"🧾 HÓA ĐƠN {create_bill_number()}"
)

if len(st.session_state.cart) == 0:

    st.info(
        "Chưa có món nào trong hóa đơn."
    )

else:

    # --------------------------------
    # HIỂN THỊ TỪNG MÓN
    # --------------------------------

    for index, item in enumerate(
        st.session_state.cart
    ):

        item_total = calculate_item_total(item)

        with st.container(border=True):

            c1, c2, c3 = st.columns(
                [4, 2, 1]
            )

            with c1:

                st.markdown(
                    f"### {index + 1}. {item['name']}"
                )

                st.write(
                    f"Đường: **{item['sugar']}**  |  "
                    f"Đá: **{item['ice']}**"
                )

                if item["toppings"]:

                    st.write(
                        "Topping: "
                        + ", ".join(
item["toppings"]
                        )
                    )

            with c2:

                st.write(
                    f"Đơn giá: "
                    f"**{format_money(item['price'])}**"
                )

                st.write(
                    f"Số lượng: **{item['quantity']}**"
                )

            with c3:

                st.write(
                    "**Thành tiền**"
                )

                st.markdown(
                    f"### {format_money(item_total)}"
                )

            # --------------------------
            # XÓA MÓN
            # --------------------------

            if st.button(
                "🗑️ Xóa",
                key=f"delete_{index}"
            ):

                st.session_state.cart.pop(
                    index
                )

                st.rerun()

    # ==============================
    # TỔNG TIỀN
    # ==============================

    total = calculate_total()

    st.divider()

    col_a, col_b = st.columns(
        [2, 1]
    )

    with col_a:

        st.write(
            f"**Số lượng món:** "
            f"{len(st.session_state.cart)}"
        )

    with col_b:

        st.markdown(
            f"## Tổng: {format_money(total)}"
        )

    # ==============================
    # NÚT XUẤT HÓA ĐƠN
    # ==============================

    st.divider()

    pdf_file = create_pdf()

    st.download_button(
        label="🖨️ XUẤT HÓA ĐƠN PDF",
        data=pdf_file,
        file_name=f"{create_bill_number()}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

    # ==============================
    # THANH TOÁN / BILL MỚI
    # ==============================

    if st.button(
        "💰 THANH TOÁN & TẠO BILL MỚI",
        use_container_width=True
    ):

        st.session_state.cart = []

        st.session_state.bill_number += 1

        st.success(
            "Thanh toán thành công! "
            "Đã tạo bill mới."
        )

        st.rerun()
