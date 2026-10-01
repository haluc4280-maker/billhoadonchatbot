import streamlit as st
from datetime import datetime
from io import BytesIO
import os
import requests


# =========================================================
# CẤU HÌNH TRANG
# =========================================================

st.set_page_config(
    page_title="Quản lý bán trà sữa",
    page_icon="🧋",
    layout="wide"
)


# =========================================================
# LOGO
# =========================================================

try:
    st.image("logo1.jpg", width=180)
except Exception:
    pass


# =========================================================
# DỮ LIỆU MENU
# =========================================================

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
    "70%",
    "50%",
    "30%",
    "0%"
]


# =========================================================
# API OPENROUTER
# =========================================================
#
# Cách 1:
# Tạo file .streamlit/secrets.toml:
#
# OPENROUTER_API_KEY = "KEY_MOI_CUA_BAN"
#
# Cách 2:
# Có thể đặt biến môi trường OPENROUTER_API_KEY
#
# KHÔNG đưa API key trực tiếp lên GitHub.
# =========================================================

try:
    OPENROUTER_API_KEY = st.secrets.get(
        "OPENROUTER_API_KEY",
        os.getenv("OPENROUTER_API_KEY", "")
    )
except Exception:
    OPENROUTER_API_KEY = os.getenv(
        "OPENROUTER_API_KEY",
        ""
    )


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Có thể đổi model này nếu muốn
OPENROUTER_MODEL = "openrouter/free"


# =========================================================
# SESSION STATE
# =========================================================

if "cart" not in st.session_state:
    st.session_state.cart = []


if "bill_number" not in st.session_state:
    st.session_state.bill_number = 1


if "customer_name" not in st.session_state:
    st.session_state.customer_name = ""


if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================================================
# HÀM TIỆN ÍCH
# =========================================================

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


# =========================================================
# TẠO THÔNG TIN MENU CHO CHATBOT
# =========================================================

def get_menu_context():

    menu_text = "\n".join(
        [
            f"- {name}: {format_money(price)}"
            for name, price in MENU.items()
        ]
    )

    topping_text = "\n".join(
        [
            f"- {name}: {format_money(price)}"
            for name, price in TOPPINGS.items()
        ]
    )

    sugar_text = ", ".join(SUGAR_LEVELS)

    ice_text = ", ".join(ICE_LEVELS)

    return f"""
MENU TRÀ SỮA:

{menu_text}

TOPPING:

{topping_text}

MỨC ĐƯỜNG:
{sugar_text}

MỨC ĐÁ:
{ice_text}
"""


# =========================================================
# LẤY THÔNG TIN HÓA ĐƠN HIỆN TẠI
# =========================================================

def get_cart_context():

    if not st.session_state.cart:

        return """
HÓA ĐƠN HIỆN TẠI:
Chưa có món nào.
"""

    cart_text = []

    for index, item in enumerate(
        st.session_state.cart,
        start=1
    ):

        item_total = calculate_item_total(item)

        toppings = ", ".join(
            item["toppings"]
        )

        if not toppings:
            toppings = "Không có"

        cart_text.append(
            f"""
{index}. {item['name']}
- Số lượng: {item['quantity']}
- Đường: {item['sugar']}
- Đá: {item['ice']}
- Topping: {toppings}
- Thành tiền: {format_money(item_total)}
"""
        )

    total = calculate_total()

    return f"""
HÓA ĐƠN HIỆN TẠI:

{"".join(cart_text)}

TỔNG TIỀN:
{format_money(total)}
"""


# =========================================================
# GỌI CHATBOT AI
# =========================================================

