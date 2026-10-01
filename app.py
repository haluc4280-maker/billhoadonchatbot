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

SUGAR_LEVELS = ["100%", "80%", "70%", "50%", "30%", "0%"]
ICE_LEVELS = ["70%", "50%", "30%", "0%"]

# ==============================
# SESSION STATE
# ==============================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "bill_number" not in st.session_state:
    st.session_state.bill_number = 1

if "customer_name" not in st.session_state:
    st.session_state.customer_name = ""


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
    return (item["price"] + topping_total) * item["quantity"]


def calculate_total():
    return sum(
        calculate_item_total(item)
        for item in st.session_state.cart
    )


def create_bill_number():
    return f"HD{st.session_state.bill_number:04d}"


# ==============================
# TÌM FONT TIẾNG VIỆT CHO PDF
# ==============================
def get_pdf_fonts():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    regular_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/Arial.ttf",
    ]

    bold_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/Arial Bold.ttf",
    ]

    regular_path = next(
        (path for path in regular_candidates if os.path.exists(path)),
        None
    )
    bold_path = next(
        (path for path in bold_candidates if os.path.exists(path)),
        None
    )

    regular_font = "Helvetica"
    bold_font = "Helvetica-Bold"

    if regular_path:
        try:
            pdfmetrics.registerFont(TTFont("AppFont", regular_path))
            regular_font = "AppFont"
        except Exception:
            pass

    if bold_path:
        try:
            pdfmetrics.registerFont(TTFont("AppFontBold", bold_path))
            bold_font = "AppFontBold"
        except Exception:
            pass

    return regular_font, bold_font


# ==============================
# TẠO HÓA ĐƠN PDF
# ==============================
def create_pdf():
    from reportlab.lib.pagesizes import A5
    from reportlab.pdfgen import canvas

    buffer = BytesIO()

    regular_font, bold_font = get_pdf_fonts()

    c = canvas.Canvas(buffer, pagesize=A5)
    width, height = A5

    y = height - 35

    # Tiêu đề
    c.setFont(bold_font, 16)
    c.drawCentredString(
        width / 2,
        y,
        "HÓA ĐƠN BÁN HÀNG"
    )

    y -= 25
    c.setFont(regular_font, 9)

    bill_number = create_bill_number()
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    c.drawString(30, y, f"Số bill: {bill_number}")

    y -= 15
    c.drawString(30, y, f"Thời gian: {now}")

    y -= 15
    customer = st.session_state.customer_name.strip() or "Khách lẻ"
    c.drawString(30, y, f"Khách hàng: {customer}")

    y -= 20
    c.line(30, y, width - 30, y)
    y -= 18

    # Danh sách món
    for index, item in enumerate(st.session_state.cart, start=1):
        item_total = calculate_item_total(item)

        # Nếu gần hết trang thì sang trang mới
        if y < 80:
            c.showPage()
            y = height - 35

        c.setFont(bold_font, 9)
        c.drawString(
            30,
            y,
            f"{index}. {item['name']}"
        )

        y -= 14
        c.setFont(regular_font, 8)

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
            topping_text = ", ".join(item["toppings"])
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

    # Tổng tiền
    if y < 80:
        c.showPage()
        y = height - 35

    c.line(30, y, width - 30, y)

    y -= 22

    total = calculate_total()

    c.setFont(bold_font, 12)
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

    c.setFont(regular_font, 9)
    c.drawCentredString(
        width / 2,
        y,
        "Cảm ơn quý khách!"
    )

    c.save()
    buffer.seek(0)

    return buffer


# ==============================
# GIAO DIỆN
# ==============================
st.title("🧋 QUẢN LÝ BÁN TRÀ SỮA")
st.caption("Tạo đơn hàng • Tính tiền • Xuất hóa đơn PDF")

st.divider()

# ==============================
# THÔNG TIN KHÁCH HÀNG
# ==============================
st.subheader("👤 Thông tin khách hàng")

st.session_state.customer_name = st.text_input(
    "Họ và tên khách hàng",
    value=st.session_state.customer_name,
    placeholder="Nhập họ và tên..."
)

st.divider()

# ==============================
# KHU VỰC NHẬP ĐƠN
# ==============================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🧋 Chọn món")

    drink = st.selectbox(
        "Loại trà sữa / thức uống",
        list(MENU.keys())
    )

    price = MENU[drink]

    st.info(f"Giá: **{format_money(price)}**")

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
        value="50%"
    )

    toppings = st.multiselect(
        "Thêm topping",
        list(TOPPINGS.keys())
    )

# ==============================
# GIÁ TOPPING
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
# THÊM VÀO HÓA ĐƠN
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
        "ice": ice,
    }

    st.session_state.cart.append(item)

    st.success(
        f"Đã thêm {quantity} ly {drink} vào hóa đơn!"
    )

    st.rerun()

# ==============================
# HÓA ĐƠN HIỆN TẠI
# ==============================
st.divider()

st.subheader(
    f"🧾 HÓA ĐƠN {create_bill_number()}"
)

if not st.session_state.cart:
    st.info("Chưa có món nào trong hóa đơn.")
else:
    for index, item in enumerate(st.session_state.cart):
        item_total = calculate_item_total(item)

        with st.container(border=True):
            c1, c2, c3 = st.columns([4, 2, 1])

            with c1:
                st.markdown(
                    f"### {index + 1}. {item['name']}"
                )

                st.write(
                    f"Đường: **{item['sugar']}** | "
                    f"Đá: **{item['ice']}**"
                )

                if item["toppings"]:
                    st.write(
                        "Topping: "
                        + ", ".join(item["toppings"])
                    )

            with c2:
                st.write(
                    f"Đơn giá: **{format_money(item['price'])}**"
                )
                st.write(
                    f"Số lượng: **{item['quantity']}**"
                )

            with c3:
                st.write("**Thành tiền**")
                st.markdown(
                    f"### {format_money(item_total)}"
                )

            if st.button(
                "🗑️ Xóa món",
                key=f"delete_{index}"
            ):
                st.session_state.cart.pop(index)
                st.rerun()

    # ==============================
    # TỔNG TIỀN
    # ==============================
    total = calculate_total()

    st.divider()

    col_a, col_b = st.columns([2, 1])

    with col_a:
        st.write(
            f"**Số dòng món:** {len(st.session_state.cart)}"
        )

    with col_b:
        st.markdown(
            f"## Tổng: {format_money(total)}"
        )

    # ==============================
    # XUẤT HÓA ĐƠN
    # ==============================
    st.divider()

    try:
        pdf_file = create_pdf()

        st.download_button(
            label="🖨️ XUẤT HÓA ĐƠN PDF",
            data=pdf_file,
            file_name=f"{create_bill_number()}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(
            "Không thể tạo PDF. Hãy kiểm tra thư viện reportlab."
        )
        st.code(str(e))

    # ==============================
    # THANH TOÁN / BILL MỚI
    # ==============================
    if st.button(
        "💰 THANH TOÁN & TẠO BILL MỚI",
        use_container_width=True
    ):
        st.session_state.cart = []
        st.session_state.customer_name = ""
        st.session_state.bill_number += 1

        st.success(
            "Thanh toán thành công! Đã tạo bill mới."
        )

        st.rerun()
