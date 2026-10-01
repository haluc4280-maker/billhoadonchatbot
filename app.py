st.set_page_config(
    page_title="Milk Tea POS",
    page_icon="🧋",
    layout="centered"
)


# =========================================================
# MENU TRÀ SỮA
# =========================================================

MENU = {
    "Trà sữa truyền thống": 30000,
    "Trà sữa matcha": 35000,
    "Trà sữa socola": 35000,
    "Trà sữa khoai môn": 35000,
    "Trà sữa ô long": 35000,
    "Trà sữa dâu": 35000,
    "Trà sữa caramel": 38000,
    "Trà sữa kem cheese": 40000,
    "Trà đào cam sả": 35000,
    "Trà vải": 32000,
    "Trà chanh dây": 32000,
    "Matcha latte": 40000
}


# =========================================================
# MENU TOPPING
# =========================================================

TOPPINGS = {
    "Không topping": 0,
    "Trân châu đen": 5000,
    "Trân châu trắng": 6000,
    "Thạch dừa": 5000,
    "Thạch trái cây": 5000,
    "Pudding trứng": 7000,
    "Kem cheese": 10000,
    "Hạt thủy tinh": 6000
}


# =========================================================
# MỨC ĐƯỜNG - ĐÁ
# =========================================================

SUGAR_LEVELS = [
    "100%",
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
# KHỞI TẠO GIỎ HÀNG
# =========================================================

if "cart" not in st.session_state:
    st.session_state.cart = []


# =========================================================
# TIÊU ĐỀ
# =========================================================

st.title("🧋 MILK TEA POS lien milk-tea")
st.caption("Hệ thống tính tiền & xuất hóa đơn trà sữa")


# =========================================================
# THÔNG TIN KHÁCH HÀNG
# =========================================================

st.subheader("👤 Thông tin khách hàng")

customer_name = st.text_input(
    "Họ và tên khách hàng",
    placeholder="Nhập tên khách hàng..."
)


# =========================================================
# CHỌN MÓN
# =========================================================

st.subheader("🧋 Chọn món")

drink = st.selectbox(
    "Loại trà sữa / thức uống",
    list(MENU.keys())
)

quantity = st.number_input(
    "Số lượng",
    min_value=1,
    max_value=50,
    value=1,
    step=1
)

topping = st.selectbox(
    "Topping",
    list(TOPPINGS.keys())
)

sugar = st.selectbox(
    "Mức độ đường",
    SUGAR_LEVELS
)

ice = st.selectbox(
    "Mức độ đá",
    ICE_LEVELS
)


# =========================================================
# GIÁ
# =========================================================

drink_price = MENU[drink]
topping_price = TOPPINGS[topping]

unit_price = drink_price + topping_price
total_price = unit_price * quantity


st.info(
    f"💰 Đơn giá: **{unit_price:,} VNĐ**  |  "
    f"Thành tiền: **{total_price:,} VNĐ**"
)


# =========================================================
# THÊM VÀO HÓA ĐƠN
# =========================================================

if st.button("➕ Thêm vào hóa đơn", use_container_width=True):

    item = {
        "drink": drink,
        "quantity": quantity,
        "topping": topping,
        "sugar": sugar,
        "ice": ice,
        "unit_price": unit_price,
        "total": total_price
    }

    st.session_state.cart.append(item)

    st.success(f"Đã thêm {quantity} ly {drink} vào hóa đơn!")


# =========================================================
# HIỂN THỊ HÓA ĐƠN TẠM
# =========================================================

st.divider()

st.subheader("🧾 Hóa đơn hiện tại")


if len(st.session_state.cart) == 0:

    st.warning("Chưa có món nào trong hóa đơn.")

else:

    grand_total = 0

    for i, item in enumerate(st.session_state.cart):

        grand_total += item["total"]

        with st.container(border=True):

            col1, col2 = st.columns([4, 1])

            with col1:

                st.markdown(
                    f"### {item['drink']}"
                )

                st.write(
                    f"🥤 Số lượng: **{item['quantity']} ly**"
                )

                st.write(
                    f"🍮 Topping: **{item['topping']}**"
                )

                st.write(
                    f"🍬 Đường: **{item['sugar']}**"
                )

                st.write(
                    f"🧊 Đá: **{item['ice']}**"
                )

                st.write(
                    f"Đơn giá: {item['unit_price']:,} VNĐ"
                )

            with col2:

                st.markdown(
                    f"**{item['total']:,} VNĐ**"
                )

                if st.button(
                    "🗑️ Xóa",
                    key=f"delete_{i}"
                ):

                    st.session_state.cart.pop(i)

                    st.rerun()


    st.divider()

    st.markdown(
        f"## 💰 TỔNG THANH TOÁN: {grand_total:,} VNĐ"
    )


# =========================================================
# XÓA TOÀN BỘ ĐƠN
# =========================================================

if len(st.session_state.cart) > 0:

    if st.button(
        "🗑️ Xóa toàn bộ hóa đơn",
        use_container_width=True
    ):

        st.session_state.cart = []

        st.rerun()


# =========================================================
# TẠO FILE HÓA ĐƠN PDF
# =========================================================

def create_invoice_pdf(customer_name, cart):

    filename = "hoa_don_tra_sua.pdf"

    c = canvas.Canvas(
        filename,
        pagesize=A5
    )

    width, height = A5

    # -----------------------------------------------------
    # FONT
    # -----------------------------------------------------

    font_path = "DejaVuSans.ttf"

    if os.path.exists(font_path):

        pdfmetrics.registerFont(
            TTFont("DejaVu", font_path)
        )

        font = "DejaVu"

    else:

        font = "Helvetica"

    # -----------------------------------------------------
    # TIÊU ĐỀ
    # -----------------------------------------------------

    y = height - 40

    c.setFont(font, 18)

    c.drawCentredString(
        width / 2,
        y,
        "HOA DON BAN HANG"
    )

    y -= 25

    c.setFont(font, 10)

    c.drawCentredString(
        width / 2,
        y,
        "MILK TEA SHOP"
    )

    # -----------------------------------------------------
    # THÔNG TIN
    # -----------------------------------------------------

    y -= 30

    c.setFont(font, 9)

    c.drawString(
        30,
        y,
        f"Khach hang: {customer_name if customer_name else 'Khach le'}"
    )

    y -= 15

    c.drawString(
        30,
        y,
        datetime.now().strftime(
            "Thoi gian: %d/%m/%Y %H:%M"
        )
    )

    y -= 25

    c.line(
        30,
        y,
        width - 30,
        y
    )

    y -= 20

    grand_total = 0

    # -----------------------------------------------------
    # DANH SÁCH MÓN
    # -----------------------------------------------------

    for index, item in enumerate(cart, start=1):

        grand_total += item["total"]

        c.setFont(font, 10)

        c.drawString(
            30,
            y,
            f"{index}. {item['drink']}"
        )

        y -= 14

        c.setFont(font, 8)

        c.drawString(
            40,
            y,
            f"So luong: {item['quantity']} | "
            f"Topping: {item['topping']}"
        )

        y -= 13

        c.drawString(
            40,
            y,
            f"Duong: {item['sugar']} | "
            f"Da: {item['ice']}"
        )

        y -= 13

        c.drawRightString(
            width - 30,
            y,
            f"{item['total']:,} VND"
        )

        y -= 20

    # -----------------------------------------------------
    # TỔNG TIỀN
    # -----------------------------------------------------

    c.line(
        30,
        y,
        width - 30,
        y
    )

    y -= 25

    c.setFont(font, 13)

    c.drawString(
        30,
        y,
        "TONG THANH TOAN:"
    )

    c.drawRightString(
        width - 30,
        y,
        f"{grand_total:,} VND"
    )

    # -----------------------------------------------------
    # CẢM ƠN
    # -----------------------------------------------------

    y -= 35

    c.setFont(font, 9)

    c.drawCentredString(
        width / 2,
        y,
        "Cam on quy khach!"
    )

    y -= 15

    c.drawCentredString(
        width / 2,
        y,
        "Hen gap lai ban lan sau!"
    )

    c.save()

    return filename


# =========================================================
# XUẤT HÓA ĐƠN
# =========================================================

if len(st.session_state.cart) > 0:

    st.divider()

    st.subheader("📄 Xuất hóa đơn")

    if st.button(
        "🧾 TẠO HÓA ĐƠN PDF",
        use_container_width=True
    ):

        pdf_file = create_invoice_pdf(
            customer_name,
            st.session_state.cart
        )

        with open(
            pdf_file,
            "rb"
        ) as file:

            st.download_button(
                label="⬇️ Tải hóa đơn về máy",
                data=file,
                file_name="hoa_don_tra_sua.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        st.success(
            "Đã tạo hóa đơn PDF thành công!"
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🧋 Milk Tea POS • Hệ thống bán hàng trà sữa"
)