def ask_ai(question):

    if not OPENROUTER_API_KEY:

        return """
⚠️ Chatbot AI chưa được kết nối.

Bạn hãy thêm API key OpenRouter vào:

`.streamlit/secrets.toml`

Ví dụ:

OPENROUTER_API_KEY = "KEY_MOI_CUA_BAN"

Sau đó chạy lại ứng dụng.
"""


    menu_context = get_menu_context()

    cart_context = get_cart_context()


    system_prompt = f"""
Bạn là trợ lý AI cho một ứng dụng quản lý bán trà sữa.

Tên trợ lý:
🧋 Trợ lý Trà Sữa

Nhiệm vụ:

1. Trả lời các câu hỏi thông thường của khách hàng.
2. Có thể trò chuyện tự nhiên bằng tiếng Việt.
3. Tư vấn đồ uống dựa trên menu thực tế.
4. Giải thích giá món.
5. Tư vấn topping.
6. Tư vấn mức đường và đá.
7. Có thể giải thích cách đặt món.
8. Có thể xem thông tin hóa đơn hiện tại.
9. Nếu khách hỏi tổng tiền thì sử dụng đúng tổng tiền trong hóa đơn.
10. Không được tự bịa món hoặc giá không có trong menu.
11. Nếu không biết thông tin của quán thì nói rõ là chưa có dữ liệu.
12. Trả lời thân thiện, ngắn gọn, dễ hiểu.
13. Có thể sử dụng emoji vừa phải.
14. Nếu người dùng hỏi một câu hỏi thông thường không liên quan đến trà sữa,
    vẫn có thể trả lời như một chatbot AI thông thường.
15. Không được tự ý thay đổi hóa đơn.
16. Không được tự ý thêm món vào giỏ hàng.
17. Không được tự ý thanh toán.
18. Chỉ tư vấn và trả lời.

DỮ LIỆU QUÁN:

{menu_context}

{cart_context}

Tên khách hàng hiện tại:
{st.session_state.customer_name or "Khách lẻ"}
"""


    # Lấy lịch sử trò chuyện gần đây
    recent_messages = st.session_state.messages[-10:]


    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]


    for message in recent_messages:

        messages.append(
            {
                "role": message["role"],
                "content": message["content"]
            }
        )


    messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Quan Ly Ban Tra Sua"
    }


    data = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 800
    }


    try:

        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=data,
            timeout=60
        )


        if response.status_code != 200:

            try:
                error_data = response.json()

                error_message = (
                    error_data
                    .get("error", {})
                    .get("message", "Lỗi không xác định")
                )

            except Exception:

                error_message = response.text


            return (
                "❌ Không thể kết nối chatbot AI.\n\n"
                f"Chi tiết: {error_message}"
            )


        result = response.json()


        answer = (
            result
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )


        if not answer:

            return "🤖 Chatbot chưa tạo được câu trả lời."


        return answer


    except requests.exceptions.Timeout:

        return (
            "⏳ Chatbot phản hồi hơi lâu. "
            "Bạn thử gửi lại câu hỏi nhé."
        )


    except requests.exceptions.ConnectionError:

        return (
            "🌐 Không thể kết nối Internet để sử dụng chatbot."
        )


    except Exception as e:

        return (
            "❌ Đã xảy ra lỗi khi gọi chatbot.\n\n"
            f"Chi tiết: {str(e)}"
        )


# =========================================================
# TÌM FONT TIẾNG VIỆT CHO PDF
# =========================================================

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
        (
            path
            for path in regular_candidates
            if os.path.exists(path)
        ),
        None
    )


    bold_path = next(
        (
            path
            for path in bold_candidates
            if os.path.exists(path)
        ),
        None
    )


    regular_font = "Helvetica"
    bold_font = "Helvetica-Bold"


    if regular_path:

        try:

            pdfmetrics.registerFont(
                TTFont(
                    "AppFont",
                    regular_path
                )
            )

            regular_font = "AppFont"

        except Exception:
            pass


    if bold_path:

        try:

            pdfmetrics.registerFont(
                TTFont(
                    "AppFontBold",
                    bold_path
                )
            )

            bold_font = "AppFontBold"

        except Exception:
            pass


    return regular_font, bold_font


# =========================================================
# TẠO HÓA ĐƠN PDF
# =========================================================

