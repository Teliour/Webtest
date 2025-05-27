import logging
import time
import allure
import pytest
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# --- Логгирование ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("test_log.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

@pytest.fixture(scope="session")
def driver():
    geckodriver_path = r"C:\Users\Илья\Downloads\geckodriver-v0.36.0-win32\geckodriver.exe"
    service = Service(geckodriver_path)
    options = Options()
    options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
    driver = webdriver.Firefox(service=service, options=options)
    driver.maximize_window()
    yield driver
    driver.quit()

# --- Page Objects ---

class MainPage:
    URL = "https://demo.opencart.com/"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)

    @allure.step("Открыть главную страницу")
    def open(self):
        logger.info("Открываем главную страницу")
        self.driver.get(self.URL)

    @allure.step("Клик по первому продукту")
    def click_first_product(self):
        first_product = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".product-layout .caption a")))
        first_product.click()
        logger.info("Клик по первому продукту")

    @allure.step("Смена валюты на {1}")
    def change_currency(self, currency_name):
        currency_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-link.dropdown-toggle")))
        currency_button.click()
        option = self.wait.until(EC.element_to_be_clickable((By.NAME, currency_name)))
        option.click()
        logger.info(f"Смена валюты на {currency_name}")
        time.sleep(2)

    @allure.step("Переход в категорию {1} -> {2}")
    def go_to_category(self, category_name, subcategory_name=None):
        menu = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, category_name)))
        menu.click()
        logger.info(f"Переход в категорию {category_name}")
        if subcategory_name:
            subcat = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, subcategory_name)))
            subcat.click()
            logger.info(f"Переход в подкатегорию {subcategory_name}")

    @allure.step("Поиск товара: {1}")
    def search_product(self, product_name):
        search_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "search")))
        search_input.clear()
        search_input.send_keys(product_name)
        self.driver.find_element(By.CSS_SELECTOR, "button.btn.btn-default.btn-lg").click()
        logger.info(f"Поиск товара: {product_name}")

    @allure.step("Добавление товара в вишлист: {1}")
    def add_product_to_wishlist_by_name(self, product_name):
        products = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-layout")))
        for product in products:
            title = product.find_element(By.CSS_SELECTOR, "h4 a").text
            if product_name.lower() in title.lower():
                wishlist_btn = product.find_element(By.CSS_SELECTOR, "button[data-original-title='Add to Wish List']")
                wishlist_btn.click()
                logger.info(f"Товар {product_name} добавлен в вишлист")
                return True
        logger.warning(f"Товар {product_name} не найден для добавления в вишлист")
        return False

    @allure.step("Добавление товара в корзину: {1}")
    def add_product_to_cart_by_name(self, product_name):
        products = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-layout")))
        for product in products:
            title = product.find_element(By.CSS_SELECTOR, "h4 a").text
            if product_name.lower() in title.lower():
                cart_btn = product.find_element(By.CSS_SELECTOR, "button[onclick*='cart.add']")
                cart_btn.click()
                logger.info(f"Товар {product_name} добавлен в корзину")
                return True
        logger.warning(f"Товар {product_name} не найден для добавления в корзину")
        return False

class ProductPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)

    @allure.step("Проверка галереи скриншотов")
    def check_thumbnails(self):
        thumbnails = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".thumbnails li a")))
        if len(thumbnails) > 1:
            for thumb in thumbnails:
                thumb.click()
                time.sleep(1)
            logger.info("Галерея скриншотов переключается")
        else:
            logger.warning("Скриншоты отсутствуют или только один")

    @allure.step("Оставить отзыв о товаре")
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
            logger.info(f"Отзыв успешно отправлен: {alert.text}")
            allure.attach(self.driver.get_screenshot_as_png(), name="ReviewSuccess", attachment_type=allure.attachment_type.PNG)
        except TimeoutException:
            logger.error("Не удалось подтвердить отправку отзыва")
            allure.attach(self.driver.get_screenshot_as_png(), name="ReviewFail", attachment_type=allure.attachment_type.PNG)

class RegisterPage:
    URL = "https://demo.opencart.com/index.php?route=account/register"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)

    @allure.step("Открыть страницу регистрации")
    def open(self):
        self.driver.get(self.URL)
        logger.info("Открыта страница регистрации")

    @allure.step("Регистрация пользователя: {1} {2}")
    def register(self, firstname, lastname, email, telephone, password):
        self.wait.until(EC.visibility_of_element_located((By.ID, "input-firstname"))).send_keys(firstname)
        self.driver.find_element(By.ID, "input-lastname").send_keys(lastname)
        self.driver.find_element(By.ID, "input-email").send_keys(email)
        self.driver.find_element(By.ID, "input-telephone").send_keys(telephone)
        self.driver.find_element(By.ID, "input-password").send_keys(password)
        self.driver.find_element(By.ID, "input-confirm").send_keys(password)
        self.driver.find_element(By.NAME, "agree").click()
        self.driver.find_element(By.CSS_SELECTOR, "input.btn.btn-primary").click()
        logger.info(f"Регистрация пользователя: {firstname} {lastname}")

