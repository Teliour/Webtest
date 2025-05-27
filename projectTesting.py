from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# Путь к geckodriver
geckodriver_path = r"C:\Users\Илья\Downloads\geckodriver-v0.36.0-win32\geckodriver.exe"
service = Service(geckodriver_path)

options = Options()
options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"

driver = webdriver.Firefox(service=service, options=options)
wait = WebDriverWait(driver, 30)



class MainPage:
    URL = "https://demo.opencart.com/"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)

    def open(self):
        self.driver.get(self.URL)

    def click_first_product(self):
        first_product = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".product-layout .caption a")))
        first_product.click()

    def change_currency(self, currency_name):
        currency_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-link.dropdown-toggle")))
        currency_button.click()
        option = self.wait.until(EC.element_to_be_clickable((By.NAME, currency_name)))
        option.click()
        time.sleep(2)

    def go_to_category(self, category_name, subcategory_name=None):
        menu = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, category_name)))
        menu.click()
        if subcategory_name:
            subcat = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, subcategory_name)))
            subcat.click()

    def search_product(self, product_name):
        search_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "search")))
        search_input.clear()
        search_input.send_keys(product_name)
        self.driver.find_element(By.CSS_SELECTOR, "button.btn.btn-default.btn-lg").click()

    def add_product_to_wishlist_by_name(self, product_name):
        products = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-layout")))
        for product in products:
            title = product.find_element(By.CSS_SELECTOR, "h4 a").text
            if product_name.lower() in title.lower():
                wishlist_btn = product.find_element(By.CSS_SELECTOR, "button[data-original-title='Add to Wish List']")
                wishlist_btn.click()
                return True
        return False

    def add_product_to_cart_by_name(self, product_name):
        products = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-layout")))
        for product in products:
            title = product.find_element(By.CSS_SELECTOR, "h4 a").text
            if product_name.lower() in title.lower():
                cart_btn = product.find_element(By.CSS_SELECTOR, "button[onclick*='cart.add']")
                cart_btn.click()
                return True
        return False


class ProductPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)

    def check_thumbnails(self):
        thumbnails = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".thumbnails li a")))
        if len(thumbnails) > 1:
            for thumb in thumbnails:
                thumb.click()
                time.sleep(1)
        else:
            print("Скриншоты отсутствуют или только один")

    def add_review(self, name, review_text, rating=5):
        reviews_tab = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Reviews (0)")))
        reviews_tab.click()
        self.wait.until(EC.visibility_of_element_located((By.ID, "input-name"))).send_keys(name)
        self.driver.find_element(By.ID, "input-review").send_keys(review_text)
        rating_radio = self.driver.find_element(By.CSS_SELECTOR, f"input[name='rating'][value='{rating}']")
        rating_radio.click()
        self.driver.find_element(By.ID, "button-review").click()
        try:
            alert = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-success")))
            print("Отзыв успешно отправлен:", alert.text)
        except TimeoutException:
            print("Не удалось подтвердить отправку отзыва")


class RegisterPage:
    URL = "https://demo.opencart.com/index.php?route=account/register"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)

    def open(self):
        self.driver.get(self.URL)

    def register(self, firstname, lastname, email, telephone, password):
        self.wait.until(EC.visibility_of_element_located((By.ID, "input-firstname"))).send_keys(firstname)
        self.driver.find_element(By.ID, "input-lastname").send_keys(lastname)
        self.driver.find_element(By.ID, "input-email").send_keys(email)
        self.driver.find_element(By.ID, "input-telephone").send_keys(telephone)
        self.driver.find_element(By.ID, "input-password").send_keys(password)
        self.driver.find_element(By.ID, "input-confirm").send_keys(password)
        self.driver.find_element(By.NAME, "agree").click()
        self.driver.find_element(By.CSS_SELECTOR, "input.btn.btn-primary").click()


class CartPage:
    URL = "https://demo.opencart.com/index.php?route=checkout/cart"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)

    def open(self):
        self.driver.get(self.URL)

    def is_product_in_cart(self, product_name):
        try:
            products = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table.table-bordered tbody tr")))
            for product in products:
                name = product.find_element(By.CSS_SELECTOR, "td.text-left a").text
                if product_name.lower() in name.lower():
                    return True
            return False
        except TimeoutException:
            return False


# --- Тесты ---

def test_main_flow():
    main_page = MainPage(driver)
    product_page = ProductPage(driver)
    register_page = RegisterPage(driver)

    main_page.open()
    main_page.click_first_product()
    product_page.check_thumbnails()
    driver.back()

    main_page.change_currency("EUR")
    main_page.change_currency("USD")

    main_page.go_to_category("Computers", "PC (0)")
    try:
        no_products = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#content p")))
        if "There are no products to list in this category." in no_products.text:
            print("Страница категории PC пуста - проверка пройдена")
        else:
            print("Страница категории PC содержит товары")
    except TimeoutException:
        print("Сообщение о пустой категории не найдено")

    register_page.open()
    register_page.register("Иван", "Иванов", "ivanov@example.com", "1234567890", "Password123")

    main_page.open()
    main_page.search_product("MacBook")
    time.sleep(3)


def test_add_to_wishlist():
    main_page = MainPage(driver)
    main_page.open()
    added = main_page.add_product_to_wishlist_by_name("MacBook")
    if added:
        print("Товар добавлен в вишлист")
    else:
        print("Товар для вишлиста не найден")


def test_add_camera_to_cart():
    main_page = MainPage(driver)
    cart_page = CartPage(driver)
    main_page.open()
    main_page.go_to_category("Cameras")
    added = main_page.add_product_to_cart_by_name("Canon EOS 5D")
    time.sleep(2)
    cart_page.open()
    if cart_page.is_product_in_cart("Canon EOS 5D"):
        print("Камера успешно добавлена в корзину")
    else:
        print("Камера не добавлена в корзину")


def test_add_tablet_to_cart():
    main_page = MainPage(driver)
    cart_page = CartPage(driver)
    main_page.open()
    main_page.go_to_category("Tablets")
    added = main_page.add_product_to_cart_by_name("Samsung Galaxy Tab")
    time.sleep(2)
    cart_page.open()
    if cart_page.is_product_in_cart("Samsung Galaxy Tab"):
        print("Планшет успешно добавлен в корзину")
    else:
        print("Планшет не добавлен в корзину")


def test_add_htc_phone_to_cart():
    main_page = MainPage(driver)
    cart_page = CartPage(driver)
    main_page.open()
    main_page.go_to_category("Phones & PDAs")
    added = main_page.add_product_to_cart_by_name("HTC Touch HD")
    time.sleep(2)
    cart_page.open()
    if cart_page.is_product_in_cart("HTC Touch HD"):
        print("Телефон HTC успешно добавлен в корзину")
    else:
        print("Телефон HTC не добавлен в корзину")


def test_write_review():
    main_page = MainPage(driver)
    product_page = ProductPage(driver)
    main_page.open()
    main_page.search_product("MacBook")
    first_product = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".product-layout .caption a")))
    first_product.click()
    product_page.add_review("Иван", "Отличный товар, рекомендую!", rating=5)


# --- Запуск тестов ---

test_main_flow()
test_add_to_wishlist()
test_add_camera_to_cart()
test_add_tablet_to_cart()
test_add_htc_phone_to_cart()
test_write_review()

time.sleep(5)
driver.quit()