def create_pdf():

    from reportlab.lib.pagesizes import A5
    from reportlab.pdfgen import canvas


    buffer = BytesIO()


    regular_font, bold_font = get_pdf_fonts()


    c = canvas.Canvas(
        buffer,
        pagesize=A5
    )


    width, height = A5


    y = height - 35


    # -----------------------------------------------------
    # TIÊU ĐỀ
    # -----------------------------------------------------

    c.setFont(
        bold_font,
        16
    )


    c.drawCentredString(
        width / 2,
        y,
        "HÓA ĐƠN BÁN HÀNG"
    )


    y -= 25


    c.setFont(
        regular_font,
        9
    )


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


    y -= 15


    customer = (
        st.session_state.customer_name.strip()
        or "Khách lẻ"
    )


    c.drawString(
        30,
        y,
        f"Khách hàng: {customer}"
    )


    y -= 20


    c.line(
        30,
        y,
        width - 30,
        y
    )


    y -= 18


    # -----------------------------------------------------
    # DANH SÁCH MÓN
    # -----------------------------------------------------

    for index, item in enumerate(
        st.session_state.cart,
        start=1
    ):

        item_total = calculate_item_total(
            item
        )


        if y < 80:

            c.showPage()

            y = height - 35


        c.setFont(
            bold_font,
            9
        )


        c.drawString(
            30,
            y,
            f"{index}. {item['name']}"
        )


        y -= 14


        c.setFont(
            regular_font,
            8
        )


        c.drawString(
            42,
            y,
            (
                f"SL: {item['quantity']} x "
                f"{format_money(item['price'])}"
            )
        )


        y -= 13


        c.drawString(
            42,
            y,
            (
                f"Đường: {item['sugar']} | "
                f"Đá: {item['ice']}"
            )
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


    # -----------------------------------------------------
    # TỔNG TIỀN
    # -----------------------------------------------------

    if y < 80:

        c.showPage()

        y = height - 35


    c.line(
        30,
        y,
        width - 30,
        y
    )


    y -= 22


    total = calculate_total()


    c.setFont(
        bold_font,
        12
    )


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


    c.setFont(
        regular_font,
        9
    )


    c.drawCentredString(
        width / 2,
        y,
        "Cảm ơn quý khách!"
    )


    c.save()


    buffer.seek(0)


    return buffer


# =========================================================
# GIAO DIỆN CHÍNH
# =========================================================

st.title(
    "🧋 QUẢN LÝ BÁN TRÀ SỮA"
)


st.caption(
    "Tạo đơn hàng • Tính tiền • Xuất hóa đơn PDF • Chatbot AI"
)


st.divider()


# =========================================================
# THÔNG TIN KHÁCH HÀNG
# =========================================================

st.subheader(
    "👤 Thông tin khách hàng"
)


st.session_state.customer_name = st.text_input(
    "Họ và tên khách hàng",
    value=st.session_state.customer_name,
    placeholder="Nhập họ và tên..."
)


st.divider()


# =========================================================
# KHU VỰC NHẬP ĐƠN
# =========================================================

col1, col2 = st.columns(2)


with col1:

    st.subheader(
        "🧋 Chọn món"
    )


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

    st.subheader(
        "⚙️ Tùy chọn"
    )


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


# =========================================================
# GIÁ TOPPING
# =========================================================

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


# =========================================================
# THÊM VÀO HÓA ĐƠN
# =========================================================

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


    st.session_state.cart.append(
        item
    )


    st.success(
        f"Đã thêm {quantity} ly {drink} vào hóa đơn!"
    )


    st.rerun()


# =========================================================
# HÓA ĐƠN HIỆN TẠI
# =========================================================

st.divider()


st.subheader(
    f"🧾 HÓA ĐƠN {create_bill_number()}"
)


if not st.session_state.cart:

    st.info(
        "Chưa có món nào trong hóa đơn."
    )


else:

    for index, item in enumerate(
        st.session_state.cart
    ):

        item_total = calculate_item_total(
            item
        )


        with st.container(
            border=True
        ):

            c1, c2, c3 = st.columns(
                [4, 2, 1]
            )


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
                        + ", ".join(
                            item["toppings"]
                        )
                    )


            with c2:

                st.write(
                    f"Đơn giá: **{format_money(item['price'])}**"
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


            if st.button(
                "🗑️ Xóa món",
                key=f"delete_{index}"
            ):

                st.session_state.cart.pop(
                    index
                )


                st.rerun()


    # =====================================================
    # TỔNG TIỀN
    # =====================================================

    total = calculate_total()


    st.divider()


    col_a, col_b = st.columns(
        [2, 1]
    )


    with col_a:

        st.write(
            f"**Số dòng món:** "
            f"{len(st.session_state.cart)}"
        )


    with col_b:

        st.markdown(
            f"## Tổng: {format_money(total)}"
        )


    # =====================================================
    # XUẤT HÓA ĐƠN
    # =====================================================

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
            "Không thể tạo PDF. "
            "Hãy kiểm tra thư viện reportlab."
        )


        st.code(
            str(e)
        )


    # =====================================================
    # THANH TOÁN / BILL MỚI
    # =====================================================

    if st.button(
        "💰 THANH TOÁN & TẠO BILL MỚI",
        use_container_width=True
    ):

        st.session_state.cart = []

        st.session_state.customer_name = ""

        st.session_state.bill_number += 1


        st.success(
            "Thanh toán thành công! "
            "Đã tạo bill mới."
        )


        st.rerun()


# =========================================================
# 🤖 CHATBOX AI
# =========================================================

st.divider()


st.subheader(
    "🤖 CHATBOX AI"
)


st.caption(
    "Bạn có thể hỏi về menu, giá món, hóa đơn "
    "hoặc đặt bất kỳ câu hỏi thông thường nào."
)


# =========================================================
# NÚT XÓA LỊCH SỬ CHAT
# =========================================================

chat_col1, chat_col2 = st.columns(
    [5, 1]
)


with chat_col2:

    if st.button(
        "🗑️ Xóa chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# =========================================================
# HIỂN THỊ LỊCH SỬ CHAT
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =========================================================
# Ô CHAT
# =========================================================

user_question = st.chat_input(
    "💬 Nhập câu hỏi của bạn..."
)


if user_question:

    # -----------------------------------------------------
    # HIỂN THỊ CÂU HỎI
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_question
        }
    )


    with st.chat_message(
        "user"
    ):

        st.markdown(
            user_question
        )


    # -----------------------------------------------------
    # AI TRẢ LỜI
    # -----------------------------------------------------

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "🤖 Đang suy nghĩ..."
        ):

            answer = ask_ai(
                user_question
            )


        st.markdown(
            answer
        )


    # -----------------------------------------------------
    # LƯU CÂU TRẢ LỜI
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