class CartPage:
    URL = "https://demo.opencart.com/index.php?route=checkout/cart"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)

    @allure.step("Открыть корзину")
    def open(self):
        self.driver.get(self.URL)
        logger.info("Открыта корзина")

    @allure.step("Проверка наличия товара в корзине: {1}")
    def is_product_in_cart(self, product_name):
        try:
            products = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table.table-bordered tbody tr")))
            for product in products:
                name = product.find_element(By.CSS_SELECTOR, "td.text-left a").text
                if product_name.lower() in name.lower():
                    logger.info(f"Товар {product_name} найден в корзине")
                    return True
            logger.warning(f"Товар {product_name} не найден в корзине")
            return False
        except TimeoutException:
            logger.error("Корзина пуста или не загрузилась")
            return False

# --- Тесты ---

@allure.feature("Главный поток")
def test_main_flow(driver):
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
    wait = WebDriverWait(driver, 30)
    try:
        no_products = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#content p")))
        if "There are no products to list in this category." in no_products.text:
            logger.info("Страница категории PC пуста - проверка пройдена")
            allure.attach(driver.get_screenshot_as_png(), name="PCEmpty", attachment_type=allure.attachment_type.PNG)
        else:
            logger.warning("Страница категории PC содержит товары")
    except TimeoutException:
        logger.error("Сообщение о пустой категории не найдено")
        allure.attach(driver.get_screenshot_as_png(), name="PCCheckFail", attachment_type=allure.attachment_type.PNG)

    register_page.open()
    register_page.register("Иван", "Иванов", "ivanov@example.com", "1234567890", "Password123")

    main_page.open()
    main_page.search_product("MacBook")
    time.sleep(3)

@allure.feature("Вишлист")
def test_add_to_wishlist(driver):
    main_page = MainPage(driver)
    main_page.open()
    added = main_page.add_product_to_wishlist_by_name("MacBook")
    if added:
        allure.attach(driver.get_screenshot_as_png(), name="WishlistSuccess", attachment_type=allure.attachment_type.PNG)
    else:
        allure.attach(driver.get_screenshot_as_png(), name="WishlistFail", attachment_type=allure.attachment_type.PNG)

@allure.feature("Корзина")
@allure.story("Добавление камеры")
def test_add_camera_to_cart(driver):
    main_page = MainPage(driver)
    cart_page = CartPage(driver)
    main_page.open()
    main_page.go_to_category("Cameras")
    main_page.add_product_to_cart_by_name("Canon EOS 5D")
    time.sleep(2)
    cart_page.open()
    assert cart_page.is_product_in_cart("Canon EOS 5D")
    allure.attach(driver.get_screenshot_as_png(), name="CameraCart", attachment_type=allure.attachment_type.PNG)

@allure.feature("Корзина")
@allure.story("Добавление планшета")
def test_add_tablet_to_cart(driver):
    main_page = MainPage(driver)
    cart_page = CartPage(driver)
    main_page.open()
    main_page.go_to_category("Tablets")
    main_page.add_product_to_cart_by_name("Samsung Galaxy Tab")
    time.sleep(2)
    cart_page.open()
    assert cart_page.is_product_in_cart("Samsung Galaxy Tab")
    allure.attach(driver.get_screenshot_as_png(), name="TabletCart", attachment_type=allure.attachment_type.PNG)

@allure.feature("Корзина")
@allure.story("Добавление телефона HTC")
def test_add_htc_phone_to_cart(driver):
    main_page = MainPage(driver)
    cart_page = CartPage(driver)
    main_page.open()
    main_page.go_to_category("Phones & PDAs")
    main_page.add_product_to_cart_by_name("HTC Touch HD")
    time.sleep(2)
    cart_page.open()
    assert cart_page.is_product_in_cart("HTC Touch HD")
    allure.attach(driver.get_screenshot_as_png(), name="HTCCart", attachment_type=allure.attachment_type.PNG)

@allure.feature("Отзывы")
def test_write_review(driver):
    main_page = MainPage(driver)
    product_page = ProductPage(driver)
    main_page.open()
    main_page.search_product("MacBook")
    wait = WebDriverWait(driver, 30)
    first_product = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".product-layout .caption a")))
    first_product.click()
    product_page.add_review("Иван", "Отличный товар, рекомендую!", rating=5)
